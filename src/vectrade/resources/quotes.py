"""Quotes resource — real-time and batch stock quotes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from vectrade._utils.encoding import encode_path_param
from vectrade.types.quote import QuoteResponse

if TYPE_CHECKING:
    from vectrade._http_wrapper import AsyncHTTP, SyncHTTP


class Quotes:
    """Synchronous quotes resource."""

    def __init__(self, http: SyncHTTP) -> None:
        self._http = http

    def get(self, symbol: str, *, fields: list[str] | None = None) -> QuoteResponse:
        """Get a real-time quote for a single symbol.

        Args:
            symbol: Stock ticker symbol (e.g., "AAPL").
            fields: Optional list of fields to return.

        Returns:
            QuoteResponse with current market data.
        """
        params: dict[str, str] = {}
        if fields:
            params["fields"] = ",".join(fields)

        response = self._http.get(f"/vq/quotes/{encode_path_param(symbol)}", params=params)
        return QuoteResponse.model_validate(response.json())

    def batch(self, symbols: list[str]) -> list[QuoteResponse]:
        """Get quotes for multiple symbols in a single request.

        Args:
            symbols: List of ticker symbols (max 20).

        Returns:
            List of QuoteResponse objects.
        """
        if not 1 <= len(symbols) <= 20:
            raise ValueError("Batch quote requests require between 1 and 20 symbols.")
        response = self._http.get("/vq/quotes/batch", params={"tickers": ",".join(symbols)})
        payload = response.json()
        data = payload.get("data", payload)
        items = data.values() if isinstance(data, dict) else data
        return [QuoteResponse.model_validate(q) for q in items]


class AsyncQuotes:
    """Asynchronous quotes resource."""

    def __init__(self, http: AsyncHTTP) -> None:
        self._http = http

    async def get(self, symbol: str, *, fields: list[str] | None = None) -> QuoteResponse:
        """Get a real-time quote for a single symbol."""
        params: dict[str, str] = {}
        if fields:
            params["fields"] = ",".join(fields)

        response = await self._http.get(f"/vq/quotes/{encode_path_param(symbol)}", params=params)
        return QuoteResponse.model_validate(response.json())

    async def batch(self, symbols: list[str]) -> list[QuoteResponse]:
        """Get quotes for multiple symbols in a single request."""
        if not 1 <= len(symbols) <= 20:
            raise ValueError("Batch quote requests require between 1 and 20 symbols.")
        response = await self._http.get("/vq/quotes/batch", params={"tickers": ",".join(symbols)})
        payload = response.json()
        data = payload.get("data", payload)
        items = data.values() if isinstance(data, dict) else data
        return [QuoteResponse.model_validate(q) for q in items]
