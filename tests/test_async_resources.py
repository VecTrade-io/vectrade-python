"""Tests for async resource methods — covers the async variants of all resources."""

import pytest
import respx

from vectrade import AsyncVecTrade

BASE_URL = "https://api.vectrade.io/v1"


@pytest.fixture
async def async_client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("VECTRADE_API_KEY", "vq_test_abcdefghijklmnop1234")
    client = AsyncVecTrade(max_retries=0)
    yield client
    await client.close()


class TestAsyncQuotes:
    @respx.mock
    @pytest.mark.asyncio
    async def test_get(self, async_client) -> None:
        respx.get(f"{BASE_URL}/vq/quotes/AAPL").respond(
            200,
            json={
                "ticker": "AAPL",
                "price": 195.0,
                "change": 2.5,
                "change_percent": 1.3,
                "volume": 50000000,
                "high": 196.0,
                "low": 192.0,
                "open": 193.0,
                "prevClose": 192.5,
                "market_cap": 3e12,
                "timestamp": "2026-05-22T12:00:00",
            },
        )
        quote = await async_client.quotes.get("AAPL")
        assert quote.symbol == "AAPL"
        assert quote.price == 195.0

    @respx.mock
    @pytest.mark.asyncio
    async def test_batch(self, async_client) -> None:
        respx.get(f"{BASE_URL}/vq/quotes/batch").respond(
            200,
            json={
                "tickers": ["AAPL", "MSFT"],
                "data": {
                    "AAPL": {
                        "ticker": "AAPL",
                        "price": 195.0,
                        "change": 2.5,
                        "change_percent": 1.3,
                        "volume": 50000000,
                        "high": 196.0,
                        "low": 192.0,
                        "open": 193.0,
                        "prevClose": 192.5,
                        "market_cap": 3e12,
                        "timestamp": "2026-05-22T12:00:00",
                    },
                    "MSFT": {
                        "ticker": "MSFT",
                        "price": 420.0,
                        "change": -1.0,
                        "change_percent": -0.24,
                        "volume": 30000000,
                        "high": 422.0,
                        "low": 418.0,
                        "open": 421.0,
                        "prevClose": 421.0,
                        "market_cap": 3.1e12,
                        "timestamp": "2026-05-22T12:00:00",
                    },
                },
            },
        )
        quotes = await async_client.quotes.batch(["AAPL", "MSFT"])
        assert len(quotes) == 2
        symbols = {q.symbol for q in quotes}
        assert "AAPL" in symbols
        assert "MSFT" in symbols


class TestAsyncFundamentals:
    @respx.mock
    @pytest.mark.asyncio
    async def test_get(self, async_client) -> None:
        respx.get(f"{BASE_URL}/vq/fundamentals/AAPL").respond(
            200,
            json={
                "ticker": "AAPL",
                "companyName": "Apple Inc.",
                "market": "NASDAQ",
                "market_cap": 3e12,
                "pe_ratio": 28.5,
                "eps": 6.8,
                "dividend_yield": 0.005,
                "beta": 1.2,
                "sma50": 270.0,
                "sma200": 260.0,
                "fiftyTwoWeekHigh": 305.0,
                "fiftyTwoWeekLow": 193.0,
                "sector": "Technology",
                "industry": "Consumer Electronics",
            },
        )
        data = await async_client.fundamentals.get("AAPL")
        assert data.symbol == "AAPL"
        assert data.company_name == "Apple Inc."


class TestAsyncTechnicals:
    @respx.mock
    @pytest.mark.asyncio
    async def test_get(self, async_client) -> None:
        respx.get(f"{BASE_URL}/vq/technical/AAPL").respond(
            200,
            json={
                "symbol": "AAPL",
                "technical_score": 72,
                "rsi_14": 58.3,
                "macd": {"value": 2.1, "signal": 1.8, "histogram": 0.3},
                "moving_averages": {"sma_20": 192.0, "sma_50": 188.0, "sma_200": 175.0},
                "summary": {"overall": "buy"},
            },
        )
        data = await async_client.technicals.get("AAPL")
        assert data.symbol == "AAPL"
        assert data.technical_score == 72


class TestAsyncNews:
    @respx.mock
    @pytest.mark.asyncio
    async def test_list(self, async_client) -> None:
        respx.get(f"{BASE_URL}/vq/news/AAPL").respond(
            200,
            json={
                "articles": [
                    {
                        "id": "news-001",
                        "title": "Apple Hits All-Time High",
                        "source": "Reuters",
                        "url": "https://example.com/news",
                        "published_at": "2026-05-22T10:00:00Z",
                        "symbols": ["AAPL"],
                        "sentiment": 0.8,
                    }
                ]
            },
        )
        articles = await async_client.news.list("AAPL", limit=5)
        assert len(articles) == 1
        assert articles[0].title == "Apple Hits All-Time High"


