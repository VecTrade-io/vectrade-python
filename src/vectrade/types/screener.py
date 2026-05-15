"""Screener response models."""

from __future__ import annotations

from pydantic import BaseModel


class ScreenerResult(BaseModel):
    """A single screener result."""

    symbol: str
    company_name: str
    price: float
    change_pct: float
    market_cap: float | None = None
    pe_ratio: float | None = None
    dividend_yield: float | None = None
    sector: str | None = None
    industry: str | None = None
    volume: int | None = None
    rsi_14: float | None = None
