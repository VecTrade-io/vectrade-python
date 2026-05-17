"""Technicals resource — technical indicators and chart data."""

from __future__ import annotations

from typing import TYPE_CHECKING

from vectrade._utils.encoding import encode_path_param
from vectrade.types.technical import TechnicalResponse

if TYPE_CHECKING:
    import httpx


class Technicals:
    """Synchronous technicals resource."""

    def __init__(self, http: httpx.Client) -> None:
        self._http = http

    def get(
        self,
        symbol: str,
        *,
        indicators: list[str] | None = None,
        interval: str = "1d",
        period: int = 200,
    ) -> TechnicalResponse:
        """Get technical indicators for a symbol.

        Args:
            symbol: Ticker symbol.
            indicators: List of indicators (e.g., ["rsi", "macd", "sma_50"]).
            interval: Candle interval ("1m", "5m", "15m", "1h", "1d", "1w").
            period: Number of data points.
        """
        params: dict[str, str] = {"interval": interval, "period": str(period)}
        if indicators:
            params["indicators"] = ",".join(indicators)

        response = self._http.get(f"/vq/technical/{encode_path_param(symbol)}", params=params)
        response.raise_for_status()
        return TechnicalResponse.model_validate(response.json())


class AsyncTechnicals:
    """Asynchronous technicals resource."""

    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def get(
        self,
        symbol: str,
        *,
        indicators: list[str] | None = None,
        interval: str = "1d",
        period: int = 200,
    ) -> TechnicalResponse:
        params: dict[str, str] = {"interval": interval, "period": str(period)}
        if indicators:
            params["indicators"] = ",".join(indicators)

        response = await self._http.get(
            f"/vq/technical/{encode_path_param(symbol)}", params=params
        )
        response.raise_for_status()
        return TechnicalResponse.model_validate(response.json())
