"""Options response types."""

from __future__ import annotations

from pydantic import BaseModel


class OptionContract(BaseModel):
    """A single option contract."""

    contract_symbol: str
    type: str  # "call" or "put"
    strike: float
    expiration: str
    bid: float
    ask: float
    last_price: float
    volume: int
    open_interest: int
    implied_volatility: float
    delta: float | None = None
    gamma: float | None = None
    theta: float | None = None
    vega: float | None = None


class OptionsChain(BaseModel):
    """Full options chain for a symbol."""

    symbol: str
    expirations: list[str]
    chain: list[OptionContract]
