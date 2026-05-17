"""Quote response models."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class QuoteResponse(BaseModel):
    """Real-time stock quote data."""

    model_config = {"populate_by_name": True}

    symbol: str = Field(validation_alias="ticker")
    price: float
    change: float
    change_pct: float = Field(validation_alias="change_percent")
    volume: int
    day_high: float = Field(validation_alias="high")
    day_low: float = Field(validation_alias="low")
    day_open: float = Field(validation_alias="open")
    previous_close: float = Field(validation_alias="prevClose")
    market_cap: float | None = None
    timestamp: datetime
