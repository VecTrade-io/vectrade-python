"""Tests for earnings resource using respx mocking."""

import httpx
import respx

from vectrade import VecTrade

MOCK_EARNINGS_RESULT = {
    "date": "2026-04-24",
    "eps_actual": 1.58,
    "eps_estimate": 1.52,
    "revenue_actual": 95_400_000_000,
    "revenue_estimate": 94_200_000_000,
}

MOCK_CALENDAR_ENTRY = {
    "symbol": "TSLA",
    "company_name": "Tesla, Inc.",
    "date": "2026-07-22",
    "time": "after_market",
    "eps_estimate": 0.73,
    "revenue_estimate": 26_500_000_000,
    "fiscal_quarter": "Q2 2026",
}


class TestEarningsHistory:
    """Test historical earnings retrieval."""

    def test_get_history(self, client: VecTrade, mock_api: respx.Router) -> None:
        """Fetches earnings history."""
        route = mock_api.get("/vq/earnings/AAPL").mock(
            return_value=httpx.Response(
                200, json={"ticker": "AAPL", "history": [MOCK_EARNINGS_RESULT]}
            )
        )
        history = client.earnings.history("AAPL")
        assert route.called
        assert len(history) == 1
        assert history[0].eps_actual == 1.58
        assert history[0].date == "2026-04-24"

    def test_history_with_limit(self, client: VecTrade, mock_api: respx.Router) -> None:
        """Respects limit parameter."""
        results = [MOCK_EARNINGS_RESULT] * 10
        route = mock_api.get("/vq/earnings/AAPL").mock(
            return_value=httpx.Response(200, json={"ticker": "AAPL", "history": results})
        )
        history = client.earnings.history("AAPL", limit=4)
        assert route.called
        assert len(history) == 4


class TestEarningsCalendar:
    """Test earnings calendar retrieval."""

    def test_get_calendar(self, client: VecTrade, mock_api: respx.Router) -> None:
        """Fetches upcoming earnings calendar."""
        route = mock_api.get("/vq/earnings/calendar").mock(
            return_value=httpx.Response(200, json={"data": [MOCK_CALENDAR_ENTRY]})
        )
        calendar = client.earnings.calendar()
        assert route.called
        assert len(calendar) == 1
        assert calendar[0].symbol == "TSLA"
        assert calendar[0].time == "after_market"

    def test_calendar_with_dates(self, client: VecTrade, mock_api: respx.Router) -> None:
        """Passes from/to date filters."""
        route = mock_api.get("/vq/earnings/calendar").mock(
            return_value=httpx.Response(200, json={"data": []})
        )
        client.earnings.calendar(from_date="2026-07-01", to_date="2026-07-31")
        assert route.called
        request = route.calls.last.request
        assert "from=2026-07-01" in str(request.url)
        assert "to=2026-07-31" in str(request.url)
