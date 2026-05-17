"""Tests for HTTP error → exception mapping and request retry behavior."""

import httpx
import pytest
import respx

from vectrade import VecTrade
from vectrade._exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    PaymentRequiredError,
    QuotaExceededError,
    RateLimitError,
    ServerError,
    ServiceUnavailableError,
    ValidationError,
)

BASE_URL = "https://api.vectrade.io/v1"


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> VecTrade:
    monkeypatch.setenv("VECTRADE_API_KEY", "vq_test_abcdefghijklmnop1234")
    c = VecTrade(max_retries=0)
    yield c
    c.close()


class TestErrorStatusMapping:
    """Verify _raise_for_status maps HTTP codes to the correct exception types."""

    @respx.mock
    def test_401_raises_authentication_error(self, client: VecTrade) -> None:
        respx.get(f"{BASE_URL}/vq/quotes/AAPL").respond(
            401,
            json={"error": {"message": "Invalid API key", "type": "auth_error"}},
            headers={"x-request-id": "req_abc"},
        )
        with pytest.raises(AuthenticationError, match="Invalid API key") as exc_info:
            client.request("GET", "/vq/quotes/AAPL")
        assert exc_info.value.status_code == 401
        assert exc_info.value.request_id == "req_abc"

    @respx.mock
    def test_403_raises_authentication_error(self, client: VecTrade) -> None:
        respx.get(f"{BASE_URL}/vq/quotes/AAPL").respond(403, json={"error": {"message": "Forbidden"}})
        with pytest.raises(AuthenticationError):
            client.request("GET", "/vq/quotes/AAPL")

    @respx.mock
    def test_404_raises_not_found_error(self, client: VecTrade) -> None:
        respx.get(f"{BASE_URL}/vq/quotes/INVALID").respond(
            404,
            json={"error": {"message": "Symbol not found", "type": "not_found"}},
            headers={"x-request-id": "req_404"},
        )
        with pytest.raises(NotFoundError, match="Symbol not found") as exc_info:
            client.request("GET", "/vq/quotes/INVALID")
        assert exc_info.value.status_code == 404

    @respx.mock
    def test_422_raises_validation_error(self, client: VecTrade) -> None:
        respx.post(f"{BASE_URL}/vq/screener").respond(
            422,
            json={"error": {"message": "Invalid filter: pe_ratio", "type": "validation_error"}},
        )
        with pytest.raises(ValidationError, match="Invalid filter"):
            client.request("POST", "/vq/screener", json={"filters": {}})

    @respx.mock
    def test_429_raises_rate_limit_error(self, client: VecTrade) -> None:
        respx.get(f"{BASE_URL}/vq/quotes/AAPL").respond(
            429,
            json={"error": {"message": "Rate limit exceeded", "type": "rate_limit"}},
            headers={
                "Retry-After": "5",
                "X-VQ-RateLimit-Limit": "100",
            },
        )
        with pytest.raises(RateLimitError, match="Rate limit exceeded") as exc_info:
            client.request("GET", "/vq/quotes/AAPL")
        assert exc_info.value.status_code == 429
        assert exc_info.value.remaining == 0

    @respx.mock
    def test_429_quota_exceeded_raises_quota_error(self, client: VecTrade) -> None:
        respx.get(f"{BASE_URL}/vq/quotes/AAPL").respond(
            429,
            json={"error": {"message": "Monthly quota exhausted", "type": "quota_exceeded"}},
        )
        with pytest.raises(QuotaExceededError, match="Monthly quota"):
            client.request("GET", "/vq/quotes/AAPL")

    @respx.mock
    def test_500_raises_server_error(self, client: VecTrade) -> None:
        respx.get(f"{BASE_URL}/vq/quotes/AAPL").respond(500, text="Internal Server Error")
        with pytest.raises(ServerError):
            client.request("GET", "/vq/quotes/AAPL")

    @respx.mock
    def test_503_raises_server_error(self, client: VecTrade) -> None:
        respx.get(f"{BASE_URL}/vq/quotes/AAPL").respond(503, text="Service Unavailable")
        with pytest.raises(ServerError):
            client.request("GET", "/vq/quotes/AAPL")

    @respx.mock
    def test_unknown_4xx_raises_api_error(self, client: VecTrade) -> None:
        respx.get(f"{BASE_URL}/vq/quotes/AAPL").respond(418, text="I'm a teapot")
        with pytest.raises(APIError) as exc_info:
            client.request("GET", "/vq/quotes/AAPL")
        assert exc_info.value.status_code == 418

    @respx.mock
    def test_error_preserves_request_id(self, client: VecTrade) -> None:
        respx.get(f"{BASE_URL}/vq/quotes/AAPL").respond(
            500,
            json={"error": {"message": "fail"}},
            headers={"x-request-id": "req_xyz_123"},
        )
        with pytest.raises(ServerError) as exc_info:
            client.request("GET", "/vq/quotes/AAPL")
        assert exc_info.value.request_id == "req_xyz_123"

    @respx.mock
    def test_error_preserves_error_type_and_docs_url(self, client: VecTrade) -> None:
        respx.get(f"{BASE_URL}/vq/quotes/AAPL").respond(
            404,
            json={"error": {"message": "Not found", "type": "not_found", "docs_url": "https://docs.vectrade.io/errors#not-found"}},
        )
        with pytest.raises(NotFoundError) as exc_info:
            client.request("GET", "/vq/quotes/AAPL")
        assert exc_info.value.error_type == "not_found"
        assert exc_info.value.docs_url == "https://docs.vectrade.io/errors#not-found"


