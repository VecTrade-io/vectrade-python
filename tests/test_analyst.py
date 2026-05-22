"""Tests for analyst resource using respx mocking."""

import httpx
import respx

from vectrade import VecTrade

MOCK_CONSENSUS = {
    "ticker": "AAPL",
    "consensus": "BUY",
    "signal": "buy",
    "consensus_score": 4.2,
    "total_analysts": 42,
    "ratings": {"strong_buy": 20, "buy": 10, "hold": 10, "sell": 2, "strong_sell": 0},
    "target_price": 215.0,
    "buy": 30,
    "hold": 10,
    "sell": 2,
}

MOCK_PRICE_TARGET = {
    "ticker": "AAPL",
    "targets": {"current": 195.0, "high": 250.0, "low": 180.0, "mean": 215.0, "median": 218.0},
    "source": "yfinance",
    "timestamp": "2026-05-10T08:30:00Z",
}

MOCK_RATING = {
    "firm": "Morgan Stanley",
    "action": "up",
    "to_grade": "Buy",
    "from_grade": "Hold",
    "date": "2026-05-12",
}


class TestAnalystConsensus:
    """Test analyst consensus retrieval."""

    def test_get_consensus(self, client: VecTrade, mock_api: respx.Router) -> None:
        """Fetches analyst consensus."""
        route = mock_api.get("/vq/analyst-consensus/AAPL").mock(
            return_value=httpx.Response(200, json=MOCK_CONSENSUS)
        )
        consensus = client.analyst.consensus("AAPL")
        assert route.called
        assert consensus.symbol == "AAPL"
        assert consensus.consensus == "BUY"
        assert consensus.total_analysts == 42


class TestAnalystPriceTargets:
    """Test price targets retrieval."""

    def test_get_price_targets(self, client: VecTrade, mock_api: respx.Router) -> None:
        """Fetches analyst price targets."""
        route = mock_api.get("/vq/analyst-targets/AAPL").mock(
            return_value=httpx.Response(200, json=MOCK_PRICE_TARGET)
        )
        targets = client.analyst.price_targets("AAPL")
        assert route.called
        assert len(targets) == 1
        assert targets[0].symbol == "AAPL"
        assert targets[0].targets["high"] == 250.0


class TestAnalystRatings:
    """Test analyst ratings retrieval."""

    def test_get_ratings(self, client: VecTrade, mock_api: respx.Router) -> None:
        """Fetches recent rating changes."""
        route = mock_api.get("/vq/upgrades-downgrades/AAPL").mock(
            return_value=httpx.Response(200, json={"upgrades_downgrades": [MOCK_RATING]})
        )
        ratings = client.analyst.ratings("AAPL")
        assert route.called
        assert len(ratings) == 1
        assert ratings[0].action == "up"
        assert ratings[0].from_grade == "Hold"
        assert ratings[0].to_grade == "Buy"

    def test_ratings_with_limit(self, client: VecTrade, mock_api: respx.Router) -> None:
        """Passes limit parameter."""
        route = mock_api.get("/vq/upgrades-downgrades/AAPL").mock(
            return_value=httpx.Response(200, json={"upgrades_downgrades": []})
        )
        client.analyst.ratings("AAPL", limit=5)
        assert route.called
