"""Tests for the technicals resource."""

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


class TestTechnicals:
    @respx.mock
    def test_get_technical_indicators(self, client: VecTrade) -> None:
        respx.get(f"{BASE_URL}/vq/technical/AAPL").respond(
            200,
            json={
                "ticker": "AAPL",
                "technical_score": 72,
                "rsi_14": 55.3,
                "macd": {"value": 1.5, "signal": 1.2, "histogram": 0.3},
                "bollinger_bands": {"upper": 200, "middle": 195, "lower": 190},
                "moving_averages": {"sma_50": 190, "sma_200": 180},
                "indicators": {"adx": 25.0},
                "summary": {"recommendation": "buy"},
            },
        )
        data = client.technicals.get("AAPL")
        assert data.symbol == "AAPL"
        assert data.technical_score == 72
        assert data.rsi_14 == 55.3
        assert data.macd is not None
        assert data.macd["value"] == 1.5

    @respx.mock
    def test_get_with_params(self, client: VecTrade) -> None:
        route = respx.get(f"{BASE_URL}/vq/technical/MSFT").respond(
            200,
            json={"ticker": "MSFT", "rsi_14": 60.0},
        )
        client.technicals.get("MSFT", indicators=["rsi", "macd"], interval="1h", period=100)
        assert route.called
        req = route.calls.last.request
        assert "indicators=rsi%2Cmacd" in str(req.url) or "indicators=rsi,macd" in str(req.url)
