"""VecTrade SDK exception hierarchy."""

from __future__ import annotations

from typing import Any


class VecTradeError(Exception):
    """Base exception for all VecTrade SDK errors."""

    def __init__(self, message: str, *, request_id: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.request_id = request_id


class ConfigurationError(VecTradeError):
    """Raised when the SDK is misconfigured (missing API key, invalid base URL)."""


class APIError(VecTradeError):
    """Raised when the API returns an error response."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        request_id: str | None = None,
        error_code: str | None = None,
        error_type: str | None = None,
        details: dict[str, Any] | None = None,
        docs_url: str | None = None,
    ) -> None:
        super().__init__(message, request_id=request_id)
        self.status_code = status_code
        self.error_code = error_code
        self.error_type = error_type
        self.details = details
        self.docs_url = docs_url


class AuthenticationError(APIError):
    """Raised when the API key is invalid or expired (HTTP 401/403)."""


class RateLimitError(APIError):
    """Raised when the rate limit is exceeded (HTTP 429)."""

    def __init__(
        self,
        message: str,
        *,
        retry_after: float | None = None,
        limit: int | None = None,
        remaining: int = 0,
        status_code: int = 429,
        **kwargs: object,
    ) -> None:
        super().__init__(message, status_code=status_code, **kwargs)  # type: ignore[arg-type]
        self.retry_after = retry_after
        self.limit = limit
        self.remaining = remaining


class QuotaExceededError(APIError):
    """Raised when the monthly/daily quota is exhausted (HTTP 402/403/429 with quota context)."""

    def __init__(
        self,
        message: str,
        *,
        quota_limit: int | None = None,
        quota_remaining: int | None = None,
        overage_policy: str | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(message, **kwargs)  # type: ignore[arg-type]
        self.quota_limit = quota_limit
        self.quota_remaining = quota_remaining
        self.overage_policy = overage_policy


class PaymentRequiredError(APIError):
    """Raised when the requested feature requires a paid plan (HTTP 402)."""


class NotFoundError(APIError):
    """Raised when the requested resource is not found (HTTP 404)."""


class ValidationError(APIError):
    """Raised when the request fails validation (HTTP 422)."""


class ServerError(APIError):
    """Raised when the server returns a 5xx error."""


class ServiceUnavailableError(ServerError):
    """Raised when the service is temporarily unavailable (HTTP 502/503)."""
