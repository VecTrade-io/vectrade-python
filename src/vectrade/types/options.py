"""Options response types."""

from __future__ import annotations

from pydantic import BaseModel, Field


class OptionContract(BaseModel):
    """A single option contract."""

    contract_symbol: str = Field(alias="contractSymbol")
    type: str = ""  # "call" or "put"
    strike: float = 0.0
    expiration: str = ""
    bid: float = 0.0
    ask: float = 0.0
    last_price: float = Field(0.0, alias="lastPrice")
    volume: int | None = 0
    open_interest: int | None = Field(0, alias="openInterest")
    implied_volatility: float = Field(0.0, alias="impliedVolatility")
    in_the_money: bool = Field(False, alias="inTheMoney")
    change: float = 0.0
    percent_change: float = Field(0.0, alias="percentChange")
    delta: float | None = None
    gamma: float | None = None
    theta: float | None = None
    vega: float | None = None

    model_config = {"populate_by_name": True}


class OptionsChain(BaseModel):
    """Full options chain for a symbol."""

    symbol: str = Field(alias="ticker")
    expiration: str = ""
    calls: list[OptionContract] = []
    puts: list[OptionContract] = []

    model_config = {"populate_by_name": True}

    @property
    def chain(self) -> list[OptionContract]:
        """All contracts (calls + puts) as a flat list."""
        return self.calls + self.puts
