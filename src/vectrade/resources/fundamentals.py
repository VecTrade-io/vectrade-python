"""Fundamentals resource — company financial data."""

from __future__ import annotations

from typing import TYPE_CHECKING

from vectrade._utils.encoding import encode_path_param
from vectrade.types.fundamental import BalanceSheet, FundamentalResponse, IncomeStatement

if TYPE_CHECKING:
    from vectrade._http_wrapper import AsyncHTTP, SyncHTTP


class Fundamentals:
    """Synchronous fundamentals resource."""

    def __init__(self, http: SyncHTTP) -> None:
        self._http = http

    def get(self, symbol: str) -> FundamentalResponse:
        """Get fundamental data for a symbol (PE, EPS, market cap, etc.)."""
        response = self._http.get(f"/vq/fundamentals/{encode_path_param(symbol)}")
        return FundamentalResponse.model_validate(response.json())

    def income_statement(self, symbol: str, *, period: str = "annual") -> list[IncomeStatement]:
        """Get income statements (annual or quarterly)."""
        response = self._http.get(
            f"/vq/fundamentals/{encode_path_param(symbol)}/income", params={"period": period}
        )
        return [IncomeStatement.model_validate(item) for item in response.json()["data"]]

    def balance_sheet(self, symbol: str, *, period: str = "annual") -> list[BalanceSheet]:
        """Get balance sheets (annual or quarterly)."""
        response = self._http.get(
            f"/vq/fundamentals/{encode_path_param(symbol)}/balance-sheet", params={"period": period}
        )
        return [BalanceSheet.model_validate(item) for item in response.json()["data"]]


class AsyncFundamentals:
    """Asynchronous fundamentals resource."""

    def __init__(self, http: AsyncHTTP) -> None:
        self._http = http

    async def get(self, symbol: str) -> FundamentalResponse:
        response = await self._http.get(f"/vq/fundamentals/{encode_path_param(symbol)}")
        return FundamentalResponse.model_validate(response.json())

    async def income_statement(
        self, symbol: str, *, period: str = "annual"
    ) -> list[IncomeStatement]:
        response = await self._http.get(
            f"/vq/fundamentals/{encode_path_param(symbol)}/income", params={"period": period}
        )
        return [IncomeStatement.model_validate(item) for item in response.json()["data"]]

    async def balance_sheet(self, symbol: str, *, period: str = "annual") -> list[BalanceSheet]:
        response = await self._http.get(
            f"/vq/fundamentals/{encode_path_param(symbol)}/balance-sheet", params={"period": period}
        )
        return [BalanceSheet.model_validate(item) for item in response.json()["data"]]
