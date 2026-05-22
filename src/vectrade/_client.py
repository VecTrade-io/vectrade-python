"""VecTrade SDK client implementation with retry and observability."""

from __future__ import annotations

import time
from collections.abc import Sequence
from typing import Any

import httpx

from vectrade._exceptions import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    NotFoundError,
    PaymentRequiredError,
    QuotaExceededError,
    RateLimitError,
    ServerError,
    ServiceUnavailableError,
    ValidationError,
)
from vectrade._http_wrapper import AsyncHTTP, SyncHTTP
from vectrade._middleware import (
    AsyncMiddleware,
    AsyncMiddlewareStack,
    Middleware,
    MiddlewareStack,
)
from vectrade._utils.config import (
    resolve_api_key,
    resolve_base_url,
    resolve_max_retries,
    resolve_timeout,
)
from vectrade._utils.headers import (
    HEADER_ACCEPT,
    HEADER_API_KEY,
    HEADER_REQUEST_ID,
    HEADER_USER_AGENT,
    ResponseMetadata,
)
from vectrade._utils.retry import (
    calculate_retry_delay,
    get_retry_after_header,
    should_retry,
)
from vectrade._version import __version__

# Custom attribute name for retry count on httpx.Response objects
_RETRY_COUNT_ATTR = "_vectrade_retries"
from vectrade.resources.ai import AI, AsyncAI
from vectrade.resources.analyst import Analyst, AsyncAnalyst
from vectrade.resources.developer import AsyncDeveloper, Developer
from vectrade.resources.earnings import AsyncEarnings, Earnings
from vectrade.resources.fundamentals import AsyncFundamentals, Fundamentals
from vectrade.resources.insider import AsyncInsider, Insider
from vectrade.resources.news import AsyncNews, News
from vectrade.resources.options import AsyncOptions, Options
from vectrade.resources.quotes import AsyncQuotes, Quotes
from vectrade.resources.screener import AsyncScreener, Screener
from vectrade.resources.technicals import AsyncTechnicals, Technicals
from vectrade.resources.webhooks import AsyncWebhooks, Webhooks


