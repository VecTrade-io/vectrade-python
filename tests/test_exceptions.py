"""Tests for exception hierarchy."""

from vectrade import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    NotFoundError,
    QuotaExceededError,
    RateLimitError,
    ServerError,
    ValidationError,
    VecTradeError,
)


class TestExceptionHierarchy:
    """Test that exception classes follow the correct inheritance chain."""

    def test_base_class(self) -> None:
        """VecTradeError is the base for all SDK exceptions."""
        exc = VecTradeError("test")
        assert isinstance(exc, Exception)
        assert str(exc) == "test"

    def test_configuration_error(self) -> None:
        """ConfigurationError inherits from VecTradeError."""
        exc = ConfigurationError("bad config")
        assert isinstance(exc, VecTradeError)

    def test_api_error(self) -> None:
        """APIError has status_code and request_id."""
        exc = APIError("not found", status_code=404, request_id="req_123")
        assert isinstance(exc, VecTradeError)
        assert exc.status_code == 404
        assert exc.request_id == "req_123"

    def test_authentication_error(self) -> None:
        """AuthenticationError is an APIError."""
        exc = AuthenticationError("invalid key", status_code=401)
        assert isinstance(exc, APIError)
        assert exc.status_code == 401

    def test_not_found_error(self) -> None:
        exc = NotFoundError("symbol not found", status_code=404)
        assert isinstance(exc, APIError)
        assert exc.status_code == 404

    def test_validation_error(self) -> None:
        exc = ValidationError("invalid params", status_code=422)
        assert isinstance(exc, APIError)

    def test_rate_limit_error(self) -> None:
        """RateLimitError carries retry metadata."""
        exc = RateLimitError(
            "too many requests",
            status_code=429,
            retry_after=2.5,
            limit=100,
            remaining=0,
        )
        assert isinstance(exc, APIError)
        assert exc.retry_after == 2.5
        assert exc.limit == 100
        assert exc.remaining == 0

    def test_quota_exceeded_error(self) -> None:
        exc = QuotaExceededError("monthly quota exceeded", status_code=429)
        assert isinstance(exc, APIError)

    def test_server_error(self) -> None:
        exc = ServerError("internal error", status_code=500)
        assert isinstance(exc, APIError)
        assert exc.status_code == 500

    def test_error_type_and_docs_url(self) -> None:
        """APIError carries error_type and docs_url."""
        exc = APIError(
            "bad request",
            status_code=400,
            error_type="invalid_request",
            docs_url="https://docs.vectrade.io/errors/invalid_request",
        )
        assert exc.error_type == "invalid_request"
        assert exc.docs_url == "https://docs.vectrade.io/errors/invalid_request"
