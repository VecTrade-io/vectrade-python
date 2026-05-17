"""Tests for the AI streaming resource."""

import json

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


class TestAI:
    @respx.mock
    def test_stream_analysis(self, client: VecTrade) -> None:
        sse_lines = "\n".join(
            [
                f"data: {json.dumps({'content': 'Apple ', 'type': 'text'})}",
                f"data: {json.dumps({'content': 'looks bullish.', 'type': 'text'})}",
                f"data: {json.dumps({'type': 'done'})}",
            ]
        )
        respx.post(f"{BASE_URL}/vq/ai/analyze").respond(
            200,
            text=sse_lines,
            headers={"content-type": "text/event-stream"},
        )
        chunks = list(client.ai.stream("Analyze AAPL"))
        assert len(chunks) == 2
        assert chunks[0].text == "Apple "
        assert chunks[1].text == "looks bullish."
