"""Tests for webhook event catalog."""

import pytest

from vectrade.webhook_events import (
    EVENT_CATALOG,
    DeliveryGuarantee,
    EventCategory,
    EventDefinition,
    get_events_by_category,
    get_events_for_tier,
)


class TestEventCatalog:
    """Test the webhook event catalog structure."""

    def test_catalog_not_empty(self):
        assert len(EVENT_CATALOG) > 0

    def test_all_entries_are_event_definitions(self):
        for key, event in EVENT_CATALOG.items():
            assert isinstance(event, EventDefinition)
            assert event.event_type == key

    def test_all_events_have_required_fields(self):
        for event in EVENT_CATALOG.values():
            assert event.event_type
            assert event.category in EventCategory
            assert event.description
            assert event.payload_schema
            assert event.delivery in DeliveryGuarantee
            assert event.retry_policy
            assert len(event.available_tiers) > 0

    def test_event_type_format(self):
        """Event types must follow 'category.action' format."""
        for event_type in EVENT_CATALOG:
            parts = event_type.split(".")
            assert len(parts) == 2, f"Invalid event type format: {event_type}"

    def test_known_events_exist(self):
        expected = [
            "quote.price_alert",
            "earnings.released",
            "insider.transaction",
            "ai.analysis_complete",
            "account.usage_threshold",
            "system.maintenance_scheduled",
        ]
        for event_type in expected:
            assert event_type in EVENT_CATALOG


class TestGetEventsForTier:
    """Test tier-based event filtering."""

    def test_enterprise_gets_all_events(self):
        enterprise_events = get_events_for_tier("enterprise")
        assert len(enterprise_events) == len(EVENT_CATALOG)

    def test_starter_subset_of_pro(self):
        starter = set(e.event_type for e in get_events_for_tier("starter"))
        pro = set(e.event_type for e in get_events_for_tier("pro"))
        assert starter.issubset(pro)

    def test_pro_subset_of_enterprise(self):
        pro = set(e.event_type for e in get_events_for_tier("pro"))
        enterprise = set(e.event_type for e in get_events_for_tier("enterprise"))
        assert pro.issubset(enterprise)

    def test_free_tier_gets_no_events(self):
        free_events = get_events_for_tier("free")
        assert len(free_events) == 0


class TestGetEventsByCategory:
    """Test category-based event filtering."""

    def test_market_data_has_events(self):
        events = get_events_by_category(EventCategory.MARKET_DATA)
        assert len(events) > 0

    def test_system_has_events(self):
        events = get_events_by_category(EventCategory.SYSTEM)
        assert len(events) >= 2

    def test_all_categories_covered(self):
        covered = set()
        for event in EVENT_CATALOG.values():
            covered.add(event.category)
        assert covered == set(EventCategory)

    def test_category_filter_is_accurate(self):
        for category in EventCategory:
            events = get_events_by_category(category)
            for event in events:
                assert event.category == category
