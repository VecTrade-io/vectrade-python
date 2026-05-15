"""Fundamental response models."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class FundamentalResponse(BaseModel):
    """Company fundamental data."""

    symbol: str
    company_name: str
    sector: str | None = None
    industry: str | None = None
    market_cap: float | None = None
    pe_ratio: float | None = None
    forward_pe: float | None = None
    eps: float | None = None
    dividend_yield: float | None = None
    beta: float | None = None
    fifty_two_week_high: float | None = None
    fifty_two_week_low: float | None = None
    avg_volume: int | None = None
    shares_outstanding: int | None = None


class IncomeStatement(BaseModel):
    """Income statement data."""

    fiscal_date: date
    period: str  # "annual" | "quarterly"
    revenue: float | None = None
    gross_profit: float | None = None
    operating_income: float | None = None
    net_income: float | None = None
    eps_basic: float | None = None
    eps_diluted: float | None = None


class BalanceSheet(BaseModel):
    """Balance sheet data."""

    fiscal_date: date
    period: str
    total_assets: float | None = None
    total_liabilities: float | None = None
    total_equity: float | None = None
    cash_and_equivalents: float | None = None
    total_debt: float | None = None
