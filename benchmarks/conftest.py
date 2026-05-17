"""Benchmark configuration for the Python SDK.

Uses pytest-benchmark for performance regression testing.
Run: pytest benchmarks/ --benchmark-only --benchmark-json=results.json
"""

import pytest

# Minimum samples for statistically significant results
BENCHMARK_ROUNDS = 100
BENCHMARK_WARMUP_ROUNDS = 5


@pytest.fixture
def benchmark_config():
    """Shared benchmark config."""
    return {
        "min_rounds": BENCHMARK_ROUNDS,
        "warmup": True,
        "warmup_iterations": BENCHMARK_WARMUP_ROUNDS,
    }


# Latency budgets (in milliseconds)
LATENCY_BUDGETS = {
    "client_init": 5.0,  # Client construction
    "request_overhead": 1.0,  # SDK overhead per request (excluding network)
    "json_parse_small": 0.5,  # Parse a small JSON response (<1KB)
    "json_parse_large": 5.0,  # Parse a large JSON response (>100KB)
    "retry_delay_calc": 0.01,  # Retry delay calculation
    "middleware_stack": 0.5,  # Full middleware stack overhead
    "pagination_iter": 1.0,  # Per-page iteration overhead
    "sse_parse_chunk": 0.1,  # Parse a single SSE chunk
}
