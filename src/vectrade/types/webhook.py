"""Webhook response models."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class WebhookEvent(BaseModel):
    """Parsed webhook event."""

    id: str
    type: str
    data: dict
    created_at: datetime


class WebhookSubscription(BaseModel):
    """Webhook subscription details."""

    id: str
    url: str
    events: list[str]
    description: str | None = None
    active: bool = True
    secret: str | None = None  # Only returned on creation
    created_at: datetime
