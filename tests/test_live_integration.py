"""Live integration tests against the production VecTrade API.

These tests verify end-to-end SDK behavior with real data.
Set VECTRADE_API_KEY env var to run (skipped otherwise).
"""

import os

import pytest

pytestmark = pytest.mark.skipif(
    not os.environ.get("VECTRADE_API_KEY"),
    reason="VECTRADE_API_KEY not set — skipping live integration tests",
)


@pytest.fixture(scope="module")
def live_client():
    from vectrade import VecTrade

    client = VecTrade()
    yield client
    client.close()


class TestLiveHealth:
    def test_health_returns_status(self, live_client) -> None:
        health = live_client.health()
        assert "status" in health
        assert health["status"] in ("ok", "degraded")


class TestLiveQuotes:
    def test_get_single_quote(self, live_client) -> None:
        quote = live_client.quotes.get("AAPL")
        assert quote.symbol == "AAPL"
        assert quote.price > 0
        assert quote.volume >= 0
        assert quote.market_cap is not None

    def test_batch_quotes(self, live_client) -> None:
        quotes = live_client.quotes.batch(["MSFT", "GOOGL"])
        assert len(quotes) >= 2
        symbols = {q.symbol for q in quotes}
        assert "MSFT" in symbols
        assert "GOOGL" in symbols
        for q in quotes:
            assert q.price > 0

    def test_get_with_fields(self, live_client) -> None:
        quote = live_client.quotes.get("TSLA")
        assert quote.symbol == "TSLA"
        assert quote.price > 0


class TestLiveFundamentals:
    def test_get_fundamentals(self, live_client) -> None:
        data = live_client.fundamentals.get("AAPL")
        assert data.symbol == "AAPL"
        assert data.company_name
        assert data.market_cap > 0


class TestLiveTechnicals:
    def test_get_technicals(self, live_client) -> None:
        data = live_client.technicals.get("AAPL")
        assert data.symbol == "AAPL"
        assert data.technical_score is not None


class TestLiveNews:
    def test_list_news(self, live_client) -> None:
        articles = live_client.news.list("AAPL", limit=3)
        assert isinstance(articles, list)
        if articles:
            assert articles[0].title
            assert articles[0].source


class TestLiveScreener:
    def test_screener_basic(self, live_client) -> None:
        results = list(live_client.screener.run(sector="Technology", limit=5))
        assert len(results) > 0
        for r in results:
            assert r.symbol
            assert r.price > 0
