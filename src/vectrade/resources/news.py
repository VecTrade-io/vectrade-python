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
        *,
        symbols: list[str] | None = None,
        category: str | None = None,
        limit: int = 20,
    ) -> list[NewsArticle]:
        """Get latest financial news.

        Args:
            symbols: Filter by ticker symbols.
            category: Filter by category (e.g., "earnings", "macro", "crypto").
            limit: Number of articles to return (max 100).
        """
        params: dict[str, str] = {"limit": str(limit)}
        if symbols:
            params["symbols"] = ",".join(symbols)
        if category:
            params["category"] = category

        response = self._http.get("/vq/news", params=params)
        response.raise_for_status()
        return [NewsArticle.model_validate(item) for item in response.json()["data"]]

    def get(self, article_id: str) -> NewsArticle:
        """Get a single news article by ID."""
        response = self._http.get(f"/vq/news/{encode_path_param(article_id)}")
        response.raise_for_status()
        return NewsArticle.model_validate(response.json())


class AsyncNews:
    """Asynchronous news resource."""

    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def list(
        self,
        *,
        symbols: list[str] | None = None,
        category: str | None = None,
        limit: int = 20,
    ) -> list[NewsArticle]:
        params: dict[str, str] = {"limit": str(limit)}
        if symbols:
            params["symbols"] = ",".join(symbols)
        if category:
            params["category"] = category

        response = await self._http.get("/vq/news", params=params)
        response.raise_for_status()
        return [NewsArticle.model_validate(item) for item in response.json()["data"]]

    async def get(self, article_id: str) -> NewsArticle:
        response = await self._http.get(f"/vq/news/{encode_path_param(article_id)}")
        response.raise_for_status()
        return NewsArticle.model_validate(response.json())