class TestRequestRetry:
    """Test retry behavior on transient failures."""

    @respx.mock
    def test_retries_on_429_then_succeeds(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("VECTRADE_API_KEY", "vq_test_abcdefghijklmnop1234")
        client = VecTrade(max_retries=2)

        route = respx.get(f"{BASE_URL}/vq/quotes/AAPL")
        route.side_effect = [
            httpx.Response(429, json={"error": {"message": "rate limited"}}),
            httpx.Response(200, json={"symbol": "AAPL", "price": 195.0}),
        ]

        response = client.request("GET", "/vq/quotes/AAPL")
        assert response.status_code == 200
        assert route.call_count == 2
        client.close()

    @respx.mock
    def test_retries_on_500_then_succeeds(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("VECTRADE_API_KEY", "vq_test_abcdefghijklmnop1234")
        client = VecTrade(max_retries=2)

        route = respx.get(f"{BASE_URL}/vq/quotes/AAPL")
        route.side_effect = [
            httpx.Response(500, text="Server Error"),
            httpx.Response(200, json={"symbol": "AAPL", "price": 195.0}),
        ]

        response = client.request("GET", "/vq/quotes/AAPL")
        assert response.status_code == 200
        assert route.call_count == 2
        client.close()

    @respx.mock
    def test_no_retry_on_404(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("VECTRADE_API_KEY", "vq_test_abcdefghijklmnop1234")
        client = VecTrade(max_retries=3)

        route = respx.get(f"{BASE_URL}/vq/quotes/INVALID")
        route.respond(404, json={"error": {"message": "Not found"}})

        with pytest.raises(NotFoundError):
            client.request("GET", "/vq/quotes/INVALID")
        assert route.call_count == 1
        client.close()

    @respx.mock
    def test_exhausted_retries_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("VECTRADE_API_KEY", "vq_test_abcdefghijklmnop1234")
        client = VecTrade(max_retries=1)

        route = respx.get(f"{BASE_URL}/vq/quotes/AAPL")
        route.side_effect = [
            httpx.Response(500, text="Error 1"),
            httpx.Response(500, text="Error 2"),
        ]

        with pytest.raises(ServerError):
            client.request("GET", "/vq/quotes/AAPL")
        assert route.call_count == 2
        client.close()


class TestFinanceCoreErrorFormat:
    """Test error parsing with the actual finance core JSON format.

    Finance returns: {"error_code": "AUTH_001", "message": "...", "details": {...}, "request_id": "..."}
    """

    @respx.mock
    def test_finance_format_401_auth(self, client: VecTrade) -> None:
        respx.get(f"{BASE_URL}/vq/quotes/AAPL").respond(
            401,
            json={
                "error_code": "AUTH_001",
                "message": "Invalid or expired credentials",
                "details": None,
                "request_id": "req_fin_001",
            },
        )
        with pytest.raises(AuthenticationError) as exc_info:
            client.request("GET", "/vq/quotes/AAPL")
        assert exc_info.value.error_code == "AUTH_001"
        assert "Invalid or expired" in str(exc_info.value)

    @respx.mock
    def test_finance_format_402_payment(self, client: VecTrade) -> None:
        respx.get(f"{BASE_URL}/vq/ai/analyze").respond(
            402,
            json={
                "error_code": "PAY_001",
                "message": "Payment required",
                "details": None,
            },
        )
        with pytest.raises(PaymentRequiredError) as exc_info:
            client.request("GET", "/vq/ai/analyze")
        assert exc_info.value.status_code == 402
        assert exc_info.value.error_code == "PAY_001"

    @respx.mock
    def test_finance_format_403_quota_exceeded(self, client: VecTrade) -> None:
        """Finance sends AUTH_002 with 'quota exceeded' in message for BLOCK policy."""
        respx.get(f"{BASE_URL}/vq/quotes/AAPL").respond(
            403,
            json={
                "error_code": "AUTH_002",
                "message": "Monthly quota exceeded (10000 calls). Upgrade your plan or wait for the next billing period.",
                "details": None,
            },
        )
        with pytest.raises(QuotaExceededError) as exc_info:
            client.request("GET", "/vq/quotes/AAPL")
        assert exc_info.value.status_code == 403
        assert exc_info.value.overage_policy == "BLOCK"

    @respx.mock
    def test_finance_format_403_forbidden_not_quota(self, client: VecTrade) -> None:
        """403 without 'quota' in message should raise AuthenticationError."""
        respx.get(f"{BASE_URL}/vq/quotes/AAPL").respond(
            403,
            json={
                "error_code": "AUTH_002",
                "message": "Insufficient permissions",
                "details": None,
            },
        )
        with pytest.raises(AuthenticationError):
            client.request("GET", "/vq/quotes/AAPL")

    @respx.mock
    def test_finance_format_404_not_found(self, client: VecTrade) -> None:
        respx.get(f"{BASE_URL}/vq/quotes/INVALID").respond(
            404,
            json={
                "error_code": "RES_001",
                "message": "Symbol not found",
                "details": None,
            },
        )
        with pytest.raises(NotFoundError) as exc_info:
            client.request("GET", "/vq/quotes/INVALID")
        assert exc_info.value.error_code == "RES_001"

    @respx.mock
    def test_finance_format_422_validation(self, client: VecTrade) -> None:
        respx.post(f"{BASE_URL}/vq/screener").respond(
            422,
            json={
                "error_code": "VAL_001",
                "message": "Invalid filter: pe_ratio",
                "details": {"field": "pe_ratio"},
            },
        )
        with pytest.raises(ValidationError) as exc_info:
            client.request("POST", "/vq/screener", json={})
        assert exc_info.value.error_code == "VAL_001"
        assert exc_info.value.details == {"field": "pe_ratio"}

    @respx.mock
    def test_finance_format_429_rate_limit(self, client: VecTrade) -> None:
        respx.get(f"{BASE_URL}/vq/quotes/AAPL").respond(
            429,
            json={
                "error_code": "RL_001",
                "message": "Rate limit exceeded. Retry after 3 seconds.",
                "details": {"retry_after": 2.5},
            },
            headers={"Retry-After": "3"},
        )
        with pytest.raises(RateLimitError) as exc_info:
            client.request("GET", "/vq/quotes/AAPL")
        assert exc_info.value.error_code == "RL_001"

    @respx.mock
    def test_finance_format_429_quota_throttle(self, client: VecTrade) -> None:
        """429 with 'quota' in message should raise QuotaExceededError."""
        respx.get(f"{BASE_URL}/vq/quotes/AAPL").respond(
            429,
            json={
                "error_code": "RL_001",
                "message": "Monthly quota exceeded, requests throttled.",
                "details": None,
            },
        )
        with pytest.raises(QuotaExceededError) as exc_info:
            client.request("GET", "/vq/quotes/AAPL")
        assert exc_info.value.overage_policy == "THROTTLE"

    @respx.mock
    def test_finance_format_502_gateway(self, client: VecTrade) -> None:
        respx.get(f"{BASE_URL}/vq/quotes/AAPL").respond(
            502,
            json={
                "error_code": "SYS_002",
                "message": "Upstream service error",
            },
        )
        with pytest.raises(ServiceUnavailableError) as exc_info:
            client.request("GET", "/vq/quotes/AAPL")
        assert exc_info.value.error_code == "SYS_002"

    @respx.mock
    def test_finance_format_503_unavailable(self, client: VecTrade) -> None:
        respx.get(f"{BASE_URL}/vq/quotes/AAPL").respond(
            503,
            json={
                "error_code": "SYS_003",
                "message": "Service temporarily unavailable",
            },
        )
        with pytest.raises(ServiceUnavailableError) as exc_info:
            client.request("GET", "/vq/quotes/AAPL")
        assert exc_info.value.error_code == "SYS_003"

    @respx.mock
    def test_finance_format_500_internal(self, client: VecTrade) -> None:
        respx.get(f"{BASE_URL}/vq/quotes/AAPL").respond(
            500,
            json={
                "error_code": "SYS_001",
                "message": "Internal server error",
            },
        )
        with pytest.raises(ServerError) as exc_info:
            client.request("GET", "/vq/quotes/AAPL")
        assert exc_info.value.error_code == "SYS_001"

    @respx.mock
    def test_finance_format_retry_after_from_body(self, client: VecTrade) -> None:
        """retry_after in JSON body should be used when header is absent."""
        respx.get(f"{BASE_URL}/vq/quotes/AAPL").respond(
            429,
            json={
                "error_code": "RL_001",
                "message": "Rate limit exceeded",
                "details": {"retry_after": 5.0},
                "retry_after": 5.0,
            },
        )
        with pytest.raises(RateLimitError) as exc_info:
            client.request("GET", "/vq/quotes/AAPL")
        assert exc_info.value.retry_after == 5.0

class TestIdempotencyKey:
    """Test that idempotency key is sent as a header."""

    @respx.mock
    def test_idempotency_key_sent_as_header(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("VECTRADE_API_KEY", "vq_test_abcdefghijklmnop1234")
        client = VecTrade(max_retries=0)

        route = respx.post(f"{BASE_URL}/vq/screener").respond(200, json={"data": []})

        client.request("POST", "/vq/screener", json={}, idempotency_key="idem_abc123")

        assert route.called
        sent_headers = route.calls[0].request.headers
        assert sent_headers.get("idempotency-key") == "idem_abc123"
        client.close()

    @respx.mock
    def test_no_idempotency_key_when_not_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("VECTRADE_API_KEY", "vq_test_abcdefghijklmnop1234")
        client = VecTrade(max_retries=0)

        route = respx.get(f"{BASE_URL}/vq/quotes/AAPL").respond(200, json={"symbol": "AAPL"})

        client.request("GET", "/vq/quotes/AAPL")

        sent_headers = route.calls[0].request.headers
        assert "idempotency-key" not in sent_headers
        client.close()


class TestSuccessfulRequest:
    """Test successful request handling."""

    @respx.mock
    def test_200_returns_response(self, client: VecTrade) -> None:
        respx.get(f"{BASE_URL}/vq/quotes/AAPL").respond(200, json={"symbol": "AAPL", "price": 195.0})
        response = client.request("GET", "/vq/quotes/AAPL")
        assert response.status_code == 200
        assert response.json()["symbol"] == "AAPL"

    @respx.mock
    def test_post_with_body(self, client: VecTrade) -> None:
        route = respx.post(f"{BASE_URL}/vq/screener").respond(200, json={"data": []})
        client.request("POST", "/vq/screener", json={"marketCapMin": 1e9})
        import json
        sent = json.loads(route.calls[0].request.content)
        assert sent == {"marketCapMin": 1000000000.0}