class TestAsyncEarnings:
    @respx.mock
    @pytest.mark.asyncio
    async def test_history(self, async_client) -> None:
        respx.get(f"{BASE_URL}/vq/earnings/AAPL").respond(
            200,
            json={
                "history": [
                    {
                        "date": "2026-04-25",
                        "quarter": "Q2 2026",
                        "eps_actual": 1.95,
                        "eps_estimate": 1.90,
                        "revenue_actual": 95e9,
                        "revenue_estimate": 94e9,
                        "surprise_pct": 2.6,
                    }
                ]
            },
        )
        results = await async_client.earnings.history("AAPL")
        assert len(results) == 1
        assert results[0].eps_actual == 1.95

    @respx.mock
    @pytest.mark.asyncio
    async def test_calendar(self, async_client) -> None:
        respx.get(f"{BASE_URL}/vq/earnings/calendar").respond(
            200,
            json={
                "data": [
                    {
                        "symbol": "NVDA",
                        "date": "2026-05-28",
                        "time": "after_close",
                        "eps_estimate": 0.82,
                    }
                ]
            },
        )
        entries = await async_client.earnings.calendar(from_date="2026-05-22", to_date="2026-05-30")
        assert len(entries) == 1
        assert entries[0].symbol == "NVDA"


class TestAsyncOptions:
    @respx.mock
    @pytest.mark.asyncio
    async def test_chain(self, async_client) -> None:
        respx.get(f"{BASE_URL}/vq/options/AAPL/chain").respond(
            200,
            json={
                "ticker": "AAPL",
                "expiration": "2026-06-20",
                "calls": [
                    {
                        "contractSymbol": "AAPL260620C00200000",
                        "strike": 200.0,
                        "lastPrice": 5.50,
                        "bid": 5.40,
                        "ask": 5.60,
                        "volume": 1200,
                        "openInterest": 5000,
                        "impliedVolatility": 0.25,
                        "inTheMoney": True,
                        "change": 0.1,
                        "percentChange": 1.8,
                    }
                ],
                "puts": [],
            },
        )
        chain = await async_client.options.chain(
            "AAPL", expiration="2026-06-20", option_type="call"
        )
        assert chain.symbol == "AAPL"

    @respx.mock
    @pytest.mark.asyncio
    async def test_expirations(self, async_client) -> None:
        respx.get(f"{BASE_URL}/vq/options/AAPL/expirations").respond(
            200,
            json={"expirations": ["2026-06-20", "2026-07-18", "2026-08-15"]},
        )
        dates = await async_client.options.expirations("AAPL")
        assert "2026-06-20" in dates


class TestAsyncAnalyst:
    @respx.mock
    @pytest.mark.asyncio
    async def test_ratings(self, async_client) -> None:
        respx.get(f"{BASE_URL}/vq/upgrades-downgrades/AAPL").respond(
            200,
            json={
                "upgrades_downgrades": [
                    {
                        "firm": "Goldman Sachs",
                        "action": "up",
                        "to_grade": "buy",
                        "from_grade": "hold",
                        "date": "2026-05-01",
                    }
                ]
            },
        )
        data = await async_client.analyst.ratings("AAPL")
        assert len(data) == 1
        assert data[0].firm == "Goldman Sachs"
        assert data[0].to_grade == "buy"

    @respx.mock
    @pytest.mark.asyncio
    async def test_price_targets(self, async_client) -> None:
        respx.get(f"{BASE_URL}/vq/analyst-targets/AAPL").respond(
            200,
            json={
                "ticker": "AAPL",
                "targets": {
                    "current": 195.0,
                    "high": 250.0,
                    "low": 180.0,
                    "mean": 215.0,
                    "median": 218.0,
                },
                "source": "yfinance",
                "timestamp": "2026-05-10T14:00:00Z",
            },
        )
        data = await async_client.analyst.price_targets("AAPL")
        assert len(data) == 1
        assert data[0].targets["high"] == 250.0
        assert data[0].symbol == "AAPL"

    @respx.mock
    @pytest.mark.asyncio
    async def test_consensus(self, async_client) -> None:
        respx.get(f"{BASE_URL}/vq/analyst-consensus/AAPL").respond(
            200,
            json={
                "ticker": "AAPL",
                "consensus": "buy",
                "total_analysts": 35,
                "buy": 25,
                "hold": 8,
                "sell": 2,
            },
        )
        data = await async_client.analyst.consensus("AAPL")
        assert data.symbol == "AAPL"
        assert data.consensus == "buy"
        assert data.total_analysts == 35


