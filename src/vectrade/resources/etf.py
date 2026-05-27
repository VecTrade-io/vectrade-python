"""ETF resource — ETF data and holdings."""

from __future__ import annotations

from typing import TYPE_CHECKING

from vectrade._utils.encoding import encode_path_param
from vectrade.types.etf import ETFResponse

if TYPE_CHECKING:
    from vectrade._http_wrapper import AsyncHTTP, SyncHTTP


class ETF:
    """Synchronous ETF resource."""

    def __init__(self, http: SyncHTTP) -> None:
        self._http = http

    def get(self, symbol: str) -> ETFResponse:
        """Get ETF information and holdings.

        Args:
            symbol: ETF ticker symbol (e.g., "SPY").

        Returns:
            ETFResponse with fund info, holdings, and sector weights.
        """
        response = self._http.get(f"/vq/etf/{encode_path_param(symbol)}")
        return ETFResponse.model_validate(response.json())


class AsyncETF:
    """Asynchronous ETF resource."""

    def __init__(self, http: AsyncHTTP) -> None:
        self._http = http

    async def get(self, symbol: str) -> ETFResponse:
        """Get ETF information and holdings."""
        response = await self._http.get(f"/vq/etf/{encode_path_param(symbol)}")
        return ETFResponse.model_validate(response.json())
