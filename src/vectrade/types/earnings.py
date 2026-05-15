"""Earnings response types."""

from __future__ import annotations

from pydantic import BaseModel


class EarningsResult(BaseModel):
    """Historical earnings result for a quarter."""

    symbol: str
    date: str
    fiscal_quarter: str  # "Q1 2026"
    eps_actual: float
    eps_estimate: float
    eps_surprise: float
    eps_surprise_pct: float
    revenue_actual: float
    revenue_estimate: float
    revenue_surprise_pct: float


class EarningsCalendarEntry(BaseModel):
    """Upcoming earnings calendar entry."""

    symbol: str
    company_name: str
    date: str
    time: str  # "before_market", "after_market", "during_market"
    eps_estimate: float | None = None
    revenue_estimate: float | None = None
    fiscal_quarter: str
