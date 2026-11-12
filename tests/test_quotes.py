"""Tests for quotes resource using respx mocking."""

import httpx
import pytest
import respx

from vectrade import VecTrade
from vectrade.types.quote import QuoteResponse

MOCK_QUOTE = {
    "symbol": "AAPL",
    "price": 198.50,
    "change": 2.30,
    "change_pct": 1.17,
    "volume": 45_000_000,
    "day_high": 199.20,
    "day_low": 196.10,
    "day_open": 196.80,
    "previous_close": 196.20,
    "market_cap": 3_100_000_000_000,
    "timestamp": "2026-05-15T16:00:00Z",
}

MOCK_BATCH = {
    "status": "ok",
    "data": {
        "AAPL": {**MOCK_QUOTE, "symbol": "AAPL"},
        "GOOGL": {**MOCK_QUOTE, "symbol": "GOOGL", "price": 178.30},
        "MSFT": {**MOCK_QUOTE, "symbol": "MSFT", "price": 445.60},
    },
}


class TestQuotesGet:
    """Test single quote retrieval."""

    @pytest.mark.parametrize("symbol", ["BTC-USD", "ETH-USD"])
    def test_crypto_quote_preserves_unavailable_values(
        self, client: VecTrade, mock_api: respx.Router, symbol: str
    ) -> None:
        payload = {
            "ticker": symbol,
            "price": 60000,
            "change_percent": 1.5,
            "volume": 1000,
            "high": 61000,
            "low": 59000,
            "open": 59500,
            "market": "crypto",
            "timestamp": "2026-11-12T12:00:00Z",
        }
        mock_api.get(f"/vq/quotes/{symbol}").mock(
            return_value=httpx.Response(200, json={"status": "ok", "data": payload})
        )
        quote = client.quotes.get(symbol)
        assert quote.symbol == symbol
        assert quote.change is None
        assert quote.previous_close is None
        assert quote.change_pct == 1.5
        assert quote.market == "crypto"

    def test_get_quote(self, client: VecTrade, mock_api: respx.Router) -> None:
        """Successfully fetches a single quote."""
        route = mock_api.get("/vq/quotes/AAPL").mock(
            return_value=httpx.Response(200, json=MOCK_QUOTE)
        )
        quote = client.quotes.get("AAPL")
        assert quote.symbol == "AAPL"
        assert quote.price == 198.50
        assert quote.change_pct == 1.17
        assert quote.volume == 45_000_000
        assert route.called

    def test_get_quote_with_fields(self, client: VecTrade, mock_api: respx.Router) -> None:
        """Fields parameter is passed as query param."""
        route = mock_api.get("/vq/quotes/AAPL").mock(
            return_value=httpx.Response(200, json=MOCK_QUOTE)
        )
        client.quotes.get("AAPL", fields=["price", "volume"])
        request = route.calls[0].request
        assert "fields" in str(request.url)

    def test_get_quote_returns_response_type(
        self, client: VecTrade, mock_api: respx.Router
    ) -> None:
        """Returns proper QuoteResponse type."""
        mock_api.get("/vq/quotes/AAPL").mock(return_value=httpx.Response(200, json=MOCK_QUOTE))
        quote = client.quotes.get("AAPL")
        assert isinstance(quote, QuoteResponse)


class TestQuotesBatch:
    """Test batch quote retrieval."""

    def test_batch_quotes(self, client: VecTrade, mock_api: respx.Router) -> None:
        """Successfully fetches multiple quotes."""
        mock_api.get("/vq/quotes/batch").mock(return_value=httpx.Response(200, json=MOCK_BATCH))
        quotes = client.quotes.batch(["AAPL", "GOOGL", "MSFT"])
        assert len(quotes) == 3
        assert quotes[0].symbol == "AAPL"
        assert quotes[1].symbol == "GOOGL"

    def test_batch_passes_tickers_param(self, client: VecTrade, mock_api: respx.Router) -> None:
        """The API accepts ticker symbols under the tickers query parameter."""
        route = mock_api.get("/vq/quotes/batch").mock(
            return_value=httpx.Response(200, json=MOCK_BATCH)
        )
        quotes = client.quotes.batch(["AAPL", "GOOGL", "MSFT"])
        request = route.calls[0].request
        assert request.url.params["tickers"] == "AAPL,GOOGL,MSFT"
        assert quotes[2].price == 445.60

    def test_batch_rejects_more_than_twenty_symbols(self, client: VecTrade) -> None:
        import pytest

        with pytest.raises(ValueError, match="1 and 20"):
            client.quotes.batch([f"TICKER{i}" for i in range(21)])


class TestQuotesPathEncoding:
    """Test URL path parameter encoding prevents path traversal."""

    def test_symbol_with_slash_is_encoded(self, client: VecTrade, mock_api: respx.Router) -> None:
        """Symbols containing slashes are URL-encoded, preventing traversal."""
        route = mock_api.get(url__regex=r"/vq/quotes/.*").mock(
            return_value=httpx.Response(200, json=MOCK_QUOTE)
        )
        client.quotes.get("../admin")
        request = route.calls[0].request
        url_path = (
            str(request.url.raw_path, "utf-8")
            if isinstance(request.url.raw_path, bytes)
            else str(request.url)
        )
        # The forward slash must be encoded (%2F) preventing path traversal
        assert "/../" not in url_path
        assert "%2F" in url_path or "%2f" in url_path

    def test_symbol_with_special_chars_is_encoded(
        self, client: VecTrade, mock_api: respx.Router
    ) -> None:
        """Symbols with special chars are safely encoded."""
        route = mock_api.get(url__regex=r"/vq/quotes/.*").mock(
            return_value=httpx.Response(200, json=MOCK_QUOTE)
        )
        client.quotes.get("AAPL%00../../secret")
        request = route.calls[0].request
        url_path = (
            str(request.url.raw_path, "utf-8")
            if isinstance(request.url.raw_path, bytes)
            else str(request.url)
        )
        # Null byte and traversal must be encoded
        assert "%00" not in url_path or "%2500" in url_path
