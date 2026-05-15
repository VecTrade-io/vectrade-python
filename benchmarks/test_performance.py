"""Performance benchmarks for the Python SDK."""

import os

import pytest

from benchmarks.conftest import LATENCY_BUDGETS


@pytest.fixture(autouse=True)
def _set_api_key(monkeypatch):
    monkeypatch.setenv("VECTRADE_API_KEY", "vt_bench_key_placeholder")


class TestClientInit:
    """Benchmark client initialization."""

    def test_sync_client_init(self, benchmark) -> None:
        from vectrade import VecTrade

        def create_client():
            c = VecTrade()
            c.close()

        result = benchmark(create_client)
        # Assert latency budget
        assert benchmark.stats["mean"] * 1000 < LATENCY_BUDGETS["client_init"]

    def test_async_client_init(self, benchmark) -> None:
        from vectrade import AsyncVecTrade

        def create_client():
            _ = AsyncVecTrade()

        benchmark(create_client)


class TestRetryCalculation:
    """Benchmark retry delay computation."""

    def test_retry_delay(self, benchmark) -> None:
        from vectrade._utils.retry import calculate_retry_delay

        def calc():
            for attempt in range(5):
                calculate_retry_delay(attempt)

        result = benchmark(calc)
        assert benchmark.stats["mean"] * 1000 < LATENCY_BUDGETS["retry_delay_calc"]


class TestSSEParsing:
    """Benchmark SSE stream parsing."""

    def test_parse_sse_chunk(self, benchmark) -> None:
        from vectrade._streaming import _parse_sse_line

        line = 'data: {"type":"chunk","content":"Analysis shows positive momentum"}'

        result = benchmark(_parse_sse_line, line)
