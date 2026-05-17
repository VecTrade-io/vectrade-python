"""News response models."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class NewsArticle(BaseModel):
    """Financial news article."""

    model_config = {"populate_by_name": True}

    id: str = Field(validation_alias="uuid")
    title: str = Field(validation_alias="headline")
    summary: str | None = None
    url: str
    source: str
    published_at: datetime = Field(validation_alias="datetime")
    symbols: list[str] = Field(default_factory=list, validation_alias="related")
    category: str | None = Field(default=None, validation_alias="type")
    sentiment: float | None = None  # -1.0 to 1.0
    image_url: str | None = Field(default=None, validation_alias="image")
