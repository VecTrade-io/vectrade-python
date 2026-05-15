"""Screener resource — stock screening with custom filters."""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

from vectrade._pagination import SyncPaginator, AsyncPaginator
from vectrade.types.screener import ScreenerResult

if TYPE_CHECKING:
    import httpx


class Screener:
    """Synchronous screener resource."""

    def __init__(self, http: httpx.Client) -> None:
        self._http = http

    def run(
        self,
        *,
        market_cap_min: float | None = None,
        market_cap_max: float | None = None,
        pe_max: float | None = None,
        pe_min: float | None = None,
        dividend_yield_min: float | None = None,
        sector: str | None = None,
        industry: str | None = None,
        country: str = "US",
        sort_by: str = "market_cap",
        sort_order: str = "desc",
        limit: int = 50,
    ) -> SyncPaginator[ScreenerResult]:
        """Run a stock screener with custom filters.

        Returns an auto-paginating iterator over results.
        """
        filters: dict[str, Any] = {"country": country, "sort_by": sort_by, "sort_order": sort_order, "limit": limit}
        if market_cap_min is not None:
            filters["market_cap_min"] = market_cap_min
        if market_cap_max is not None:
            filters["market_cap_max"] = market_cap_max
        if pe_max is not None:
            filters["pe_max"] = pe_max
        if pe_min is not None:
            filters["pe_min"] = pe_min
        if dividend_yield_min is not None:
            filters["dividend_yield_min"] = dividend_yield_min
        if sector:
            filters["sector"] = sector
        if industry:
            filters["industry"] = industry

        def fetch_page(cursor: str | None = None) -> dict:
            params = {**filters}
            if cursor:
                params["cursor"] = cursor
            response = self._http.get("/vq/screener", params=params)
            response.raise_for_status()
            return response.json()

        return SyncPaginator(fetch_page=fetch_page, model=ScreenerResult)


class AsyncScreener:
    """Asynchronous screener resource."""

    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    def run(
        self,
        *,
        market_cap_min: float | None = None,
        market_cap_max: float | None = None,
        pe_max: float | None = None,
        pe_min: float | None = None,
        dividend_yield_min: float | None = None,
        sector: str | None = None,
        industry: str | None = None,
        country: str = "US",
        sort_by: str = "market_cap",
        sort_order: str = "desc",
        limit: int = 50,
    ) -> AsyncPaginator[ScreenerResult]:
        """Run a stock screener with custom filters."""
        filters: dict[str, Any] = {"country": country, "sort_by": sort_by, "sort_order": sort_order, "limit": limit}
        if market_cap_min is not None:
            filters["market_cap_min"] = market_cap_min
        if market_cap_max is not None:
            filters["market_cap_max"] = market_cap_max
        if pe_max is not None:
            filters["pe_max"] = pe_max
        if pe_min is not None:
            filters["pe_min"] = pe_min
        if dividend_yield_min is not None:
            filters["dividend_yield_min"] = dividend_yield_min
        if sector:
            filters["sector"] = sector
        if industry:
            filters["industry"] = industry

        async def fetch_page(cursor: str | None = None) -> dict:
            params = {**filters}
            if cursor:
                params["cursor"] = cursor
            response = await self._http.get("/vq/screener", params=params)
            response.raise_for_status()
            return response.json()

        return AsyncPaginator(fetch_page=fetch_page, model=ScreenerResult)
