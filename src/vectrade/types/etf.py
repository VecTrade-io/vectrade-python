"""ETF data response models."""

from __future__ import annotations

from pydantic import BaseModel


class ETFResponse(BaseModel):
    """ETF information and holdings data."""

    model_config = {"populate_by_name": True}

    ticker: str
    asset_class: str | None = None
    name: str | None = None
    description: str | None = None
    category: str | None = None
    fund_family: str | None = None
    legal_type: str | None = None
    exchange: str | None = None
    currency: str | None = None
    expense_ratio: float | None = None
    total_assets: float | None = None
    nav_price: float | None = None
    price: float | None = None
    previous_close: float | None = None
    ytd_return: float | None = None
    three_year_avg_return: float | None = None
    five_year_avg_return: float | None = None
    beta_3year: float | None = None
    trailing_pe: float | None = None
    fifty_two_week_high: float | None = None
    fifty_two_week_low: float | None = None
    average_volume: int | None = None
    volume: int | None = None
    top_holdings: list[dict] | None = None
    sector_weights: dict | None = None
