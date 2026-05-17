"""Insider resource — insider transactions and ownership."""

from __future__ import annotations

from typing import TYPE_CHECKING

from vectrade._utils.encoding import encode_path_param
from vectrade.types.insider import InsiderSummary, InsiderTransaction

if TYPE_CHECKING:
    from vectrade._http_wrapper import AsyncHTTP, SyncHTTP


class Insider:
    """Synchronous insider resource."""

    def __init__(self, http: SyncHTTP) -> None:
        self._http = http

    def transactions(self, symbol: str, *, limit: int = 20) -> list[InsiderTransaction]:
        """Get recent insider transactions for a symbol."""
        response = self._http.get(f"/vq/insider/{encode_path_param(symbol)}")
        data = response.json()
        trades = data.get("trades", [])[:limit]
        return [InsiderTransaction.model_validate(t) for t in trades]

    def summary(self, symbol: str) -> InsiderSummary:
        """Get insider trading summary for a symbol."""
        response = self._http.get(f"/vq/insider/{encode_path_param(symbol)}")
        return InsiderSummary.model_validate(response.json())


class AsyncInsider:
    """Asynchronous insider resource."""

    def __init__(self, http: AsyncHTTP) -> None:
        self._http = http

    async def transactions(self, symbol: str, *, limit: int = 20) -> list[InsiderTransaction]:
        """Get recent insider transactions for a symbol."""
        response = await self._http.get(f"/vq/insider/{encode_path_param(symbol)}")
        data = response.json()
        trades = data.get("trades", [])[:limit]
        return [InsiderTransaction.model_validate(t) for t in trades]

    async def summary(self, symbol: str) -> InsiderSummary:
        """Get insider trading summary for a symbol."""
        response = await self._http.get(f"/vq/insider/{encode_path_param(symbol)}")
        return InsiderSummary.model_validate(response.json())
