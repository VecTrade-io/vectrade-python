"""Earnings resource — earnings calendar and historical results."""

from __future__ import annotations

from typing import TYPE_CHECKING

from vectrade._utils.encoding import encode_path_param
from vectrade.types.earnings import EarningsCalendarEntry, EarningsResult

if TYPE_CHECKING:
    import httpx


class Earnings:
    """Synchronous earnings resource."""

    def __init__(self, http: httpx.Client) -> None:
        self._http = http

    def history(self, symbol: str, *, limit: int = 8) -> list[EarningsResult]:
        """Get historical earnings results for a symbol.

        Args:
            symbol: Stock ticker symbol.
            limit: Maximum number of quarters to return.

        Returns:
            List of EarningsResult (most recent first).
        """
        response = self._http.get(
            f"/vq/earnings/{encode_path_param(symbol)}"
        )
        response.raise_for_status()
        data = response.json()
        history = data.get("history", [])[:limit]
        return [EarningsResult.model_validate(e) for e in history]

    def calendar(
        self, *, from_date: str | None = None, to_date: str | None = None
    ) -> list[EarningsCalendarEntry]:
        """Get upcoming earnings calendar.

        Args:
            from_date: Start date (YYYY-MM-DD). Defaults to today.
            to_date: End date (YYYY-MM-DD). Defaults to 7 days out.

        Returns:
            List of EarningsCalendarEntry.
        """
        params: dict[str, str] = {}
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        response = self._http.get("/vq/earnings/calendar", params=params)
        response.raise_for_status()
        return [EarningsCalendarEntry.model_validate(e) for e in response.json()["data"]]


class AsyncEarnings:
    """Asynchronous earnings resource."""

    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def history(self, symbol: str, *, limit: int = 8) -> list[EarningsResult]:
        """Get historical earnings results for a symbol."""
        response = await self._http.get(
            f"/vq/earnings/{encode_path_param(symbol)}"
        )
        response.raise_for_status()
        data = response.json()
        history = data.get("history", [])[:limit]
        return [EarningsResult.model_validate(e) for e in history]

    async def calendar(
        self, *, from_date: str | None = None, to_date: str | None = None
    ) -> list[EarningsCalendarEntry]:
        """Get upcoming earnings calendar."""
        params: dict[str, str] = {}
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        response = await self._http.get("/vq/earnings/calendar", params=params)
        response.raise_for_status()
        return [EarningsCalendarEntry.model_validate(e) for e in response.json()["data"]]