class TestAsyncInsider:
    @respx.mock
    @pytest.mark.asyncio
    async def test_transactions(self, async_client) -> None:
        respx.get(f"{BASE_URL}/vq/insider/AAPL").respond(
            200,
            json={
                "trades": [
                    {
                        "insider_name": "Tim Cook",
                        "position": "CEO",
                        "transaction_type": "sale",
                        "shares": 50000,
                        "total_value": 9750000.0,
                        "transaction_date": "2026-05-10",
                    }
                ]
            },
        )
        txns = await async_client.insider.transactions("AAPL")
        assert len(txns) == 1
        assert txns[0].insider_name == "Tim Cook"

    @respx.mock
    @pytest.mark.asyncio
    async def test_transactions_with_limit(self, async_client) -> None:
        respx.get(f"{BASE_URL}/vq/insider/AAPL").respond(
            200,
            json={
                "trades": [
                    {
                        "insider_name": "Tim Cook",
                        "position": "CEO",
                        "transaction_type": "purchase",
                        "shares": 10000,
                        "total_value": 1900000.0,
                        "transaction_date": "2026-04-20",
                    }
                ]
            },
        )
        txns = await async_client.insider.transactions("AAPL", limit=5)
        assert len(txns) == 1


class TestAsyncDeveloper:
    @respx.mock
    @pytest.mark.asyncio
    async def test_list_keys(self, async_client) -> None:
        respx.get(f"{BASE_URL}/vq/developer/keys").respond(
            200,
            json=[{"id": "abc123", "key_prefix": "vq_test_abc", "label": "Test", "scopes": ["*"]}],
        )
        keys = await async_client.developer.list_keys()
        assert len(keys) == 1
        assert keys[0]["label"] == "Test"

    @respx.mock
    @pytest.mark.asyncio
    async def test_create_key(self, async_client) -> None:
        respx.post(f"{BASE_URL}/vq/developer/keys").respond(
            200,
            json={
                "id": "new123",
                "key_prefix": "vq_test_new",
                "label": "New Key",
                "scopes": ["quotes", "news"],
                "raw_key": "vq_test_secretkey123",
                "created_at": "2026-05-22T12:00:00Z",
            },
        )
        result = await async_client.developer.create_key(label="New Key", scopes=["quotes", "news"])
        assert result["raw_key"] == "vq_test_secretkey123"

    @respx.mock
    @pytest.mark.asyncio
    async def test_revoke_key(self, async_client) -> None:
        respx.delete(f"{BASE_URL}/vq/developer/keys/abc123").respond(204)
        await async_client.developer.revoke_key("abc123")

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_usage(self, async_client) -> None:
        respx.get(f"{BASE_URL}/vq/developer/usage").respond(
            200,
            json={
                "period": "2026-05",
                "total_requests": 5000,
                "ai_requests": 200,
                "error_count": 15,
                "tokens_used": 50000,
                "quota_limit": 100000,
                "quota_remaining": 95000,
            },
        )
        usage = await async_client.developer.get_usage()
        assert usage["total_requests"] == 5000

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_daily_usage(self, async_client) -> None:
        respx.get(f"{BASE_URL}/vq/developer/usage/daily").respond(
            200,
            json=[{"date": "2026-05-21", "requests": 150, "errors": 2}],
        )
        daily = await async_client.developer.get_daily_usage(days=7)
        assert len(daily) == 1

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_plan(self, async_client) -> None:
        respx.get(f"{BASE_URL}/vq/developer/plan").respond(
            200,
            json={
                "plan_id": "professional",
                "plan_name": "Professional",
                "status": "ACTIVE",
                "current_period_start": "2026-05-01",
                "current_period_end": "2026-06-01",
            },
        )
        plan = await async_client.developer.get_plan()
        assert plan["plan_id"] == "professional"

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_quota(self, async_client) -> None:
        respx.get(f"{BASE_URL}/vq/developer/quota").respond(
            200,
            json={
                "plan_id": "professional",
                "monthly_quota": 500000,
                "used": 1000,
                "remaining": 499000,
                "overage_policy": "THROTTLE",
                "reset_at": "2026-06-01T00:00:00Z",
            },
        )
        quota = await async_client.developer.get_quota()
        assert quota["remaining"] == 499000


class TestAsyncScreener:
    @respx.mock
    @pytest.mark.asyncio
    async def test_run(self, async_client) -> None:
        respx.post(f"{BASE_URL}/vq/screener/filter").respond(
            200,
            json={
                "data": [
                    {
                        "symbol": "NVDA",
                        "company_name": "NVIDIA Corp.",
                        "price": 220.0,
                        "change_pct": 2.1,
                        "market_cap": 5.4e12,
                    }
                ],
                "page_info": {"has_next": False, "cursor": None, "total": 1},
            },
        )
        results = []
        async for item in async_client.screener.run(market_cap_min=1e12, pe_max=50.0, limit=10):
            results.append(item)
        assert len(results) == 1
        assert results[0].symbol == "NVDA"
