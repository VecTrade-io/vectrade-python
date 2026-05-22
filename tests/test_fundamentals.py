"""Tests for the fundamentals resource."""

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


class TestFundamentals:
    @respx.mock
    def test_get_fundamentals(self, client: VecTrade) -> None:
        respx.get(f"{BASE_URL}/vq/fundamentals/AAPL").respond(
            200,
            json={
                "ticker": "AAPL",
                "companyName": "Apple Inc.",
                "market": "NASDAQ",
                "market_cap": 3000000000000,
                "price": 195.0,
                "change": 2.5,
                "change_percent": 1.3,
                "volume": 50000000,
                "prevClose": 192.5,
                "high": 196.0,
                "low": 193.0,
                "open": 193.5,
                "max52": 200.0,
                "min52": 140.0,
            },
        )
        data = client.fundamentals.get("AAPL")
        assert data.symbol == "AAPL"
        assert data.company_name == "Apple Inc."
        assert data.market == "NASDAQ"
        assert data.market_cap == 3000000000000
        assert data.fifty_two_week_high == 200.0
        assert data.fifty_two_week_low == 140.0

    @respx.mock
    def test_income_statement(self, client: VecTrade) -> None:
        respx.get(f"{BASE_URL}/vq/fundamentals/AAPL/statements").respond(
            200,
            json={
                "ticker": "AAPL",
                "income_statement": {
                    "ticker": "AAPL",
                    "earnings": [
                        {
                            "period": "2025-09-30",
                            "Total Revenue": 400000000000,
                            "Net Income": 100000000000,
                            "Gross Profit": 180000000000,
                        }
                    ],
                },
            },
        )
        stmts = client.fundamentals.income_statement("AAPL")
        assert len(stmts) == 1
        assert stmts[0].total_revenue == 400000000000

    @respx.mock
    def test_balance_sheet(self, client: VecTrade) -> None:
        respx.get(f"{BASE_URL}/vq/fundamentals/AAPL/statements").respond(
            200,
            json={
                "ticker": "AAPL",
                "balance_sheet": {
                    "ticker": "AAPL",
                    "earnings": [
                        {
                            "period": "2025-09-30",
                            "Total Assets": 350000000000,
                            "Stockholders Equity": 60000000000,
                        }
                    ],
                },
            },
        )
        sheets = client.fundamentals.balance_sheet("AAPL")
        assert len(sheets) == 1
        assert sheets[0].total_assets == 350000000000
