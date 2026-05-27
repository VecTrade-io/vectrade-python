"""Sentiment resource — sentiment analysis and social data."""

from __future__ import annotations

from typing import TYPE_CHECKING

from vectrade._utils.encoding import encode_path_param
from vectrade.types.sentiment import SentimentResponse

if TYPE_CHECKING:
    from vectrade._http_wrapper import AsyncHTTP, SyncHTTP


class Sentiment:
    """Synchronous sentiment resource."""

    def __init__(self, http: SyncHTTP) -> None:
        self._http = http

    def get(self, symbol: str) -> SentimentResponse:
        """Get sentiment analysis for a symbol.

        Includes sentiment score, signal, news sentiment breakdown,
        and social media metrics.

        Args:
            symbol: Stock ticker symbol (e.g., "AAPL").

        Returns:
            SentimentResponse with sentiment data.
        """
        response = self._http.get(f"/vq/sentiment/{encode_path_param(symbol)}")
        return SentimentResponse.model_validate(response.json())


class AsyncSentiment:
    """Asynchronous sentiment resource."""

    def __init__(self, http: AsyncHTTP) -> None:
        self._http = http

    async def get(self, symbol: str) -> SentimentResponse:
        """Get sentiment analysis for a symbol."""
        response = await self._http.get(f"/vq/sentiment/{encode_path_param(symbol)}")
        return SentimentResponse.model_validate(response.json())
