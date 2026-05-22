"""Additional sync resource tests to fill remaining coverage gaps."""

import respx
import pytest
from httpx import Response

from vectrade import VecTrade

BASE_URL = "https://api.vectrade.io/v1"


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("VECTRADE_API_KEY", "vq_test_abcdefghijklmnop1234")
    c = VecTrade(max_retries=0)
    yield c
    c.close()


class TestDeveloperSyncExtras:
    """Test sync developer methods that previously had no coverage."""

    @respx.mock
    def test_get_daily_usage(self, client) -> None:
        respx.get(f"{BASE_URL}/vq/developer/usage/daily").respond(
            200,
            json=[
                {"date": "2026-05-21", "requests": 150, "errors": 2},
                {"date": "2026-05-20", "requests": 200, "errors": 0},
            ],
        )
        daily = client.developer.get_daily_usage(days=7)
        assert len(daily) == 2
        assert daily[0]["requests"] == 150

    @respx.mock
    def test_get_plan(self, client) -> None:
        respx.get(f"{BASE_URL}/vq/developer/plan").respond(
            200,
            json={
                "plan_id": "professional",
                "plan_name": "Professional",
                "status": "ACTIVE",
                "current_period_start": "2026-05-01",
                "current_period_end": "2026-06-01",
                "features": ["ai", "webhooks", "screener"],
            },
        )
        plan = client.developer.get_plan()
        assert plan["plan_id"] == "professional"
        assert plan["status"] == "ACTIVE"

    @respx.mock
    def test_get_quota(self, client) -> None:
        respx.get(f"{BASE_URL}/vq/developer/quota").respond(
            200,
            json={
                "plan_id": "professional",
                "monthly_quota": 500000,
                "used": 1500,
                "remaining": 498500,
                "overage_policy": "THROTTLE",
                "reset_at": "2026-06-01T00:00:00Z",
            },
        )
        quota = client.developer.get_quota()
        assert quota["monthly_quota"] == 500000
        assert quota["remaining"] == 498500


class TestEarningsSyncExtras:
    """Test sync earnings calendar."""

    @respx.mock
    def test_calendar(self, client) -> None:
        respx.get(f"{BASE_URL}/vq/earnings/calendar").respond(
            200,
            json={
                "data": [
                    {
                        "symbol": "NVDA",
                        "date": "2026-05-28",
                        "time": "after_close",
                        "eps_estimate": 0.82,
                    },
                    {
                        "symbol": "CRM",
                        "date": "2026-05-29",
                        "time": "before_open",
                        "eps_estimate": 2.35,
                    },
                ]
            },
        )
        entries = client.earnings.calendar(from_date="2026-05-22", to_date="2026-05-30")
        assert len(entries) == 2
        assert entries[0].symbol == "NVDA"
        assert entries[1].symbol == "CRM"

    @respx.mock
    def test_calendar_empty(self, client) -> None:
        respx.get(f"{BASE_URL}/vq/earnings/calendar").respond(
            200, json={"data": []}
        )
        entries = client.earnings.calendar(from_date="2026-12-25", to_date="2026-12-26")
        assert entries == []


class TestOptionsSyncExtras:
    """Test sync options expirations."""

    @respx.mock
    def test_expirations(self, client) -> None:
        respx.get(f"{BASE_URL}/vq/options/AAPL/expirations").respond(
            200,
            json={"expirations": ["2026-06-20", "2026-07-18", "2026-08-15", "2026-09-19"]},
        )
        dates = client.options.expirations("AAPL")
        assert len(dates) == 4
        assert "2026-06-20" in dates
        assert "2026-09-19" in dates


class TestScreenerSyncExtras:
    """Test screener with various filter combinations."""

    @respx.mock
    def test_run_with_all_filters(self, client) -> None:
        respx.post(f"{BASE_URL}/vq/screener/filter").respond(
            200,
            json={
                "data": [
                    {
                        "symbol": "AAPL",
                        "company_name": "Apple Inc.",
                        "price": 195.0,
                        "change_pct": 1.3,
                        "market_cap": 3e12,
                    }
                ],
                "page_info": {"has_next": False, "cursor": None, "total": 1},
            },
        )
        results = list(
            client.screener.run(
                market_cap_min=1e12,
                market_cap_max=5e12,
                pe_min=10.0,
                pe_max=50.0,
                dividend_yield_min=0.001,
                sector="Technology",
                limit=20,
            )
        )
        assert len(results) == 1
        assert results[0].symbol == "AAPL"

    @respx.mock
    def test_run_paginated(self, client) -> None:
        """Test that pagination works when there are multiple pages."""
        respx.post(f"{BASE_URL}/vq/screener/filter").mock(
            side_effect=[
                Response(
                    200,
                    json={
                        "data": [
                            {
                                "symbol": "AAPL",
                                "company_name": "Apple Inc.",
                                "price": 195.0,
                                "change_pct": 1.3,
                                "market_cap": 3e12,
                            }
                        ],
                        "page_info": {
                            "has_next": True,
                            "cursor": "cursor_abc",
                            "total": 2,
                        },
                    },
                ),
                Response(
                    200,
                    json={
                        "data": [
                            {
                                "symbol": "MSFT",
                                "company_name": "Microsoft Corp.",
                                "price": 420.0,
                                "change_pct": 0.5,
                                "market_cap": 3.1e12,
                            }
                        ],
                        "page_info": {
                            "has_next": False,
                            "cursor": None,
                            "total": 2,
                        },
                    },
                ),
            ]
        )
        results = list(client.screener.run(market_cap_min=1e12))
        assert len(results) == 2
        symbols = [r.symbol for r in results]
        assert "AAPL" in symbols
        assert "MSFT" in symbols

    @respx.mock
    def test_run_empty_results(self, client) -> None:
        respx.post(f"{BASE_URL}/vq/screener/filter").respond(
            200,
            json={
                "data": [],
                "page_info": {"has_next": False, "cursor": None, "total": 0},
            },
        )
        results = list(client.screener.run(sector="NonExistent"))
        assert results == []
