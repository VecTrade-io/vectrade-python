"""Tests for options resource using respx mocking."""

import httpx
import pytest
import respx

from vectrade import VecTrade


MOCK_OPTION_CONTRACT = {
    "contract_symbol": "AAPL260620C00200000",
    "type": "call",
    "strike": 200.0,
    "expiration": "2026-06-20",
    "bid": 5.40,
    "ask": 5.60,
    "last_price": 5.50,
    "volume": 12500,
    "open_interest": 34000,
    "implied_volatility": 0.28,
    "delta": 0.45,
    "gamma": 0.03,
    "theta": -0.05,
    "vega": 0.18,
}

MOCK_OPTIONS_CHAIN = {
    "symbol": "AAPL",
    "expirations": ["2026-06-20", "2026-07-18", "2026-08-15"],
    "chain": [MOCK_OPTION_CONTRACT],
}


class TestOptionsChain:
    """Test options chain retrieval."""

    def test_get_chain(self, client: VecTrade, mock_api: respx.Router) -> None:
        """Fetches full options chain."""
        route = mock_api.get("/vq/options/AAPL").mock(
            return_value=httpx.Response(200, json=MOCK_OPTIONS_CHAIN)
        )
        chain = client.options.chain("AAPL")
        assert route.called
        assert chain.symbol == "AAPL"
        assert len(chain.chain) == 1
        assert chain.chain[0].strike == 200.0
        assert chain.chain[0].delta == 0.45

    def test_chain_with_filters(self, client: VecTrade, mock_api: respx.Router) -> None:
        """Fetches chain with expiration and type filters."""
        route = mock_api.get("/vq/options/AAPL").mock(
            return_value=httpx.Response(200, json=MOCK_OPTIONS_CHAIN)
        )
        chain = client.options.chain("AAPL", expiration="2026-06-20", option_type="call")
        assert route.called
        request = route.calls.last.request
        assert "expiration=2026-06-20" in str(request.url)
        assert "type=call" in str(request.url)


class TestOptionsExpirations:
    """Test available expirations."""

    def test_get_expirations(self, client: VecTrade, mock_api: respx.Router) -> None:
        """Fetches available expiration dates."""
        mock_response = {"data": ["2026-06-20", "2026-07-18", "2026-08-15"]}
        route = mock_api.get("/vq/options/AAPL/expirations").mock(
            return_value=httpx.Response(200, json=mock_response)
        )
        expirations = client.options.expirations("AAPL")
        assert route.called
        assert len(expirations) == 3
        assert expirations[0] == "2026-06-20"
