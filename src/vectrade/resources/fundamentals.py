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
            f"/vq/fundamentals/{encode_path_param(symbol)}/statements", params={"period": period}
        )
        data = response.json()
        raw = data.get("income_statement", {})
        earnings = raw.get("earnings", []) if isinstance(raw, dict) else []
        return [IncomeStatement.model_validate(item) for item in earnings]

    def balance_sheet(self, symbol: str, *, period: str = "annual") -> list[BalanceSheet]:
        """Get balance sheets (annual or quarterly)."""
        response = self._http.get(
            f"/vq/fundamentals/{encode_path_param(symbol)}/statements", params={"period": period}
        )
        data = response.json()
        raw = data.get("balance_sheet", {})
        entries = raw.get("earnings", []) if isinstance(raw, dict) else []
        return [BalanceSheet.model_validate(item) for item in entries]

    def statements(self, symbol: str) -> dict:
        """Get all financial statements (income, balance sheet, cash flow) as raw dict.

        Args:
            symbol: Stock ticker symbol.

        Returns:
            Dict with keys: income_statement, balance_sheet, cashflow_statement.
        """
        response = self._http.get(f"/vq/fundamentals/{encode_path_param(symbol)}/statements")
        return response.json()


class AsyncFundamentals:
    """Asynchronous fundamentals resource."""

    def __init__(self, http: AsyncHTTP) -> None:
        self._http = http

    async def get(self, symbol: str) -> FundamentalResponse:
        response = await self._http.get(f"/vq/fundamentals/{encode_path_param(symbol)}")
        return FundamentalResponse.model_validate(response.json())

    async def statements(self, symbol: str) -> dict:
        """Get all financial statements as raw dict."""
        response = await self._http.get(f"/vq/fundamentals/{encode_path_param(symbol)}/statements")
        return response.json()

    async def income_statement(
        self, symbol: str, *, period: str = "annual"
    ) -> list[IncomeStatement]:
        response = await self._http.get(
            f"/vq/fundamentals/{encode_path_param(symbol)}/statements", params={"period": period}
        )
        data = response.json()
        raw = data.get("income_statement", {})
        earnings = raw.get("earnings", []) if isinstance(raw, dict) else []
        return [IncomeStatement.model_validate(item) for item in earnings]

    async def balance_sheet(self, symbol: str, *, period: str = "annual") -> list[BalanceSheet]:
        response = await self._http.get(
            f"/vq/fundamentals/{encode_path_param(symbol)}/statements", params={"period": period}
        )
        data = response.json()
        raw = data.get("balance_sheet", {})
        entries = raw.get("earnings", []) if isinstance(raw, dict) else []
        return [BalanceSheet.model_validate(item) for item in entries]
