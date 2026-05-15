"""Tests for header utilities."""

from vectrade._utils.headers import RateLimitInfo, ResponseMetadata


class TestRateLimitInfo:
    """Test rate limit parsing from headers."""

    def test_parse_all_headers(self) -> None:
        headers = {
            "X-VQ-RateLimit-Limit": "1000",
            "X-VQ-RateLimit-Remaining": "950",
            "X-VQ-RateLimit-Reset": "1715800000",
        }
        info = RateLimitInfo.from_headers(headers)
        assert info.limit == 1000
        assert info.remaining == 950
        assert info.reset_timestamp == 1715800000

    def test_missing_headers(self) -> None:
        info = RateLimitInfo.from_headers({})
        assert info.limit is None
        assert info.remaining is None
        assert info.reset_timestamp is None

    def test_invalid_values(self) -> None:
        headers = {
            "X-VQ-RateLimit-Limit": "invalid",
            "X-VQ-RateLimit-Remaining": "",
        }
        info = RateLimitInfo.from_headers(headers)
        assert info.limit is None
        assert info.remaining is None


class TestResponseMetadata:
    """Test response metadata extraction."""

    def test_full_metadata(self) -> None:
        headers = {
            "X-Request-Id": "req_abc123",
            "X-VQ-RateLimit-Limit": "100",
            "X-VQ-RateLimit-Remaining": "99",
            "X-VQ-RateLimit-Reset": "1715800000",
        }
        meta = ResponseMetadata.from_headers(headers)
        assert meta.request_id == "req_abc123"
        assert meta.rate_limit.limit == 100

    def test_missing_request_id(self) -> None:
        meta = ResponseMetadata.from_headers({})
        assert meta.request_id is None
