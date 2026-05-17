"""Insider trading response types."""

from __future__ import annotations

from pydantic import BaseModel, Field


class InsiderTransaction(BaseModel):
    """Individual insider transaction."""

    model_config = {"populate_by_name": True}

    insider_name: str = Field(validation_alias="insider")
    position: str | None = None
    transaction_type: str | None = Field(default=None, validation_alias="transaction_type")
    shares: int | None = None
    total_value: float | None = Field(default=None, validation_alias="value")
    transaction_date: str | None = None
    ownership: str | None = None
    description: str | None = None


class InsiderSummary(BaseModel):
    """Insider trading summary."""

    model_config = {"populate_by_name": True}

    symbol: str = Field(validation_alias="ticker")
    buy_count: int = 0
    sell_count: int = 0
    exercise_count: int = 0
    buy_volume: int = 0
    sell_volume: int = 0
    net_trades: int = 0
    count: int = 0
