"""Tests for analyst resource using respx mocking."""

import httpx
import respx

from vectrade import VecTrade

MOCK_CONSENSUS = {
    "symbol": "AAPL",
    "consensus": "Buy",
    "target_high": 250.0,
    "target_low": 180.0,
    "target_mean": 215.0,
    "target_median": 218.0,
    "total_analysts": 42,
    "buy": 30,
    "hold": 10,
    "sell": 2,
}

MOCK_PRICE_TARGET = {
    "analyst_name": "John Smith",
    "firm": "Goldman Sachs",
    "target": 230.0,
    "rating": "Buy",
    "published_at": "2026-05-10T08:30:00Z",
}

MOCK_RATING = {
    "analyst_name": "Jane Doe",
    "firm": "Morgan Stanley",
    "action": "upgraded",
    "from_rating": "Hold",
    "to_rating": "Buy",
    "target": 225.0,
    "published_at": "2026-05-12T06:00:00Z",
}


class TestAnalystConsensus:
    """Test analyst consensus retrieval."""

    def test_get_consensus(self, client: VecTrade, mock_api: respx.Router) -> None:
        """Fetches analyst consensus."""
        route = mock_api.get("/vq/analyst/AAPL/consensus").mock(
            return_value=httpx.Response(200, json=MOCK_CONSENSUS)
        )
        consensus = client.analyst.consensus("AAPL")
        assert route.called
        assert consensus.symbol == "AAPL"
        assert consensus.consensus == "Buy"
        assert consensus.total_analysts == 42
        assert consensus.buy == 30


class TestAnalystPriceTargets:
    """Test price targets retrieval."""

    def test_get_price_targets(self, client: VecTrade, mock_api: respx.Router) -> None:
        """Fetches analyst price targets."""
        route = mock_api.get("/vq/analyst/AAPL/price-targets").mock(
            return_value=httpx.Response(200, json={"data": [MOCK_PRICE_TARGET]})
        )
        targets = client.analyst.price_targets("AAPL")
        assert route.called
        assert len(targets) == 1
        assert targets[0].firm == "Goldman Sachs"
        assert targets[0].target == 230.0


class TestAnalystRatings:
    """Test analyst ratings retrieval."""

    def test_get_ratings(self, client: VecTrade, mock_api: respx.Router) -> None:
        """Fetches recent rating changes."""
        route = mock_api.get("/vq/analyst/AAPL/ratings").mock(
            return_value=httpx.Response(200, json={"data": [MOCK_RATING]})
        )
        ratings = client.analyst.ratings("AAPL")
        assert route.called
        assert len(ratings) == 1
        assert ratings[0].action == "upgraded"
        assert ratings[0].from_rating == "Hold"
        assert ratings[0].to_rating == "Buy"

    def test_ratings_with_limit(self, client: VecTrade, mock_api: respx.Router) -> None:
        """Passes limit parameter."""
        route = mock_api.get("/vq/analyst/AAPL/ratings").mock(
            return_value=httpx.Response(200, json={"data": []})
        )
        client.analyst.ratings("AAPL", limit=5)
        assert route.called
        request = route.calls.last.request
        assert "limit=5" in str(request.url)
