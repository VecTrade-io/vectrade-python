"""SDK middleware/plugin architecture for request interception and telemetry."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Protocol

import httpx


@dataclass
class RequestContext:
    """Context passed through the middleware chain."""

    method: str
    url: str
    headers: dict[str, str]
    params: dict[str, Any] = field(default_factory=dict)
    body: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResponseContext:
    """Context returned from the middleware chain."""

    status_code: int
    headers: dict[str, str]
    body: bytes
    elapsed_ms: float
    request: RequestContext
    metadata: dict[str, Any] = field(default_factory=dict)


class Middleware(Protocol):
    """Protocol for sync middleware functions."""

    def __call__(
        self,
        request: RequestContext,
        call_next: Callable[[RequestContext], ResponseContext],
    ) -> ResponseContext: ...


class AsyncMiddleware(Protocol):
    """Protocol for async middleware functions."""

    async def __call__(
        self,
        request: RequestContext,
        call_next: Callable[[RequestContext], Awaitable[ResponseContext]],
    ) -> ResponseContext: ...


class MiddlewareStack:
    """Manages ordered middleware execution."""

    def __init__(self) -> None:
        self._middlewares: list[Middleware] = []

    def use(self, middleware: Middleware) -> None:
        """Add middleware to the stack. First added = outermost."""
        self._middlewares.append(middleware)

    def execute(
        self,
        request: RequestContext,
        handler: Callable[[RequestContext], ResponseContext],
    ) -> ResponseContext:
        """Execute the middleware chain with the given terminal handler."""
        chain = handler
        for mw in reversed(self._middlewares):
            chain = _wrap_middleware(mw, chain)
        return chain(request)


class AsyncMiddlewareStack:
    """Manages ordered async middleware execution."""

    def __init__(self) -> None:
        self._middlewares: list[AsyncMiddleware] = []

    def use(self, middleware: AsyncMiddleware) -> None:
        """Add async middleware to the stack."""
        self._middlewares.append(middleware)

    async def execute(
        self,
        request: RequestContext,
        handler: Callable[[RequestContext], Awaitable[ResponseContext]],
    ) -> ResponseContext:
        """Execute the async middleware chain."""
        chain = handler
        for mw in reversed(self._middlewares):
            chain = _wrap_async_middleware(mw, chain)
        return await chain(request)


def _wrap_middleware(
    mw: Middleware,
    next_handler: Callable[[RequestContext], ResponseContext],
) -> Callable[[RequestContext], ResponseContext]:
    def wrapped(req: RequestContext) -> ResponseContext:
        return mw(req, next_handler)
    return wrapped


def _wrap_async_middleware(
    mw: AsyncMiddleware,
    next_handler: Callable[[RequestContext], Awaitable[ResponseContext]],
) -> Callable[[RequestContext], Awaitable[ResponseContext]]:
    async def wrapped(req: RequestContext) -> ResponseContext:
        return await mw(req, next_handler)
    return wrapped


# ── Built-in Middlewares ──────────────────────────────────────────────


class LoggingMiddleware:
    """Logs request/response details."""

    def __init__(self, logger: Any = None) -> None:
        self._logger = logger

    def __call__(
        self,
        request: RequestContext,
        call_next: Callable[[RequestContext], ResponseContext],
    ) -> ResponseContext:
        if self._logger:
            self._logger.debug(f"→ {request.method} {request.url}")
        response = call_next(request)
        if self._logger:
            self._logger.debug(
                f"← {response.status_code} ({response.elapsed_ms:.1f}ms)"
            )
        return response


class TimingMiddleware:
    """Records request timing in metadata."""

    def __call__(
        self,
        request: RequestContext,
        call_next: Callable[[RequestContext], ResponseContext],
    ) -> ResponseContext:
        start = time.perf_counter()
        response = call_next(request)
        elapsed = (time.perf_counter() - start) * 1000
        response.metadata["timing_ms"] = elapsed
        return response


class IdempotencyMiddleware:
    """Adds Idempotency-Key header for mutation requests."""

    def __init__(self, key_generator: Callable[[], str] | None = None) -> None:
        import uuid
        self._generate = key_generator or (lambda: str(uuid.uuid4()))

    def __call__(
        self,
        request: RequestContext,
        call_next: Callable[[RequestContext], ResponseContext],
    ) -> ResponseContext:
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            if "Idempotency-Key" not in request.headers:
                request.headers["Idempotency-Key"] = self._generate()
        return call_next(request)
