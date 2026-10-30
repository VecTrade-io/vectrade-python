"""Screener resource — stock screening with custom filters."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from vectrade._pagination import AsyncPaginator, SyncPaginator
from vectrade.types.screener import ScreenerResult

if TYPE_CHECKING:
    from vectrade._http_wrapper import AsyncHTTP, SyncHTTP


class Screener:
    """Synchronous screener resource."""

    def __init__(self, http: SyncHTTP) -> None:
        self._http = http

    def run(
        self,
        *,
        market_cap_min: float | None = None,
        market_cap_max: float | None = None,
        pe_max: float | None = None,
        pe_min: float | None = None,
        dividend_yield_min: float | None = None,
        dividend_yield_max: float | None = None,
        change_min: float | None = None,
        change_max: float | None = None,
        beta_min: float | None = None,
        beta_max: float | None = None,
        revenue_growth_min: float | None = None,
        revenue_growth_max: float | None = None,
        rsi_min: float | None = None,
        rsi_max: float | None = None,
        volume_min: int | None = None,
        sector: str | None = None,
        sort_by: str = "market_cap",
        sort_order: str = "desc",
        limit: int = 20,
    ) -> SyncPaginator[ScreenerResult]:
        """Run a stock screener with custom filters.

        Returns an auto-paginating iterator over results.
        """
        if not 1 <= limit <= 50:
            raise ValueError("Screener limit must be between 1 and 50.")
        filters: dict[str, Any] = {
            "sort_by": sort_by,
            "sort_order": sort_order,
            "limit": limit,
        }
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
        if dividend_yield_max is not None:
            filters["dividend_yield_max"] = dividend_yield_max
        if change_min is not None:
            filters["change_min"] = change_min
        if change_max is not None:
            filters["change_max"] = change_max
        if beta_min is not None:
            filters["beta_min"] = beta_min
        if beta_max is not None:
            filters["beta_max"] = beta_max
        if revenue_growth_min is not None:
            filters["revenue_growth_min"] = revenue_growth_min
        if revenue_growth_max is not None:
            filters["revenue_growth_max"] = revenue_growth_max
        if rsi_min is not None:
            filters["rsi_min"] = rsi_min
        if rsi_max is not None:
            filters["rsi_max"] = rsi_max
        if volume_min is not None:
            filters["volume_min"] = volume_min
        if sector:
            filters["sector"] = sector

        def fetch_page(cursor: str | None = None) -> dict[str, Any]:
            params = {key: str(value) for key, value in filters.items()}
            if cursor:
                params["cursor"] = cursor
            response = self._http.get("/vq/screener", params=params)
            return response.json()  # type: ignore[no-any-return]

        return SyncPaginator(fetch_page=fetch_page, model=ScreenerResult)


class AsyncScreener:
    """Asynchronous screener resource."""

    def __init__(self, http: AsyncHTTP) -> None:
        self._http = http

    def run(
        self,
        *,
        market_cap_min: float | None = None,
        market_cap_max: float | None = None,
        pe_max: float | None = None,
        pe_min: float | None = None,
        dividend_yield_min: float | None = None,
        dividend_yield_max: float | None = None,
        change_min: float | None = None,
        change_max: float | None = None,
        beta_min: float | None = None,
        beta_max: float | None = None,
        revenue_growth_min: float | None = None,
        revenue_growth_max: float | None = None,
        rsi_min: float | None = None,
        rsi_max: float | None = None,
        volume_min: int | None = None,
        sector: str | None = None,
        sort_by: str = "market_cap",
        sort_order: str = "desc",
        limit: int = 20,
    ) -> AsyncPaginator[ScreenerResult]:
        """Run a stock screener with custom filters."""
        if not 1 <= limit <= 50:
            raise ValueError("Screener limit must be between 1 and 50.")
        filters: dict[str, Any] = {
            "sort_by": sort_by,
            "sort_order": sort_order,
            "limit": limit,
        }
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
        if dividend_yield_max is not None:
            filters["dividend_yield_max"] = dividend_yield_max
        if change_min is not None:
            filters["change_min"] = change_min
        if change_max is not None:
            filters["change_max"] = change_max
        if beta_min is not None:
            filters["beta_min"] = beta_min
        if beta_max is not None:
            filters["beta_max"] = beta_max
        if revenue_growth_min is not None:
            filters["revenue_growth_min"] = revenue_growth_min
        if revenue_growth_max is not None:
            filters["revenue_growth_max"] = revenue_growth_max
        if rsi_min is not None:
            filters["rsi_min"] = rsi_min
        if rsi_max is not None:
            filters["rsi_max"] = rsi_max
        if volume_min is not None:
            filters["volume_min"] = volume_min
        if sector:
            filters["sector"] = sector

        async def fetch_page(cursor: str | None = None) -> dict[str, Any]:
            params = {key: str(value) for key, value in filters.items()}
            if cursor:
                params["cursor"] = cursor
            response = await self._http.get("/vq/screener", params=params)
            return response.json()  # type: ignore[no-any-return]

        return AsyncPaginator(fetch_page=fetch_page, model=ScreenerResult)
