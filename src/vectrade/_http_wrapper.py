"""Internal HTTP wrappers routing resource requests through the client pipeline.

Resources use these instead of raw httpx clients, ensuring all requests benefit from:
- Automatic retry with exponential backoff on 429/5xx
- Typed exception mapping (VecTradeError hierarchy)
- Middleware execution
- Response metadata tracking
"""

from __future__ import annotations

from typing import Any

import httpx


def _unwrap_success_envelope(response: httpx.Response) -> httpx.Response:
    if response.status_code == 204 or not response.content:
        return response
    try:
        body = response.json()
    except ValueError:
        return response
    if (
        not isinstance(body, dict)
        or body.get("status") not in {"ok", "degraded"}
        or "data" not in body
    ):
        return response

    metadata = {name: value for name, value in body.items() if name not in {"status", "data"}}
    payload = {"data": body["data"], **metadata} if metadata else body["data"]

    headers = {
        name: value
        for name, value in response.headers.items()
        if name.lower() not in {"content-length", "content-encoding"}
    }
    return httpx.Response(
        status_code=response.status_code,
        headers=headers,
        json=payload,
        request=response.request,
    )


class SyncHTTP:
    """Routes sync HTTP calls through the client's request pipeline."""

    __slots__ = ("_raw", "_request")

    def __init__(self, request_fn: Any, raw_client: httpx.Client) -> None:
        self._request = request_fn
        self._raw = raw_client

    def get(self, url: str, *, params: Any = None, timeout: float | None = None) -> httpx.Response:
        """Send a GET request with retry and error mapping."""
        response = self._request("GET", url, params=params, timeout=timeout)
        return _unwrap_success_envelope(response)

    def post(self, url: str, *, json: Any = None, params: Any = None) -> httpx.Response:
        """Send a POST request with retry and error mapping."""
        response = self._request("POST", url, json=json, params=params)
        return _unwrap_success_envelope(response)

    def delete(self, url: str) -> httpx.Response:
        """Send a DELETE request with retry and error mapping."""
        response = self._request("DELETE", url)
        return _unwrap_success_envelope(response)

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
        response = await self._request("GET", url, params=params, timeout=timeout)
        return _unwrap_success_envelope(response)

    async def post(self, url: str, *, json: Any = None, params: Any = None) -> httpx.Response:
        """Send a POST request with retry and error mapping."""
        response = await self._request("POST", url, json=json, params=params)
        return _unwrap_success_envelope(response)

    async def delete(self, url: str) -> httpx.Response:
        """Send a DELETE request with retry and error mapping."""
        response = await self._request("DELETE", url)
        return _unwrap_success_envelope(response)

    def stream(self, method: str, url: str, **kwargs: Any) -> Any:
        """Delegate streaming to the raw httpx client (no retry for streams)."""
        return self._raw.stream(method, url, **kwargs)
