"""News resource — financial news and sentiment."""

from __future__ import annotations

from typing import TYPE_CHECKING

from vectrade._utils.encoding import encode_path_param
from vectrade.types.news import NewsArticle

if TYPE_CHECKING:
    import httpx


class News:
    """Synchronous news resource."""

    def __init__(self, http: httpx.Client) -> None:
        self._http = http

    def list(
        self,
        symbol: str,
        *,
        limit: int = 20,
    ) -> list[NewsArticle]:
        """Get latest financial news for a symbol.

        Args:
            symbol: Ticker symbol (e.g., "AAPL").
            limit: Number of articles to return (max 100).
        """
        response = self._http.get(f"/vq/news/{encode_path_param(symbol)}")
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])[:limit]
        return [NewsArticle.model_validate(item) for item in articles]

    def get(self, symbol: str) -> list[NewsArticle]:
        """Get news articles for a symbol."""
        return self.list(symbol)


class AsyncNews:
    """Asynchronous news resource."""

    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def list(
        self,
        symbol: str,
        *,
        limit: int = 20,
    ) -> list[NewsArticle]:
        """Get latest financial news for a symbol."""
        response = await self._http.get(f"/vq/news/{encode_path_param(symbol)}")
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])[:limit]
        return [NewsArticle.model_validate(item) for item in articles]

    async def get(self, symbol: str) -> list[NewsArticle]:
        """Get news articles for a symbol."""
        return await self.list(symbol)
