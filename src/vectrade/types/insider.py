"""Insider trading response types."""

from __future__ import annotations

from pydantic import BaseModel


class InsiderTransaction(BaseModel):
    """Individual insider transaction."""

    symbol: str
    insider_name: str
    title: str
    transaction_type: str  # "buy", "sell", "exercise"
    shares: int
    price: float
    total_value: float
    shares_owned_after: int
    filed_at: str


class InsiderSummary(BaseModel):
    """Insider trading summary over recent periods."""

    symbol: str
    net_shares_30d: int
    net_value_30d: float
    net_shares_90d: int
    net_value_90d: float
    buy_count_90d: int
    sell_count_90d: int
    most_recent_transaction: InsiderTransaction | None = None
