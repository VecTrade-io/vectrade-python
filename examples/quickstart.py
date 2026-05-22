"""Quick start example — fetch a quote and display basic info."""

from vectrade import VecTrade

vt = VecTrade()  # reads VECTRADE_API_KEY from environment

# Get a real-time quote
quote = vt.quotes.get("AAPL")
print(f"{quote.symbol}: ${quote.price:.2f} ({quote.change_percent:+.2f}%)")
print(f"  Volume: {quote.volume:,}")
print(f"  Day Range: ${quote.day_low:.2f} - ${quote.day_high:.2f}")
