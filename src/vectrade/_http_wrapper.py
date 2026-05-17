"""Internal HTTP wrappers routing resource requests through the client pipeline.

Resources use these instead of raw httpx clients, ensuring all requests benefit from:
- Automatic retry with exponential backoff on 429/5xx
- Typed exception mapping (VecTradeError hierarchy)
- Middleware execution
- Response metadata tracking
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import httpx


class SyncHTTP:
    """Routes sync HTTP calls through the client's request pipeline."""

    __slots__ = ("_raw", "_request")

    def __init__(self, request_fn: Any, raw_client: httpx.Client) -> None:
        self._request = request_fn
        self._raw = raw_client

    def get(self, url: str, *, params: Any = None, timeout: float | None = None) -> httpx.Response:
        """Send a GET request with retry and error mapping."""
        return self._request("GET", url, params=params, timeout=timeout)  # type: ignore[no-any-return]

    def post(self, url: str, *, json: Any = None, params: Any = None) -> httpx.Response:
        """Send a POST request with retry and error mapping."""
        return self._request("POST", url, json=json, params=params)  # type: ignore[no-any-return]

    def delete(self, url: str) -> httpx.Response:
        """Send a DELETE request with retry and error mapping."""
        return self._request("DELETE", url)  # type: ignore[no-any-return]

    def stream(self, method: str, url: str, **kwargs: Any) -> Any:
        """Delegate streaming to the raw httpx client (no retry for streams)."""
        return self._raw.stream(method, url, **kwargs)


class AsyncHTTP:
    """Routes async HTTP calls through the client's request pipeline."""

    __slots__ = ("_raw", "_request")

    def __init__(self, request_fn: Any, raw_client: httpx.AsyncClient) -> None:
        self._request = request_fn
        self._raw = raw_client

    async def get(
        self, url: str, *, params: Any = None, timeout: float | None = None
    ) -> httpx.Response:
        """Send a GET request with retry and error mapping."""
        return await self._request("GET", url, params=params, timeout=timeout)  # type: ignore[no-any-return]

    async def post(self, url: str, *, json: Any = None, params: Any = None) -> httpx.Response:
        """Send a POST request with retry and error mapping."""
        return await self._request("POST", url, json=json, params=params)  # type: ignore[no-any-return]

    async def delete(self, url: str) -> httpx.Response:
        """Send a DELETE request with retry and error mapping."""
        return await self._request("DELETE", url)  # type: ignore[no-any-return]

    def stream(self, method: str, url: str, **kwargs: Any) -> Any:
        """Delegate streaming to the raw httpx client (no retry for streams)."""
        return self._raw.stream(method, url, **kwargs)
