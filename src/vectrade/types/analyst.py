"""Analyst response types."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AnalystConsensus(BaseModel):
    """Consensus analyst rating."""

    symbol: str = Field(alias="ticker")
    consensus: str  # "BUY", "HOLD", "SELL"
    target_high: float | None = Field(None, alias="target_high")
    target_low: float | None = Field(None, alias="target_low")
    target_mean: float | None = Field(None, alias="target_mean")
    target_median: float | None = Field(None, alias="target_median")
    total_analysts: int = 0
    buy: int = 0
    hold: int = 0
    sell: int = 0
    signal: str | None = None
    consensus_score: float | None = None
    ratings: dict | None = None
    target_price: float | None = None

    model_config = {"populate_by_name": True}


class PriceTarget(BaseModel):
    """Aggregated analyst price targets for a symbol."""

    symbol: str = Field(alias="ticker")
    targets: dict  # {"current", "high", "low", "mean", "median"}
    source: str | None = None
    timestamp: str | None = None

    model_config = {"populate_by_name": True}

    @property
    def target_high(self) -> float | None:
        return self.targets.get("high")

    @property
    def target_low(self) -> float | None:
        return self.targets.get("low")

    @property
    def target_mean(self) -> float | None:
        return self.targets.get("mean")

    @property
    def current(self) -> float | None:
        return self.targets.get("current")


class AnalystRating(BaseModel):
    """Analyst rating change event."""

    firm: str
    action: str  # "main", "up", "down", "init"
    to_grade: str = ""
    from_grade: str = ""
    date: str | None = None
