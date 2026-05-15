"""Tests for insider resource using respx mocking."""

import httpx
import pytest
import respx

from vectrade import VecTrade


MOCK_TRANSACTION = {
    "symbol": "AAPL",
    "insider_name": "Tim Cook",
    "title": "CEO",
    "transaction_type": "sell",
    "shares": 50000,
    "price": 198.50,
    "total_value": 9_925_000.0,
    "shares_owned_after": 3_280_000,
    "filed_at": "2026-05-10T16:00:00Z",
}

MOCK_SUMMARY = {
    "symbol": "AAPL",
    "net_shares_30d": -150000,
    "net_value_30d": -29_750_000.0,
    "net_shares_90d": -320000,
    "net_value_90d": -63_200_000.0,
    "buy_count_90d": 2,
    "sell_count_90d": 8,
    "most_recent_transaction": MOCK_TRANSACTION,
}


class TestInsiderTransactions:
    """Test insider transactions retrieval."""

    def test_get_transactions(self, client: VecTrade, mock_api: respx.Router) -> None:
        """Fetches insider transactions."""
        route = mock_api.get("/vq/insider/AAPL/transactions").mock(
            return_value=httpx.Response(200, json={"data": [MOCK_TRANSACTION]})
        )
        transactions = client.insider.transactions("AAPL")
        assert route.called
        assert len(transactions) == 1
        assert transactions[0].insider_name == "Tim Cook"
        assert transactions[0].transaction_type == "sell"
        assert transactions[0].total_value == 9_925_000.0

    def test_transactions_with_limit(self, client: VecTrade, mock_api: respx.Router) -> None:
        """Passes limit parameter."""
        route = mock_api.get("/vq/insider/AAPL/transactions").mock(
            return_value=httpx.Response(200, json={"data": []})
        )
        client.insider.transactions("AAPL", limit=5)
        assert route.called
        request = route.calls.last.request
        assert "limit=5" in str(request.url)


class TestInsiderSummary:
    """Test insider summary retrieval."""

    def test_get_summary(self, client: VecTrade, mock_api: respx.Router) -> None:
        """Fetches insider trading summary."""
        route = mock_api.get("/vq/insider/AAPL/summary").mock(
            return_value=httpx.Response(200, json=MOCK_SUMMARY)
        )
        summary = client.insider.summary("AAPL")
        assert route.called
        assert summary.symbol == "AAPL"
        assert summary.net_shares_30d == -150000
        assert summary.buy_count_90d == 2
        assert summary.sell_count_90d == 8
        assert summary.most_recent_transaction is not None
        assert summary.most_recent_transaction.insider_name == "Tim Cook"
