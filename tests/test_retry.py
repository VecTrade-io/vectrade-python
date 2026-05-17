"""Tests for retry logic and delay calculation."""

import pytest

from vectrade._utils.retry import (
    calculate_retry_delay,
    should_retry,
)


class TestShouldRetry:
    """Test retry eligibility determination."""

    @pytest.mark.parametrize("status_code", [429, 500, 502, 503, 504])
    def test_retryable_status_codes(self, status_code: int) -> None:
        """Known retryable status codes return True."""
        assert should_retry(status_code) is True

    @pytest.mark.parametrize("status_code", [200, 201, 400, 401, 403, 404, 422])
    def test_non_retryable_status_codes(self, status_code: int) -> None:
        """Non-retryable status codes return False."""
        assert should_retry(status_code) is False


class TestCalculateRetryDelay:
    """Test exponential backoff delay calculation."""

    def test_first_attempt_uses_initial_delay(self) -> None:
        """First retry uses approximately the initial delay."""
        delay = calculate_retry_delay(0, initial_delay=1.0)
        # With ±25% jitter, delay should be between 0.75 and 1.25
        assert 0.5 <= delay <= 1.5

    def test_exponential_growth(self) -> None:
        """Delay grows exponentially with attempts."""
        delays = [calculate_retry_delay(i, initial_delay=1.0, backoff_factor=2.0) for i in range(5)]
        # Each delay should generally be larger than the previous (ignoring jitter)
        # Test the median tendency
        assert delays[2] > delays[0]  # 4x vs 1x base

    def test_respects_max_delay(self) -> None:
        """Delay never exceeds max_delay."""
        delay = calculate_retry_delay(100, initial_delay=1.0, max_delay=30.0)
        assert delay <= 30.0

    def test_retry_after_takes_precedence(self) -> None:
        """Server Retry-After value takes precedence over calculation."""
        delay = calculate_retry_delay(0, retry_after=5.0)
        assert delay == 5.0

    def test_retry_after_capped_by_max_delay(self) -> None:
        """Retry-After is still capped by max_delay."""
        delay = calculate_retry_delay(0, retry_after=100.0, max_delay=30.0)
        assert delay == 30.0

    def test_retry_after_zero_uses_calculation(self) -> None:
        """Retry-After of 0 falls through to normal calculation."""
        delay = calculate_retry_delay(0, retry_after=0.0, initial_delay=1.0)
        # retry_after=0 → not > 0, so calculation is used
        assert delay > 0
