"""Monitor your API usage and manage keys programmatically."""

from vectrade import VecTrade

vt = VecTrade()

# Check current plan
plan = vt.developer.get_plan()
print(f"Plan: {plan.plan_name} (${plan.monthly_price_usd}/mo)")
print(f"Rate Limit: {plan.rate_limit_rpm} req/min")

# Check quota
quota = vt.developer.get_quota()
print(f"\nUsage: {quota.used:,} / {quota.monthly_quota:,} ({quota.usage_pct:.1f}%)")
print(f"Remaining: {quota.remaining:,} requests")

# List active keys
keys = vt.developer.list_keys()
print(f"\nAPI Keys ({len(keys)}):")
for key in keys:
    print(f"  {key.key_prefix}... [{key.status}] — {key.label}")
