"""Tests for insider resource using respx mocking."""

import httpx
import respx

from vectrade import VecTrade

MOCK_TRANSACTION = {
    "insider": "Tim Cook",
    "position": "CEO",
    "transaction_type": "sell",
    "shares": 50000,
    "value": 9_925_000.0,
    "transaction_date": "2026-05-10",
    "ownership": "D",
    "description": "Sale at price 198.50 per share.",
}

MOCK_INSIDER_RESPONSE = {
    "ticker": "AAPL",
    "trades": [MOCK_TRANSACTION],
    "buy_count": 2,
    "sell_count": 8,
    "exercise_count": 0,
    "buy_volume": 10000,
    "sell_volume": 150000,
    "net_trades": -6,
    "count": 10,
}


class TestInsiderTransactions:
    """Test insider transactions retrieval."""

    def test_get_transactions(self, client: VecTrade, mock_api: respx.Router) -> None:
        """Fetches insider transactions."""
        route = mock_api.get("/vq/insider/AAPL").mock(
            return_value=httpx.Response(200, json=MOCK_INSIDER_RESPONSE)
        )
        transactions = client.insider.transactions("AAPL")
        assert route.called
        assert len(transactions) == 1
        assert transactions[0].insider_name == "Tim Cook"
        assert transactions[0].transaction_type == "sell"
        assert transactions[0].total_value == 9_925_000.0

    def test_transactions_with_limit(self, client: VecTrade, mock_api: respx.Router) -> None:
        """Respects limit parameter."""
        trades = [MOCK_TRANSACTION] * 10
        response = {**MOCK_INSIDER_RESPONSE, "trades": trades}
        route = mock_api.get("/vq/insider/AAPL").mock(
            return_value=httpx.Response(200, json=response)
        )
        transactions = client.insider.transactions("AAPL", limit=5)
        assert route.called
        assert len(transactions) == 5


class TestInsiderSummary:
    """Test insider summary retrieval."""

    def test_get_summary(self, client: VecTrade, mock_api: respx.Router) -> None:
        """Fetches insider trading summary."""
        route = mock_api.get("/vq/insider/AAPL").mock(
            return_value=httpx.Response(200, json=MOCK_INSIDER_RESPONSE)
        )
        summary = client.insider.summary("AAPL")
        assert route.called
        assert summary.symbol == "AAPL"
        assert summary.buy_count == 2
        assert summary.sell_count == 8
        assert summary.net_trades == -6