class _BaseClient:
    """Shared configuration for sync and async clients."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        sandbox: bool = False,
        middleware: Sequence[Middleware | AsyncMiddleware] | None = None,
    ) -> None:
        self.api_key = resolve_api_key(api_key)
        if not self.api_key:
            raise ConfigurationError(
                "api_key is required. Set the VECTRADE_API_KEY environment variable "
                "or pass api_key= to the client constructor. "
                "Get your key at https://app.vectrade.io/keys"
            )

        self.base_url = resolve_base_url(base_url=base_url, sandbox=sandbox)
        self.timeout = resolve_timeout(timeout)
        self.max_retries = resolve_max_retries(max_retries)
        self._middleware_list = list(middleware or [])

    @property
    def _default_headers(self) -> dict[str, str]:
        return {
            HEADER_API_KEY: self.api_key,  # type: ignore[dict-item]
            HEADER_USER_AGENT: f"vectrade-python/{__version__}",
            HEADER_ACCEPT: "application/json",
        }

    def __repr__(self) -> str:
        masked = self._mask_api_key(self.api_key or "")
        return f"{self.__class__.__name__}(api_key='{masked}', base_url='{self.base_url}')"

    @staticmethod
    def _mask_api_key(key: str) -> str:
        """Mask API key for safe display in logs and repr."""
        if len(key) <= 10:
            return "***"
        return f"{key[:7]}...{key[-4:]}"

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        """Raise typed exceptions based on HTTP status code.

        Parses the VecTrade error format: { error_code, message, details, request_id, retry_after }
        Also supports RFC 9457 (detail/type) and nested { error: { message, type } } envelopes.
        """
        if response.is_success:
            return

        request_id = response.headers.get(HEADER_REQUEST_ID)
        status = response.status_code

        # Parse error body — support multiple formats for resilience
        message = response.text or f"HTTP {status}"
        error_code: str | None = None
        error_type: str | None = None
        docs_url: str | None = None
        details: dict[str, Any] | None = None
        body_retry_after: float | None = None

        try:
            body = response.json()
            # VecTrade core format: { error_code, message, details, retry_after }
            if isinstance(body.get("error_code"), str):
                error_code = body["error_code"]
                message = body.get("message", message)
                details = body.get("details")
                body_retry_after = body.get("retry_after")
                error_type = error_code  # Use error_code as error_type
            # RFC 9457: { detail, type, title, status }
            elif isinstance(body.get("detail"), str):
                message = body["detail"]
                error_type = body.get("type")
                docs_url = body.get("docs_url")
            # Nested envelope: { error: { message, type, docs_url } }
            elif isinstance(body.get("error"), dict):
                err = body["error"]
                message = err.get("message", message)
                error_type = err.get("type")
                docs_url = err.get("docs_url")
        except Exception:
            pass  # Non-JSON body — use response.text

        common_kwargs = {
            "status_code": status,
            "request_id": request_id,
            "error_code": error_code,
            "error_type": error_type,
            "details": details,
            "docs_url": docs_url,
        }

        # Resolve retry_after from header OR body
        retry_after = get_retry_after_header(response) or body_retry_after

        # Quota headers for quota-related errors
        quota_remaining_hdr = response.headers.get("X-VQ-Quota-Remaining")
        quota_limit_hdr = response.headers.get("X-VQ-Quota-Limit")

        if status == 401:
            raise AuthenticationError(message, **common_kwargs)
        elif status == 402:
            raise PaymentRequiredError(message, **common_kwargs)
        elif status == 403:
            # 403 can be auth OR quota exceeded (BLOCK overage policy).
            # Finance uses AUTH_002 for both — detect quota by message content.
            _msg_lower = message.lower()
            if "quota" in _msg_lower or error_type == "quota_exceeded":
                raise QuotaExceededError(
                    message,
                    quota_limit=int(quota_limit_hdr) if quota_limit_hdr else None,
                    quota_remaining=int(quota_remaining_hdr) if quota_remaining_hdr else None,
                    overage_policy="BLOCK",
                    **common_kwargs,
                )
            raise AuthenticationError(message, **common_kwargs)
        elif status == 404:
            raise NotFoundError(message, **common_kwargs)
        elif status == 422:
            raise ValidationError(message, **common_kwargs)
        elif status == 429:
            limit_header = response.headers.get("X-VQ-RateLimit-Limit")
            limit = int(limit_header) if limit_header else None

            # Distinguish rate limit from quota exceeded
            _msg_lower = message.lower()
            if "quota" in _msg_lower or error_type == "quota_exceeded":
                raise QuotaExceededError(
                    message,
                    quota_limit=int(quota_limit_hdr) if quota_limit_hdr else None,
                    quota_remaining=0,
                    overage_policy="THROTTLE",
                    **common_kwargs,
                )
            raise RateLimitError(
                message,
                retry_after=retry_after,
                limit=limit,
                remaining=0,
                **common_kwargs,
            )
        elif status in (502, 503):
            raise ServiceUnavailableError(message, **common_kwargs)
        elif status >= 500:
            raise ServerError(message, **common_kwargs)
        else:
            raise APIError(message, **common_kwargs)


class VecTrade(_BaseClient):
    """Synchronous VecTrade API client.

    Usage:
        client = VecTrade()  # reads VECTRADE_API_KEY from env
        quote = client.quotes.get("AAPL")
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._http = httpx.Client(
            base_url=self.base_url,
            headers=self._default_headers,
            timeout=self.timeout,
        )
        self._last_response_metadata: ResponseMetadata | None = None

        # Middleware stack
        self._middleware_stack = MiddlewareStack()
        for mw in self._middleware_list:
            self._middleware_stack.use(mw)  # type: ignore[arg-type]

        # Resource namespaces — routed through retry + error mapping pipeline
        _managed = SyncHTTP(self.request, self._http)
        self.quotes = Quotes(_managed)
        self.fundamentals = Fundamentals(_managed)
        self.technicals = Technicals(_managed)
        self.news = News(_managed)
        self.screener = Screener(_managed)
        self.ai = AI(_managed)
        self.webhooks = Webhooks(_managed)
        self.options = Options(_managed)
        self.analyst = Analyst(_managed)
        self.earnings = Earnings(_managed)
        self.insider = Insider(_managed)
        self.developer = Developer(_managed)

    def request(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        """Make a request with automatic retry on transient failures."""
        extra_headers = dict(headers or {})
        if idempotency_key:
            extra_headers["Idempotency-Key"] = idempotency_key

        # Run through middleware if any are configured
        if self._middleware_stack._middlewares:
            from vectrade._middleware import RequestContext, ResponseContext

            req_ctx = RequestContext(
                method=method,
                url=f"{self.base_url}{path}",
                headers=dict(extra_headers),
                params=dict(params or {}),
                body=json,
            )
            _captured_response: httpx.Response | None = None

            def terminal_handler(ctx: RequestContext) -> ResponseContext:
                nonlocal _captured_response
                resp = self._execute_with_retry(
                    ctx.method,
                    path,
                    json=ctx.body,
                    params=ctx.params or None,
                    headers=ctx.headers,
                    timeout=timeout,
                )
                _captured_response = resp
                return ResponseContext(
                    status_code=resp.status_code,
                    headers=dict(resp.headers),
                    body=resp.content,
                    elapsed_ms=resp.elapsed.total_seconds() * 1000,
                    request=ctx,
                )

            self._middleware_stack.execute(req_ctx, terminal_handler)
            assert _captured_response is not None
            return _captured_response

        return self._execute_with_retry(
            method,
            path,
            json=json,
            params=params,
            headers=extra_headers,
            timeout=timeout,
        )

    def _execute_with_retry(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        """Execute HTTP request with retry logic."""
        last_exc: Exception | None = None
        effective_timeout = timeout if timeout is not None else self.timeout

        for attempt in range(self.max_retries + 1):
            try:
                response = self._http.request(
                    method,
                    path,
                    json=json,
                    params=params,
                    headers=headers or {},
                    timeout=effective_timeout,
                )
            except httpx.TransportError as exc:
                last_exc = exc
                if attempt < self.max_retries:
                    delay = calculate_retry_delay(attempt)
                    time.sleep(delay)
                    continue
                raise

            if response.is_success or not should_retry(response.status_code):
                self._raise_for_status(response)
                # Attach retry count for transparency (§12.4)
                setattr(response, _RETRY_COUNT_ATTR, attempt)
                # Populate response metadata
                self._last_response_metadata = ResponseMetadata.from_headers(dict(response.headers))
                return response

            # Retryable error
            last_exc = None
            if attempt < self.max_retries:
                retry_after = get_retry_after_header(response)
                delay = calculate_retry_delay(attempt, retry_after=retry_after)
                time.sleep(delay)
            else:
                self._raise_for_status(response)

        # Should not reach here, but satisfy type checker
        raise last_exc or RuntimeError("Unexpected retry exhaustion")  # pragma: no cover

    @property
    def last_response_metadata(self) -> ResponseMetadata | None:
        """Metadata from the most recent API response (for debugging)."""
        return self._last_response_metadata

    def close(self) -> None:
        """Close the HTTP client connection pool."""
        self._http.close()

    def health(self, *, timeout: float = 5.0) -> dict[str, Any]:
        """Check API health status.

        Returns:
            Dict with at least a 'status' key ('ok' or 'degraded').

        Raises:
            ServerError: If the health endpoint returns 5xx.
            httpx.TransportError: If the service is unreachable.
        """
        # Health endpoint is at the server root, not under the versioned path
        base = self._http.base_url
        authority = f"{base.host}:{base.port}" if base.port else base.host
        health_url = f"{base.scheme}://{authority}/health"
        response = self._http.get(health_url, timeout=timeout)
        self._raise_for_status(response)
        return response.json()  # type: ignore[no-any-return]

    def __enter__(self) -> VecTrade:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


class AsyncVecTrade(_BaseClient):
    """Asynchronous VecTrade API client.

    Usage:
        async with AsyncVecTrade() as client:
            quote = await client.quotes.get("AAPL")
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._http = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self._default_headers,
            timeout=self.timeout,
        )
        self._last_response_metadata: ResponseMetadata | None = None

        # Middleware stack
        self._middleware_stack = AsyncMiddlewareStack()
        for mw in self._middleware_list:
            self._middleware_stack.use(mw)  # type: ignore[arg-type]

        # Resource namespaces — routed through retry + error mapping pipeline
        _managed = AsyncHTTP(self.request, self._http)
        self.quotes = AsyncQuotes(_managed)
        self.fundamentals = AsyncFundamentals(_managed)
        self.technicals = AsyncTechnicals(_managed)
        self.news = AsyncNews(_managed)
        self.screener = AsyncScreener(_managed)
        self.ai = AsyncAI(_managed)
        self.webhooks = AsyncWebhooks(_managed)
        self.options = AsyncOptions(_managed)
        self.analyst = AsyncAnalyst(_managed)
        self.earnings = AsyncEarnings(_managed)
        self.insider = AsyncInsider(_managed)
        self.developer = AsyncDeveloper(_managed)

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        idempotency_key: str | None = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        """Make an async request with automatic retry on transient failures."""
        extra_headers = dict(headers or {})
        if idempotency_key:
            extra_headers["Idempotency-Key"] = idempotency_key

        # Run through middleware if any are configured
        if self._middleware_stack._middlewares:
            from vectrade._middleware import RequestContext, ResponseContext

            req_ctx = RequestContext(
                method=method,
                url=f"{self.base_url}{path}",
                headers=dict(extra_headers),
                params=dict(params or {}),
                body=json,
            )
            _captured_response: httpx.Response | None = None

            async def terminal_handler(ctx: RequestContext) -> ResponseContext:
                nonlocal _captured_response
                resp = await self._execute_with_retry(
                    ctx.method,
                    path,
                    json=ctx.body,
                    params=ctx.params or None,
                    headers=ctx.headers,
                    timeout=timeout,
                )
                _captured_response = resp
                return ResponseContext(
                    status_code=resp.status_code,
                    headers=dict(resp.headers),
                    body=resp.content,
                    elapsed_ms=resp.elapsed.total_seconds() * 1000,
                    request=ctx,
                )

            await self._middleware_stack.execute(req_ctx, terminal_handler)
            assert _captured_response is not None
            return _captured_response

        return await self._execute_with_retry(
            method,
            path,
            json=json,
            params=params,
            headers=extra_headers,
            timeout=timeout,
        )

    async def _execute_with_retry(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        """Execute async HTTP request with retry logic."""
        import asyncio

        last_exc: Exception | None = None
        effective_timeout = timeout if timeout is not None else self.timeout

        for attempt in range(self.max_retries + 1):
            try:
                response = await self._http.request(
                    method,
                    path,
                    json=json,
                    params=params,
                    headers=headers or {},
                    timeout=effective_timeout,
                )
            except httpx.TransportError as exc:
                last_exc = exc
                if attempt < self.max_retries:
                    delay = calculate_retry_delay(attempt)
                    await asyncio.sleep(delay)
                    continue
                raise

            if response.is_success or not should_retry(response.status_code):
                self._raise_for_status(response)
                # Attach retry count for transparency (§12.4)
                setattr(response, _RETRY_COUNT_ATTR, attempt)
                # Populate response metadata
                self._last_response_metadata = ResponseMetadata.from_headers(dict(response.headers))
                return response

            # Retryable error
            last_exc = None
            if attempt < self.max_retries:
                retry_after = get_retry_after_header(response)
                delay = calculate_retry_delay(attempt, retry_after=retry_after)
                await asyncio.sleep(delay)
            else:
                self._raise_for_status(response)

        # Should not reach here, but satisfy type checker
        raise last_exc or RuntimeError("Unexpected retry exhaustion")  # pragma: no cover

    @property
    def last_response_metadata(self) -> ResponseMetadata | None:
        """Metadata from the most recent API response (for debugging)."""
        return self._last_response_metadata

    async def close(self) -> None:
        """Close the HTTP client connection pool."""
        await self._http.aclose()

    async def health(self, *, timeout: float = 5.0) -> dict[str, Any]:
        """Check API health status.

        Returns:
            Dict with at least a 'status' key ('ok' or 'degraded').

        Raises:
            ServerError: If the health endpoint returns 5xx.
            httpx.TransportError: If the service is unreachable.
        """
        # Health endpoint is at the server root, not under the versioned path
        base = self._http.base_url
        authority = f"{base.host}:{base.port}" if base.port else base.host
        health_url = f"{base.scheme}://{authority}/health"
        response = await self._http.get(health_url, timeout=timeout)
        self._raise_for_status(response)
        return response.json()  # type: ignore[no-any-return]

    async def __aenter__(self) -> AsyncVecTrade:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
