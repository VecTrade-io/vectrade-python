"""Tests for the screener resource."""

import pytest
import respx

from vectrade import VecTrade

BASE_URL = "https://api.vectrade.io/v1"


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> VecTrade:
    monkeypatch.setenv("VECTRADE_API_KEY", "vq_test_abcdefghijklmnop1234")
    c = VecTrade(max_retries=0)
    yield c
    c.close()


class TestScreener:
    @respx.mock
    def test_run_returns_paginator(self, client: VecTrade) -> None:
        respx.get(f"{BASE_URL}/vq/screener").respond(
            200,
            json={
                "data": [
                    {
                        "symbol": "AAPL",
                        "company_name": "Apple Inc.",
                        "price": 195.0,
                        "change_pct": 1.3,
                        "market_cap": 3e12,
                    },
                    {
                        "symbol": "MSFT",
                        "company_name": "Microsoft Corp.",
                        "price": 420.0,
                        "change_pct": 0.8,
                        "market_cap": 2.8e12,
                    },
                ],
                "page_info": {"has_next": False, "cursor": None, "total": 2},
            },
        )
        results = list(client.screener.run(sector="Technology", limit=10))
        assert len(results) == 2
        assert results[0].symbol == "AAPL"

    @respx.mock
    def test_run_paginates(self, client: VecTrade) -> None:
        # Page 1
        respx.get(f"{BASE_URL}/vq/screener").mock(
            side_effect=[
                respx.MockResponse(
                    200,
                    json={
                        "data": [
                            {
                                "symbol": "AAPL",
                                "company_name": "Apple",
                                "price": 195.0,
                                "change_pct": 1.3,
                                "market_cap": 3e12,
                            }
                        ],
                        "page_info": {"has_next": True, "cursor": "c1", "total": 2},
                    },
                ),
                respx.MockResponse(
                    200,
                    json={
                        "data": [
                            {
                                "symbol": "MSFT",
                                "company_name": "Microsoft",
                                "price": 420.0,
                                "change_pct": 0.8,
                                "market_cap": 2.8e12,
                            }
                        ],
                        "page_info": {"has_next": False, "cursor": None, "total": 2},
                    },
                ),
            ]
        )
        results = list(client.screener.run(limit=1))
        assert len(results) == 2
        assert results[0].symbol == "AAPL"
        assert results[1].symbol == "MSFT"
