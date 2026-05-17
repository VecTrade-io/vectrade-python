"""Webhook event types — canonical event catalog for VecTrade platform.

This module defines all webhook event types, their payloads, and delivery guarantees.
Events follow CloudEvents specification (https://cloudevents.io/).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class EventCategory(str, Enum):
    """Webhook event categories."""

    MARKET_DATA = "market_data"
    ACCOUNT = "account"
    AI = "ai"
    SYSTEM = "system"


class DeliveryGuarantee(str, Enum):
    """Event delivery guarantee level."""

    AT_LEAST_ONCE = "at_least_once"
    AT_MOST_ONCE = "at_most_once"
    BEST_EFFORT = "best_effort"


@dataclass(frozen=True)
class EventDefinition:
    """Defines a webhook event type and its characteristics."""

    event_type: str
    category: EventCategory
    description: str
    payload_schema: str
    delivery: DeliveryGuarantee
    retry_policy: str
    available_tiers: tuple[str, ...]


# Complete webhook event catalog
EVENT_CATALOG: dict[str, EventDefinition] = {
    # Market Data Events
    "quote.price_alert": EventDefinition(
        event_type="quote.price_alert",
        category=EventCategory.MARKET_DATA,
        description="Triggered when a watched symbol crosses a price threshold.",
        payload_schema="PriceAlertPayload",
        delivery=DeliveryGuarantee.AT_LEAST_ONCE,
        retry_policy="3 retries with exponential backoff (1s, 4s, 16s)",
        available_tiers=("starter", "pro", "enterprise"),
    ),
    "quote.volume_spike": EventDefinition(
        event_type="quote.volume_spike",
        category=EventCategory.MARKET_DATA,
        description="Triggered when volume exceeds 3x the 20-day average.",
        payload_schema="VolumeSpikePayload",
        delivery=DeliveryGuarantee.AT_LEAST_ONCE,
        retry_policy="3 retries with exponential backoff",
        available_tiers=("pro", "enterprise"),
    ),
    "quote.market_open": EventDefinition(
        event_type="quote.market_open",
        category=EventCategory.MARKET_DATA,
        description="Fired daily at market open with pre-market summary.",
        payload_schema="MarketOpenPayload",
        delivery=DeliveryGuarantee.BEST_EFFORT,
        retry_policy="No retry (time-sensitive)",
        available_tiers=("starter", "pro", "enterprise"),
    ),
    "quote.market_close": EventDefinition(
        event_type="quote.market_close",
        category=EventCategory.MARKET_DATA,
        description="Fired daily at market close with end-of-day summary.",
        payload_schema="MarketClosePayload",
        delivery=DeliveryGuarantee.BEST_EFFORT,
        retry_policy="No retry (time-sensitive)",
        available_tiers=("starter", "pro", "enterprise"),
    ),
    # Earnings & Analyst Events
    "earnings.released": EventDefinition(
        event_type="earnings.released",
        category=EventCategory.MARKET_DATA,
        description="Triggered when a watched company releases earnings.",
        payload_schema="EarningsReleasedPayload",
        delivery=DeliveryGuarantee.AT_LEAST_ONCE,
        retry_policy="5 retries with exponential backoff",
        available_tiers=("starter", "pro", "enterprise"),
    ),
    "earnings.upcoming": EventDefinition(
        event_type="earnings.upcoming",
        category=EventCategory.MARKET_DATA,
        description="Reminder 24h before a watched company reports earnings.",
        payload_schema="EarningsUpcomingPayload",
        delivery=DeliveryGuarantee.AT_LEAST_ONCE,
        retry_policy="3 retries",
        available_tiers=("pro", "enterprise"),
    ),
    "analyst.rating_change": EventDefinition(
        event_type="analyst.rating_change",
        category=EventCategory.MARKET_DATA,
        description="Triggered on analyst upgrade/downgrade for watched symbols.",
        payload_schema="RatingChangePayload",
        delivery=DeliveryGuarantee.AT_LEAST_ONCE,
        retry_policy="3 retries with exponential backoff",
        available_tiers=("pro", "enterprise"),
    ),
    # Insider Events
    "insider.transaction": EventDefinition(
        event_type="insider.transaction",
        category=EventCategory.MARKET_DATA,
        description="Triggered when an insider transaction is filed for watched symbols.",
        payload_schema="InsiderTransactionPayload",
        delivery=DeliveryGuarantee.AT_LEAST_ONCE,
        retry_policy="3 retries with exponential backoff",
        available_tiers=("pro", "enterprise"),
    ),
    # AI Events
    "ai.analysis_complete": EventDefinition(
        event_type="ai.analysis_complete",
        category=EventCategory.AI,
        description="Triggered when an async AI analysis job completes.",
        payload_schema="AnalysisCompletePayload",
        delivery=DeliveryGuarantee.AT_LEAST_ONCE,
        retry_policy="5 retries with exponential backoff",
        available_tiers=("pro", "enterprise"),
    ),
    # Account Events
    "account.usage_threshold": EventDefinition(
        event_type="account.usage_threshold",
        category=EventCategory.ACCOUNT,
        description="Triggered at 80% and 95% of plan quota usage.",
        payload_schema="UsageThresholdPayload",
        delivery=DeliveryGuarantee.AT_LEAST_ONCE,
        retry_policy="3 retries",
        available_tiers=("starter", "pro", "enterprise"),
    ),
    "account.key_created": EventDefinition(
        event_type="account.key_created",
        category=EventCategory.ACCOUNT,
        description="Triggered when a new API key is created.",
        payload_schema="KeyEventPayload",
        delivery=DeliveryGuarantee.AT_LEAST_ONCE,
        retry_policy="3 retries",
        available_tiers=("starter", "pro", "enterprise"),
    ),
    "account.key_revoked": EventDefinition(
        event_type="account.key_revoked",
        category=EventCategory.ACCOUNT,
        description="Triggered when an API key is revoked.",
        payload_schema="KeyEventPayload",
        delivery=DeliveryGuarantee.AT_LEAST_ONCE,
        retry_policy="3 retries",
        available_tiers=("starter", "pro", "enterprise"),
    ),
    # System Events
    "system.maintenance_scheduled": EventDefinition(
        event_type="system.maintenance_scheduled",
        category=EventCategory.SYSTEM,
        description="Advance notice of planned maintenance windows.",
        payload_schema="MaintenancePayload",
        delivery=DeliveryGuarantee.AT_LEAST_ONCE,
        retry_policy="5 retries",
        available_tiers=("starter", "pro", "enterprise"),
    ),
    "system.incident_update": EventDefinition(
        event_type="system.incident_update",
        category=EventCategory.SYSTEM,
        description="Status updates during active incidents.",
        payload_schema="IncidentPayload",
        delivery=DeliveryGuarantee.AT_LEAST_ONCE,
        retry_policy="5 retries",
        available_tiers=("starter", "pro", "enterprise"),
    ),
}


def get_events_for_tier(tier: str) -> list[EventDefinition]:
    """Get all events available for a given plan tier.

    Args:
        tier: Plan tier name ("starter", "pro", "enterprise").

    Returns:
        List of EventDefinition objects available for this tier.
    """
    return [e for e in EVENT_CATALOG.values() if tier in e.available_tiers]


def get_events_by_category(category: EventCategory) -> list[EventDefinition]:
    """Get all events in a specific category.

    Args:
        category: EventCategory to filter by.

    Returns:
        List of EventDefinition objects in this category.
    """
    return [e for e in EVENT_CATALOG.values() if e.category == category]
