"""Screener response models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ScreenerResult(BaseModel):
    """A single screener result."""

    model_config = {"populate_by_name": True}

    symbol: str
    company_name: str = Field(validation_alias="companyName")
    price: float
    change_pct: float = Field(validation_alias="changePct")
    market_cap: float | None = Field(default=None, validation_alias="marketCap")
    pe_ratio: float | None = Field(default=None, validation_alias="peRatio")
    dividend_yield: float | None = Field(default=None, validation_alias="dividendYield")
    beta: float | None = None
    revenue_growth_yoy: float | None = Field(default=None, validation_alias="revenueGrowthYoy")
    sector: str | None = None
    volume: int | None = None
    rsi_14: float | None = Field(default=None, validation_alias="rsi14")
