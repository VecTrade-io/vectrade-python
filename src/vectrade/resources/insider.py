"""Insider resource — insider transactions and ownership."""

from __future__ import annotations

from typing import TYPE_CHECKING

from vectrade._utils.encoding import encode_path_param
from vectrade.types.insider import InsiderTransaction, InsiderSummary

if TYPE_CHECKING:
    import httpx


class Insider:
    """Synchronous insider resource."""

    def __init__(self, http: httpx.Client) -> None:
        self._http = http

    def transactions(self, symbol: str, *, limit: int = 20) -> list[InsiderTransaction]:
        """Get recent insider transactions for a symbol.

        Args:
            symbol: Stock ticker symbol.
            limit: Maximum number of transactions to return.

        Returns:
            List of InsiderTransaction (most recent first).
        """
        response = self._http.get(
            f"/vq/insider/{encode_path_param(symbol)}/transactions", params={"limit": str(limit)}
        )
        response.raise_for_status()
        return [InsiderTransaction.model_validate(t) for t in response.json()["data"]]

    def summary(self, symbol: str) -> InsiderSummary:
        """Get insider trading summary for a symbol.

        Args:
            symbol: Stock ticker symbol.

        Returns:
            InsiderSummary with net buy/sell over recent periods.
        """
        response = self._http.get(f"/vq/insider/{encode_path_param(symbol)}/summary")
        response.raise_for_status()
        return InsiderSummary.model_validate(response.json())


class AsyncInsider:
    """Asynchronous insider resource."""

    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def transactions(self, symbol: str, *, limit: int = 20) -> list[InsiderTransaction]:
        """Get recent insider transactions for a symbol."""
        response = await self._http.get(
            f"/vq/insider/{encode_path_param(symbol)}/transactions", params={"limit": str(limit)}
        )
        response.raise_for_status()
        return [InsiderTransaction.model_validate(t) for t in response.json()["data"]]

    async def summary(self, symbol: str) -> InsiderSummary:
        """Get insider trading summary for a symbol."""
        response = await self._http.get(f"/vq/insider/{encode_path_param(symbol)}/summary")
        response.raise_for_status()
        return InsiderSummary.model_validate(response.json())
