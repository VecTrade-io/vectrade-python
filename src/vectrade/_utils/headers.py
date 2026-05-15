"""Header utilities for request/response processing."""

from __future__ import annotations

from dataclasses import dataclass


# Header constants — centralized to avoid hardcoding across modules
HEADER_API_KEY = "X-API-Key"
HEADER_AUTHORIZATION = "Authorization"
HEADER_USER_AGENT = "User-Agent"
HEADER_ACCEPT = "Accept"
HEADER_CONTENT_TYPE = "Content-Type"
HEADER_IDEMPOTENCY_KEY = "Idempotency-Key"
HEADER_REQUEST_ID = "X-Request-Id"

# Rate limit response headers
HEADER_RATELIMIT_LIMIT = "X-VQ-RateLimit-Limit"
HEADER_RATELIMIT_REMAINING = "X-VQ-RateLimit-Remaining"
HEADER_RATELIMIT_RESET = "X-VQ-RateLimit-Reset"

# Quota response headers
HEADER_QUOTA_LIMIT = "X-VQ-Quota-Limit"
HEADER_QUOTA_REMAINING = "X-VQ-Quota-Remaining"
HEADER_OVERAGE = "X-VQ-Overage"

# Retry header
HEADER_RETRY_AFTER = "Retry-After"


@dataclass(frozen=True)
class RateLimitInfo:
    """Parsed rate limit information from response headers."""

    limit: int | None
    remaining: int | None
    reset_timestamp: int | None

    @classmethod
    def from_headers(cls, headers: dict[str, str]) -> RateLimitInfo:
        """Parse rate limit info from response headers."""
        return cls(
            limit=_parse_int(headers.get(HEADER_RATELIMIT_LIMIT)),
            remaining=_parse_int(headers.get(HEADER_RATELIMIT_REMAINING)),
            reset_timestamp=_parse_int(headers.get(HEADER_RATELIMIT_RESET)),
        )


@dataclass(frozen=True)
class QuotaInfo:
    """Parsed quota information from response headers."""

    limit: int | None
    remaining: int | None
    is_overage: bool

    @classmethod
    def from_headers(cls, headers: dict[str, str]) -> QuotaInfo:
        """Parse quota info from response headers."""
        return cls(
            limit=_parse_int(headers.get(HEADER_QUOTA_LIMIT)),
            remaining=_parse_int(headers.get(HEADER_QUOTA_REMAINING)),
            is_overage=headers.get(HEADER_OVERAGE, "").lower() == "true",
        )


@dataclass(frozen=True)
class ResponseMetadata:
    """Metadata extracted from every API response."""

    request_id: str | None
    rate_limit: RateLimitInfo
    quota: QuotaInfo

    @classmethod
    def from_headers(cls, headers: dict[str, str]) -> ResponseMetadata:
        """Parse response metadata from headers."""
        return cls(
            request_id=headers.get(HEADER_REQUEST_ID),
            rate_limit=RateLimitInfo.from_headers(headers),
            quota=QuotaInfo.from_headers(headers),
        )


def _parse_int(value: str | None) -> int | None:
    """Safely parse an optional string to int."""
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None
