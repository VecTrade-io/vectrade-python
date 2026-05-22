"""Fetch options chain and find high-volume contracts."""

from vectrade import VecTrade

vt = VecTrade()

# Get available expirations
expirations = vt.options.get_expirations("SPY")
print(f"Available expirations: {len(expirations.dates)}")

# Fetch the nearest chain
chain = vt.options.get_chain("SPY", expiration=expirations.dates[0])

# Find high-volume calls
high_vol_calls = [c for c in chain.calls if (c.volume or 0) > 10000]
print(f"\nHigh-volume calls ({expirations.dates[0]}):")
for call in sorted(high_vol_calls, key=lambda c: c.volume or 0, reverse=True)[:5]:
    print(f"  Strike ${call.strike:.0f}: vol={call.volume:,}, OI={call.open_interest:,}")
