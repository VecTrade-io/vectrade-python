"""Earnings response types."""

from __future__ import annotations

from pydantic import BaseModel, Field


class EarningsResult(BaseModel):
    """Historical earnings result for a quarter."""

    model_config = {"populate_by_name": True}

    date: str
    eps_actual: float | None = None
    eps_estimate: float | None = None
    revenue_actual: float | None = None
    revenue_estimate: float | None = None
    eps_surprise: float | None = None
    eps_surprise_pct: float | None = None
    revenue_surprise_pct: float | None = None


class EarningsCalendarEntry(BaseModel):
    """Upcoming earnings calendar entry."""

    model_config = {"populate_by_name": True}

    symbol: str | None = None
    company_name: str | None = Field(None, alias="companyName")
    date: str
    time: str | None = None
    eps_estimate: float | None = Field(None, alias="epsEstimate")
    revenue_estimate: float | None = Field(None, alias="revenueEstimate")
    fiscal_quarter: str | None = Field(None, alias="fiscalQuarter")
