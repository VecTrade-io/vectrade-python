"""Quote response models."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class QuoteResponse(BaseModel):
    """Real-time stock quote data."""

    symbol: str
    price: float
    change: float
    change_pct: float
    volume: int
    day_high: float
    day_low: float
    day_open: float
    previous_close: float
    market_cap: float | None = None
    timestamp: datetime
