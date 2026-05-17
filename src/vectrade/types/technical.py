"""Technical analysis response models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TechnicalResponse(BaseModel):
    """Technical analysis response with computed indicators."""

    model_config = {"populate_by_name": True}

    symbol: str = Field(validation_alias="ticker")
    technical_score: int | None = None
    rsi_14: float | None = None
    macd: dict[str, Any] | None = None
    bollinger_bands: dict[str, Any] | None = None
    moving_averages: dict[str, Any] | None = None
    indicators: dict[str, Any] | None = None
    support_resistance: dict[str, Any] | None = None
    summary: dict[str, Any] | None = None
    timestamp: datetime | None = None
