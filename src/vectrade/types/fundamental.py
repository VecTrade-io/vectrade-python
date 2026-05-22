"""Fundamental response models."""

from __future__ import annotations

from datetime import datetime

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
    """Income statement data (raw from collector)."""

    model_config = {"extra": "allow", "populate_by_name": True}

    period: str = ""  # fiscal period end date e.g. "2024-09-30"
    total_revenue: float | None = Field(default=None, validation_alias="Total Revenue")
    gross_profit: float | None = Field(default=None, validation_alias="Gross Profit")
    operating_income: float | None = Field(default=None, validation_alias="Operating Income")
    net_income: float | None = Field(default=None, validation_alias="Net Income")
    basic_eps: float | None = Field(default=None, validation_alias="Basic EPS")
    diluted_eps: float | None = Field(default=None, validation_alias="Diluted EPS")
    ebitda: float | None = Field(default=None, validation_alias="EBITDA")
    cost_of_revenue: float | None = Field(default=None, validation_alias="Cost Of Revenue")
    research_and_development: float | None = Field(
        default=None, validation_alias="Research And Development"
    )


class BalanceSheet(BaseModel):
    """Balance sheet data (raw from collector)."""

    model_config = {"extra": "allow", "populate_by_name": True}

    period: str = ""  # fiscal period end date
    total_assets: float | None = Field(default=None, validation_alias="Total Assets")
    total_liabilities: float | None = Field(
        default=None, validation_alias="Total Liabilities Net Minority Interest"
    )
    total_equity: float | None = Field(default=None, validation_alias="Stockholders Equity")
    cash_and_equivalents: float | None = Field(
        default=None, validation_alias="Cash And Cash Equivalents"
    )
    total_debt: float | None = Field(default=None, validation_alias="Total Debt")
