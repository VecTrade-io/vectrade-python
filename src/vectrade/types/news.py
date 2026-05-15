"""News response models."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class NewsArticle(BaseModel):
    """Financial news article."""

    id: str
    title: str
    summary: str | None = None
    url: str
    source: str
    published_at: datetime
    symbols: list[str] = []
    category: str | None = None
    sentiment: float | None = None  # -1.0 to 1.0
    image_url: str | None = None
