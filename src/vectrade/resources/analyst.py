"""Analyst resource — analyst ratings and price targets."""

from __future__ import annotations

from typing import TYPE_CHECKING

from vectrade._utils.encoding import encode_path_param
from vectrade.types.analyst import AnalystConsensus, PriceTarget, AnalystRating

if TYPE_CHECKING:
    import httpx


class Analyst:
    """Synchronous analyst resource."""

    def __init__(self, http: httpx.Client) -> None:
        self._http = http

    def consensus(self, symbol: str) -> AnalystConsensus:
        """Get analyst consensus rating for a symbol.

        Args:
            symbol: Stock ticker symbol.

        Returns:
            AnalystConsensus with rating breakdown and average target.
        """
        response = self._http.get(f"/vq/analyst/{encode_path_param(symbol)}/consensus")
        response.raise_for_status()
        return AnalystConsensus.model_validate(response.json())

    def price_targets(self, symbol: str) -> list[PriceTarget]:
        """Get individual analyst price targets.

        Args:
            symbol: Stock ticker symbol.

        Returns:
            List of PriceTarget from individual analysts.
        """
        response = self._http.get(f"/vq/analyst/{encode_path_param(symbol)}/price-targets")
        response.raise_for_status()
        return [PriceTarget.model_validate(t) for t in response.json()["data"]]

    def ratings(self, symbol: str, *, limit: int = 20) -> list[AnalystRating]:
        """Get recent analyst rating changes.

        Args:
            symbol: Stock ticker symbol.
            limit: Maximum number of ratings to return.

        Returns:
            List of AnalystRating entries.
        """
        response = self._http.get(
            f"/vq/analyst/{encode_path_param(symbol)}/ratings", params={"limit": str(limit)}
        )
        response.raise_for_status()
        return [AnalystRating.model_validate(r) for r in response.json()["data"]]


class AsyncAnalyst:
    """Asynchronous analyst resource."""

    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def consensus(self, symbol: str) -> AnalystConsensus:
        """Get analyst consensus rating for a symbol."""
        response = await self._http.get(f"/vq/analyst/{encode_path_param(symbol)}/consensus")
        response.raise_for_status()
        return AnalystConsensus.model_validate(response.json())

    async def price_targets(self, symbol: str) -> list[PriceTarget]:
        """Get individual analyst price targets."""
        response = await self._http.get(f"/vq/analyst/{encode_path_param(symbol)}/price-targets")
        response.raise_for_status()
        return [PriceTarget.model_validate(t) for t in response.json()["data"]]

    async def ratings(self, symbol: str, *, limit: int = 20) -> list[AnalystRating]:
        """Get recent analyst rating changes."""
        response = await self._http.get(
            f"/vq/analyst/{encode_path_param(symbol)}/ratings", params={"limit": str(limit)}
        )
        response.raise_for_status()
        return [AnalystRating.model_validate(r) for r in response.json()["data"]]
