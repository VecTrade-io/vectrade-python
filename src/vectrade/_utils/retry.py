"""Retry logic with exponential backoff and jitter."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import httpx

# Status codes that trigger automatic retry
RETRYABLE_STATUS_CODES = frozenset({429, 500, 502, 503, 504})

# Default retry configuration
DEFAULT_MAX_RETRIES = 3
DEFAULT_INITIAL_DELAY = 0.5  # seconds
DEFAULT_MAX_DELAY = 30.0  # seconds
DEFAULT_BACKOFF_FACTOR = 2.0


def calculate_retry_delay(
    attempt: int,
    *,
    initial_delay: float = DEFAULT_INITIAL_DELAY,
    max_delay: float = DEFAULT_MAX_DELAY,
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    retry_after: float | None = None,
) -> float:
    """Calculate delay before next retry with exponential backoff and jitter.

    Args:
        attempt: Zero-indexed retry attempt number.
        initial_delay: Base delay in seconds.
        max_delay: Maximum delay cap in seconds.
        backoff_factor: Multiplier for exponential growth.
        retry_after: Server-specified retry-after value (takes precedence).

    Returns:
        Delay in seconds before next attempt.
    """
    if retry_after is not None and retry_after > 0:
        return min(retry_after, max_delay)

    # Exponential backoff: initial_delay * backoff_factor^attempt
    delay = initial_delay * (backoff_factor**attempt)

    # Add jitter (±25%) to prevent thundering herd
    jitter = delay * 0.25 * (2 * random.random() - 1)
    delay += jitter

    return min(delay, max_delay)


def should_retry(status_code: int) -> bool:
    """Determine if a response status code is retryable."""
    return status_code in RETRYABLE_STATUS_CODES


def get_retry_after_header(response: httpx.Response) -> float | None:
    """Extract Retry-After value from response headers.

    Handles both integer seconds and HTTP-date formats.
    """
    retry_after = response.headers.get("retry-after")
    if retry_after is None:
        return None

    try:
        return float(retry_after)
    except ValueError:
        return None
