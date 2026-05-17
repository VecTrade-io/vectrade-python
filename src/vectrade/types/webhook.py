"""Webhook response models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class WebhookEvent(BaseModel):
    """Parsed webhook event."""

    id: str
    type: str
    data: dict[str, Any]
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
