"""Tests for earnings resource using respx mocking."""

import httpx
import pytest
import respx

from vectrade import VecTrade


MOCK_EARNINGS_RESULT = {
    "symbol": "AAPL",
    "date": "2026-04-24",
    "fiscal_quarter": "Q2 2026",
    "eps_actual": 1.58,
    "eps_estimate": 1.52,
    "eps_surprise": 0.06,
    "eps_surprise_pct": 3.95,
    "revenue_actual": 95_400_000_000,
    "revenue_estimate": 94_200_000_000,
    "revenue_surprise_pct": 1.27,
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
        route = mock_api.get("/vq/earnings/AAPL/history").mock(
            return_value=httpx.Response(200, json={"data": [MOCK_EARNINGS_RESULT]})
        )
        history = client.earnings.history("AAPL")
        assert route.called
        assert len(history) == 1
        assert history[0].eps_actual == 1.58
        assert history[0].fiscal_quarter == "Q2 2026"

    def test_history_with_limit(self, client: VecTrade, mock_api: respx.Router) -> None:
        """Passes limit parameter."""
        route = mock_api.get("/vq/earnings/AAPL/history").mock(
            return_value=httpx.Response(200, json={"data": []})
        )
        client.earnings.history("AAPL", limit=4)
        assert route.called
        request = route.calls.last.request
        assert "limit=4" in str(request.url)


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
