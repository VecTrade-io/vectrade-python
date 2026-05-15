"""Analyst response types."""

from __future__ import annotations

from pydantic import BaseModel


class AnalystConsensus(BaseModel):
    """Consensus analyst rating."""

    symbol: str
    consensus: str  # "Strong Buy", "Buy", "Hold", "Sell", "Strong Sell"
    target_high: float
    target_low: float
    target_mean: float
    target_median: float
    total_analysts: int
    buy: int
    hold: int
    sell: int


class PriceTarget(BaseModel):
    """Individual analyst price target."""

    analyst_name: str
    firm: str
    target: float
    rating: str
    published_at: str


class AnalystRating(BaseModel):
    """Analyst rating change event."""

    analyst_name: str
    firm: str
    action: str  # "initiated", "upgraded", "downgraded", "reiterated"
    from_rating: str | None = None
    to_rating: str
    target: float | None = None
    published_at: str
