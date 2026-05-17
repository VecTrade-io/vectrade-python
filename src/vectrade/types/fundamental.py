"""Fundamental response models."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class FundamentalResponse(BaseModel):
    """Company fundamental data."""

    model_config = {"populate_by_name": True}

    symbol: str = Field(validation_alias="ticker")
    company_name: str = Field(validation_alias="companyName")
    market: str | None = None
    market_cap: float | None = None
    price: float | None = None
    change: float | None = None
    change_pct: float | None = Field(default=None, validation_alias="change_percent")
    volume: int | None = None
    previous_close: float | None = Field(default=None, validation_alias="prevClose")
    day_high: float | None = Field(default=None, validation_alias="high")
    day_low: float | None = Field(default=None, validation_alias="low")
    day_open: float | None = Field(default=None, validation_alias="open")
    fifty_two_week_high: float | None = Field(default=None, validation_alias="max52")
    fifty_two_week_low: float | None = Field(default=None, validation_alias="min52")
    sma50: float | None = None
    sma200: float | None = None
    timestamp: datetime | None = None


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
