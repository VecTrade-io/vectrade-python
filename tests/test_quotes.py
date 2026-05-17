"""Tests for quotes resource using respx mocking."""

import httpx
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
    "data": [
        {**MOCK_QUOTE, "symbol": "AAPL"},
        {**MOCK_QUOTE, "symbol": "GOOGL", "price": 178.30},
        {**MOCK_QUOTE, "symbol": "MSFT", "price": 445.60},
    ]
}


class TestQuotesGet:
    """Test single quote retrieval."""

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

    def test_batch_passes_symbols_param(self, client: VecTrade, mock_api: respx.Router) -> None:
        """Symbols are comma-joined in query params."""
        route = mock_api.get("/vq/quotes/batch").mock(
            return_value=httpx.Response(200, json=MOCK_BATCH)
        )
        quotes = client.quotes.batch(["AAPL", "GOOGL", "MSFT"])
        request = route.calls[0].request
        assert "symbols" in str(request.url)
        assert quotes[2].price == 445.60


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
