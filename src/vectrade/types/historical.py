"""Historical price data response models."""

from __future__ import annotations

from pydantic import BaseModel


class HistoricalBar(BaseModel):
    """Single OHLCV bar."""

    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: int | None = None
    adj_close: float | None = None


class HistoricalResponse(BaseModel):
    """Historical price data."""

    model_config = {"populate_by_name": True}

    ticker: str
    normalized_ticker: str | None = None
    market: str | None = None
    history: list[HistoricalBar] = []
