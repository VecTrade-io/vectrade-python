"""Plan tier configuration — rate limits, quotas, and feature gates.

Plans are **dynamic** — created and modified by admins via the VecTrade
admin API.  The SDK does NOT hardcode tier names or limits.  Instead it
provides data-classes to represent plan/quota responses and a thin
helper that fetches the authenticated user's active plan from the API.

Offline / unauthenticated usage:
    ``DEFAULT_TIERS`` contains well-known defaults matching the platform's
    initial seed plans.  These are **hints only** — always prefer the
    live values from ``/api/v1/vq/developer/plan`` and ``/developer/quota``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# ---------------------------------------------------------------------------
# Response data-classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PlanInfo:
    """Active subscription returned by ``GET /developer/plan``."""

    plan_id: str
    plan_name: str
    status: str
    rate_limit_rpm: int
    rate_limit_rps: int
    monthly_quota: int
    max_keys: int
    includes_ai: bool
    overage_policy: str
    monthly_price_usd: float
    metering_type: str  # "prompt" | "token"
    ai_prompts_per_day: int  # -1 = unlimited
    monthly_tokens: int  # 0 means N/A
    overage_cap_multiplier: float
    description: str = ""

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> PlanInfo:
        """Construct from a ``/developer/plan`` JSON response."""
        return cls(
            plan_id=data.get("plan_id") or data.get("id", ""),
            plan_name=data.get("plan_name") or data.get("name", ""),
            status=data.get("status", "active"),
            rate_limit_rpm=int(data.get("rate_limit_rpm", 0)),
            rate_limit_rps=int(data.get("rate_limit_rps", 0)),
            monthly_quota=int(data.get("monthly_quota", 0)),
            max_keys=int(data.get("max_keys", 0)),
            includes_ai=bool(data.get("includes_ai", False)),
            overage_policy=str(data.get("overage_policy", "BLOCK")),
            monthly_price_usd=float(data.get("monthly_price_usd", 0)),
            metering_type=str(data.get("metering_type", "prompt")),
            ai_prompts_per_day=int(data.get("ai_prompts_per_day", 0)),
            monthly_tokens=int(data.get("monthly_tokens", 0)),
            overage_cap_multiplier=float(data.get("overage_cap_multiplier", 1.0)),
            description=str(data.get("description", "")),
        )


@dataclass(frozen=True)
class QuotaInfo:
    """Quota snapshot returned by ``GET /developer/quota``."""

    plan_id: str
    monthly_quota: int
    used: int
    remaining: int
    overage_policy: str
    reset_at: str

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> QuotaInfo:
        """Construct from a ``/developer/quota`` JSON response."""
        return cls(
            plan_id=data.get("plan_id", ""),
            monthly_quota=int(data.get("monthly_quota", 0)),
            used=int(data.get("used", 0)),
            remaining=int(data.get("remaining", 0)),
            overage_policy=str(data.get("overage_policy", "BLOCK")),
            reset_at=str(data.get("reset_at", "")),
        )

    @property
    def usage_pct(self) -> float:
        """Percentage of monthly quota consumed (0.0-100.0+)."""
        if self.monthly_quota <= 0:
            return 0.0
        return (self.used / self.monthly_quota) * 100.0

    @property
    def is_exhausted(self) -> bool:
        return self.remaining <= 0


# ---------------------------------------------------------------------------
# Well-known defaults (mirrors platform seed_default_plans — HINTS ONLY)
# ---------------------------------------------------------------------------

DEFAULT_TIERS: dict[str, dict[str, Any]] = {
    "free": {
        "rate_limit_rpm": 30,
        "rate_limit_rps": 2,
        "monthly_quota": 10_000,
        "max_keys": 0,
        "monthly_price_usd": 0,
        "overage_policy": "BLOCK",
        "metering_type": "prompt",
        "ai_prompts_per_day": 5,
        "monthly_tokens": 0,
        "overage_cap_multiplier": 1.0,
    },
    "standard": {
        "rate_limit_rpm": 120,
        "rate_limit_rps": 10,
        "monthly_quota": 100_000,
        "max_keys": 5,
        "monthly_price_usd": 19,
        "overage_policy": "PAYG",
        "metering_type": "token",
        "ai_prompts_per_day": -1,
        "monthly_tokens": 1_000_000,
        "overage_cap_multiplier": 2.0,
    },
    "professional": {
        "rate_limit_rpm": 300,
        "rate_limit_rps": 25,
        "monthly_quota": 500_000,
        "max_keys": 20,
        "monthly_price_usd": 49,
        "overage_policy": "PAYG",
        "metering_type": "token",
        "ai_prompts_per_day": -1,
        "monthly_tokens": 5_000_000,
        "overage_cap_multiplier": 2.0,
    },
}


def get_default_tier(name: str) -> dict[str, Any]:
    """Return well-known defaults for a named tier (offline hint).

    Raises ``KeyError`` if *name* is not one of the seed plans.
    """
    return DEFAULT_TIERS[name.lower()]
