"""Webhook response models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class WebhookEvent(BaseModel):
    """Parsed webhook event."""

    id: str
    type: str
    data: dict[str, Any]
    created_at: datetime


class WebhookSubscription(BaseModel):
    """Webhook subscription details."""

    model_config = {"populate_by_name": True}

    id: str
    url: str
    events: list[str]
    symbols: list[str] = Field(default_factory=list)
    description: str | None = None
    active: bool = True
    secret: str | None = None  # Only returned on creation
    created_at: datetime = Field(alias="createdAt")
