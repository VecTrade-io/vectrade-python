"""Tests for tier configuration — dynamic plan models and default hints."""

import pytest

from vectrade.tier_config import (
    DEFAULT_TIERS,
    PlanInfo,
    QuotaInfo,
    get_default_tier,
)


class TestDefaultTiers:
    """Test the well-known seed-plan defaults (offline hints)."""

    def test_all_seed_plans_present(self):
        assert set(DEFAULT_TIERS.keys()) == {"free", "standard", "professional"}

    def test_free_is_zero_cost(self):
        free = DEFAULT_TIERS["free"]
        assert free["monthly_price_usd"] == 0

    def test_rate_limits_increase_with_tier(self):
        order = ["free", "standard", "professional"]
        for i in range(len(order) - 1):
            lower = DEFAULT_TIERS[order[i]]
            higher = DEFAULT_TIERS[order[i + 1]]
            assert higher["rate_limit_rpm"] > lower["rate_limit_rpm"]
            assert higher["rate_limit_rps"] > lower["rate_limit_rps"]

    def test_quotas_increase_with_tier(self):
        order = ["free", "standard", "professional"]
        for i in range(len(order) - 1):
            lower = DEFAULT_TIERS[order[i]]
            higher = DEFAULT_TIERS[order[i + 1]]
            assert higher["monthly_quota"] > lower["monthly_quota"]
            assert higher["max_keys"] >= lower["max_keys"]

    def test_overage_policies(self):
        assert DEFAULT_TIERS["free"]["overage_policy"] == "BLOCK"
        assert DEFAULT_TIERS["standard"]["overage_policy"] == "PAYG"
        assert DEFAULT_TIERS["professional"]["overage_policy"] == "PAYG"


class TestGetDefaultTier:
    """Test get_default_tier helper."""

    def test_lookup_by_name(self):
        tier = get_default_tier("professional")
        assert tier["rate_limit_rpm"] == 300

    def test_case_insensitive(self):
        tier = get_default_tier("FREE")
        assert tier["monthly_quota"] == 10_000

    def test_invalid_tier_raises(self):
        with pytest.raises(KeyError):
            get_default_tier("platinum")


class TestPlanInfo:
    """Test PlanInfo dataclass and from_api factory."""

    def test_from_api_full_response(self):
        data = {
            "plan_id": "standard",
            "plan_name": "Standard",
            "status": "active",
            "rate_limit_rpm": 120,
            "rate_limit_rps": 10,
            "monthly_quota": 100_000,
            "max_keys": 5,
            "includes_ai": True,
            "overage_policy": "PAYG",
            "monthly_price_usd": 19.0,
            "metering_type": "token",
            "ai_prompts_per_day": -1,
            "monthly_tokens": 1_000_000,
            "overage_cap_multiplier": 2.0,
            "description": "For active traders",
        }
        plan = PlanInfo.from_api(data)
        assert plan.plan_id == "standard"
        assert plan.rate_limit_rpm == 120
        assert plan.monthly_quota == 100_000
        assert plan.overage_policy == "PAYG"
        assert plan.metering_type == "token"

    def test_from_api_minimal_response(self):
        """from_api should handle missing keys with safe defaults."""
        plan = PlanInfo.from_api({"id": "free", "name": "Free"})
        assert plan.plan_id == "free"
        assert plan.plan_name == "Free"
        assert plan.rate_limit_rpm == 0
        assert plan.overage_policy == "BLOCK"

    def test_frozen(self):
        plan = PlanInfo.from_api({"plan_id": "x", "plan_name": "X"})
        with pytest.raises(AttributeError):
            plan.plan_id = "y"  # type: ignore[misc]


class TestQuotaInfo:
    """Test QuotaInfo dataclass and helpers."""

    def test_from_api(self):
        data = {
            "plan_id": "standard",
            "monthly_quota": 100_000,
            "used": 43_000,
            "remaining": 57_000,
            "overage_policy": "PAYG",
            "reset_at": "2026-06-01T00:00:00Z",
        }
        quota = QuotaInfo.from_api(data)
        assert quota.used == 43_000
        assert quota.remaining == 57_000
        assert quota.usage_pct == pytest.approx(43.0)
        assert not quota.is_exhausted

    def test_exhausted(self):
        quota = QuotaInfo.from_api(
            {
                "plan_id": "free",
                "monthly_quota": 10_000,
                "used": 10_000,
                "remaining": 0,
                "overage_policy": "BLOCK",
                "reset_at": "2026-06-01T00:00:00Z",
            }
        )
        assert quota.is_exhausted
        assert quota.usage_pct == pytest.approx(100.0)

    def test_usage_pct_over_quota(self):
        quota = QuotaInfo.from_api(
            {
                "plan_id": "standard",
                "monthly_quota": 100_000,
                "used": 150_000,
                "remaining": -50_000,
                "overage_policy": "PAYG",
                "reset_at": "",
            }
        )
        assert quota.usage_pct == pytest.approx(150.0)
        assert quota.is_exhausted
