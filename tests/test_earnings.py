"""Tests for earnings resource using respx mocking."""

import httpx
import pytest
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

    @pytest.mark.parametrize("status", ["ok", "degraded"])
    def test_calendar_accepts_unwrapped_list(
        self, client: VecTrade, mock_api: respx.Router, status: str
    ) -> None:
        mock_api.get("/vq/earnings/calendar").mock(
            return_value=httpx.Response(200, json={"status": status, "data": [MOCK_CALENDAR_ENTRY]})
        )
        entries = client.earnings.calendar()
        assert len(entries) == 1
        assert entries[0].symbol == "TSLA"

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

    def test_calendar_parses_api_camel_case(self, client: VecTrade, mock_api: respx.Router) -> None:
        """Maps the camelCase fields served by the API."""
        mock_api.get("/vq/earnings/calendar").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        {
                            "symbol": "CSCO",
                            "companyName": "Cisco Systems, Inc.",
                            "date": "2026-11-12",
                            "time": "after_market",
                            "epsEstimate": 1.33,
                            "revenueEstimate": None,
                            "fiscalQuarter": "Q1 2027",
                        }
                    ]
                },
            )
        )
        entry = client.earnings.calendar()[0]
        assert entry.company_name == "Cisco Systems, Inc."
        assert entry.eps_estimate == 1.33
        assert entry.fiscal_quarter == "Q1 2027"

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
