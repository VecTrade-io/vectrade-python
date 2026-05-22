"""Async example — fetch multiple quotes concurrently."""

import asyncio

from vectrade import AsyncVecTrade


async def main():
    async with AsyncVecTrade() as vt:
        symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]

        # Fetch quotes concurrently
        quotes = await asyncio.gather(*[vt.quotes.get(s) for s in symbols])

        print("Portfolio Snapshot:")
        print(f"{'Symbol':<8} {'Price':>10} {'Change':>10}")
        print("-" * 30)
        for q in sorted(quotes, key=lambda x: x.change_percent, reverse=True):
            print(f"{q.symbol:<8} ${q.price:>8.2f} {q.change_percent:>+8.2f}%")


if __name__ == "__main__":
    asyncio.run(main())
