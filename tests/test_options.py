"""Tests for options resource using respx mocking."""

import httpx
import respx

from vectrade import VecTrade

MOCK_OPTION_CONTRACT = {
    "contractSymbol": "AAPL260620C00200000",
    "strike": 200.0,
    "lastPrice": 5.50,
    "bid": 5.40,
    "ask": 5.60,
    "volume": 12500,
    "openInterest": 34000,
    "impliedVolatility": 0.28,
    "inTheMoney": True,
    "change": 0.2,
    "percentChange": 3.8,
}

MOCK_OPTIONS_CHAIN = {
    "ticker": "AAPL",
    "expiration": "2026-06-20",
    "calls": [MOCK_OPTION_CONTRACT],
    "puts": [],
}


class TestOptionsChain:
    """Test options chain retrieval."""

    def test_get_chain(self, client: VecTrade, mock_api: respx.Router) -> None:
        """Fetches full options chain."""
        route = mock_api.get("/vq/options/AAPL/chain").mock(
            return_value=httpx.Response(200, json=MOCK_OPTIONS_CHAIN)
        )
        chain = client.options.chain("AAPL")
        assert route.called
        assert chain.symbol == "AAPL"
        assert len(chain.calls) == 1
        assert chain.calls[0].strike == 200.0

    def test_chain_with_filters(self, client: VecTrade, mock_api: respx.Router) -> None:
        """Fetches chain with expiration and type filters."""
        route = mock_api.get("/vq/options/AAPL/chain").mock(
            return_value=httpx.Response(200, json=MOCK_OPTIONS_CHAIN)
        )
        client.options.chain("AAPL", expiration="2026-06-20", option_type="call")
        assert route.called
        request = route.calls.last.request
        assert "expiration=2026-06-20" in str(request.url)
        assert "type=call" in str(request.url)


class TestOptionsExpirations:
    """Test available expirations."""

    def test_get_expirations(self, client: VecTrade, mock_api: respx.Router) -> None:
        """Fetches available expiration dates."""
        mock_response = {"expirations": ["2026-06-20", "2026-07-18", "2026-08-15"]}
        route = mock_api.get("/vq/options/AAPL/expirations").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        expirations = client.options.expirations("AAPL")
        assert route.called
        assert len(expirations) == 3
        assert expirations[0] == "2026-06-20"
