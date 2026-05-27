"""Historical resource — historical OHLCV price data."""

from __future__ import annotations

from typing import TYPE_CHECKING

from vectrade._utils.encoding import encode_path_param
from vectrade.types.historical import HistoricalResponse

if TYPE_CHECKING:
    from vectrade._http_wrapper import AsyncHTTP, SyncHTTP


class Historical:
    """Synchronous historical prices resource."""

    def __init__(self, http: SyncHTTP) -> None:
        self._http = http

    def get(self, symbol: str, *, period: str = "5d") -> HistoricalResponse:
        """Get historical OHLCV price data for a symbol.

        Args:
            symbol: Stock ticker symbol (e.g., "AAPL").
            period: Time period — "5d", "1mo", "3mo", "6mo", "1y", "5y".

        Returns:
            HistoricalResponse with OHLCV bars.
        """
        response = self._http.get(
            f"/vq/quotes/{encode_path_param(symbol)}/history",
            params={"period": period},
        )
        return HistoricalResponse.model_validate(response.json())


class AsyncHistorical:
    """Asynchronous historical prices resource."""

    def __init__(self, http: AsyncHTTP) -> None:
        self._http = http

    async def get(self, symbol: str, *, period: str = "5d") -> HistoricalResponse:
        """Get historical OHLCV price data for a symbol."""
        response = await self._http.get(
            f"/vq/quotes/{encode_path_param(symbol)}/history",
            params={"period": period},
        )
        return HistoricalResponse.model_validate(response.json())
