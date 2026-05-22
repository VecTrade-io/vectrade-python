"""Use the stock screener to find undervalued tech stocks."""

from vectrade import VecTrade

vt = VecTrade()

# Screen for large-cap tech with low P/E
results = vt.screener.filter(
    market_cap_min=10_000_000_000,
    sector="Technology",
    pe_max=25,
    limit=10,
)

print("Undervalued Large-Cap Tech:")
print(f"{'Symbol':<8} {'Name':<25} {'Market Cap':>14} {'P/E':>8}")
print("-" * 58)
for stock in results.results:
    mcap = f"${stock.market_cap / 1e9:.1f}B" if stock.market_cap else "N/A"
    print(f"{stock.symbol:<8} {stock.name:<25} {mcap:>14} {stock.pe_ratio or 'N/A':>8}")
