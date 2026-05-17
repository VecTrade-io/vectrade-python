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

    symbol: str | None = None
    company_name: str | None = None
    date: str
    time: str | None = None
    eps_estimate: float | None = None
    revenue_estimate: float | None = None
    fiscal_quarter: str | None = None
