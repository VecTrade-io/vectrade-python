"""VecTrade Python SDK — Official client for the VecTrade financial data and AI platform."""

from vectrade._client import AsyncVecTrade, VecTrade
from vectrade._exceptions import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    NotFoundError,
    PaymentRequiredError,
    QuotaExceededError,
    RateLimitError,
    ServerError,
    ServiceUnavailableError,
    ValidationError,
    VecTradeError,
)
from vectrade._version import __version__

__all__ = [
    "APIError",
    "AsyncVecTrade",
    "AuthenticationError",
    "ConfigurationError",
    "NotFoundError",
    "PaymentRequiredError",
    "QuotaExceededError",
    "RateLimitError",
    "ServerError",
    "ServiceUnavailableError",
    "ValidationError",
    "VecTrade",
    "VecTradeError",
    "__version__",
]
