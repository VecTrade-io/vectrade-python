"""Technical analysis response models."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class CandleData(BaseModel):
    """OHLCV candle data."""

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


class IndicatorValue(BaseModel):
    """A computed indicator value at a specific timestamp."""

    timestamp: datetime
    value: float


class TechnicalResponse(BaseModel):
    """Technical analysis response with candles and indicators."""

    symbol: str
    interval: str
    candles: list[CandleData]
    indicators: dict[str, list[IndicatorValue]] = {}
