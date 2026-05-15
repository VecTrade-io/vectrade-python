"""Property-based tests using Hypothesis (§6.7 Testing Pyramid — fuzz testing)."""

from __future__ import annotations

from hypothesis import given, settings, assume
from hypothesis import strategies as st

from vectrade._utils.encoding import encode_path_param
from vectrade._utils.retry import (
    calculate_retry_delay,
    should_retry,
    RETRYABLE_STATUS_CODES,
    DEFAULT_MAX_DELAY,
)


# ---------- encode_path_param properties ----------

@given(st.text())
def test_encode_path_param_never_contains_raw_slash(value: str):
    """Encoded path params must never contain a raw '/' (path traversal)."""
    encoded = encode_path_param(value)
    assert "/" not in encoded


@given(st.text())
def test_encode_path_param_never_contains_raw_dot_dot(value: str):
    """Encoded path params must never allow '..' traversal."""
    encoded = encode_path_param(value)
    assert ".." not in encoded


@given(st.text(min_size=1))
def test_encode_path_param_non_empty_input_produces_non_empty_output(value: str):
    """Non-empty input always produces non-empty encoded output."""
    encoded = encode_path_param(value)
    assert len(encoded) > 0


@given(st.text())
def test_encode_path_param_idempotent_safety(value: str):
    """Double-encoding should not produce raw special chars."""
    encoded_once = encode_path_param(value)
    encoded_twice = encode_path_param(encoded_once)
    assert "/" not in encoded_twice
    assert ".." not in encoded_twice


# ---------- calculate_retry_delay properties ----------

@given(
    attempt=st.integers(min_value=0, max_value=20),
    initial_delay=st.floats(min_value=0.001, max_value=10.0),
    max_delay=st.floats(min_value=0.1, max_value=300.0),
    backoff_factor=st.floats(min_value=1.0, max_value=5.0),
)
def test_retry_delay_never_exceeds_max(
    attempt: int, initial_delay: float, max_delay: float, backoff_factor: float
):
    """Retry delay must never exceed max_delay regardless of attempt."""
    delay = calculate_retry_delay(
        attempt,
        initial_delay=initial_delay,
        max_delay=max_delay,
        backoff_factor=backoff_factor,
    )
    assert delay <= max_delay


@given(attempt=st.integers(min_value=0, max_value=20))
def test_retry_delay_always_positive(attempt: int):
    """Retry delay must always be positive."""
    delay = calculate_retry_delay(attempt)
    assert delay > 0


@given(
    attempt=st.integers(min_value=0, max_value=10),
    retry_after=st.floats(min_value=0.1, max_value=100.0),
)
def test_retry_after_header_takes_precedence(attempt: int, retry_after: float):
    """When retry_after is set, it should be used (capped by max_delay)."""
    delay = calculate_retry_delay(attempt, retry_after=retry_after)
    assert delay <= DEFAULT_MAX_DELAY
    assert delay == min(retry_after, DEFAULT_MAX_DELAY)


# ---------- should_retry properties ----------

@given(st.integers(min_value=200, max_value=399))
def test_success_codes_never_retried(status_code: int):
    """2xx/3xx status codes should never trigger a retry."""
    assert not should_retry(status_code)


@given(st.sampled_from(sorted(RETRYABLE_STATUS_CODES)))
def test_retryable_codes_always_retried(status_code: int):
    """Known retryable codes should always trigger retry."""
    assert should_retry(status_code)
