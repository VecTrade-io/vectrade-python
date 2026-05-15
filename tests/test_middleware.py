"""Tests for middleware architecture."""

from vectrade._middleware import (
    IdempotencyMiddleware,
    LoggingMiddleware,
    MiddlewareStack,
    RequestContext,
    ResponseContext,
    TimingMiddleware,
)


def _make_request() -> RequestContext:
    return RequestContext(
        method="GET",
        url="https://api.vectrade.io/v1/quotes/AAPL",
        headers={"Authorization": "Bearer vq_test_key"},
    )


def _make_handler(status: int = 200) -> object:
    """Create a terminal handler that returns a fixed response."""
    def handler(request: RequestContext) -> ResponseContext:
        return ResponseContext(
            status_code=status,
            headers={"X-Request-Id": "req_test_123"},
            body=b'{"symbol": "AAPL"}',
            elapsed_ms=42.0,
            request=request,
        )
    return handler


class TestMiddlewareStack:
    """Test middleware chain execution."""

    def test_empty_stack(self) -> None:
        """Empty stack calls handler directly."""
        stack = MiddlewareStack()
        req = _make_request()
        resp = stack.execute(req, _make_handler())
        assert resp.status_code == 200

    def test_single_middleware(self) -> None:
        """Single middleware wraps the handler."""
        calls: list[str] = []

        def middleware(request, call_next):
            calls.append("before")
            response = call_next(request)
            calls.append("after")
            return response

        stack = MiddlewareStack()
        stack.use(middleware)
        stack.execute(_make_request(), _make_handler())

        assert calls == ["before", "after"]

    def test_ordering(self) -> None:
        """Middlewares execute in order (first added = outermost)."""
        order: list[int] = []

        def make_mw(n: int):
            def middleware(request, call_next):
                order.append(n)
                return call_next(request)
            return middleware

        stack = MiddlewareStack()
        stack.use(make_mw(1))
        stack.use(make_mw(2))
        stack.use(make_mw(3))
        stack.execute(_make_request(), _make_handler())

        assert order == [1, 2, 3]

    def test_middleware_can_modify_request(self) -> None:
        """Middleware can add headers before passing along."""
        def add_header(request, call_next):
            request.headers["X-Custom"] = "test-value"
            return call_next(request)

        captured_headers = {}

        def handler(request):
            captured_headers.update(request.headers)
            return ResponseContext(
                status_code=200, headers={}, body=b"",
                elapsed_ms=0, request=request,
            )

        stack = MiddlewareStack()
        stack.use(add_header)
        stack.execute(_make_request(), handler)

        assert captured_headers["X-Custom"] == "test-value"


class TestTimingMiddleware:
    """Test timing middleware."""

    def test_records_timing(self) -> None:
        stack = MiddlewareStack()
        stack.use(TimingMiddleware())
        resp = stack.execute(_make_request(), _make_handler())
        assert "timing_ms" in resp.metadata
        assert resp.metadata["timing_ms"] >= 0


class TestIdempotencyMiddleware:
    """Test idempotency key injection."""

    def test_adds_key_for_post(self) -> None:
        req = RequestContext(
            method="POST",
            url="https://api.vectrade.io/v1/webhooks",
            headers={},
        )

        captured = {}

        def handler(request):
            captured.update(request.headers)
            return ResponseContext(
                status_code=201, headers={}, body=b"",
                elapsed_ms=0, request=request,
            )

        stack = MiddlewareStack()
        stack.use(IdempotencyMiddleware())
        stack.execute(req, handler)

        assert "Idempotency-Key" in captured
        assert len(captured["Idempotency-Key"]) > 0

    def test_skips_get_requests(self) -> None:
        req = _make_request()  # GET

        captured = {}

        def handler(request):
            captured.update(request.headers)
            return ResponseContext(
                status_code=200, headers={}, body=b"",
                elapsed_ms=0, request=request,
            )

        stack = MiddlewareStack()
        stack.use(IdempotencyMiddleware())
        stack.execute(req, handler)

        assert "Idempotency-Key" not in captured

    def test_preserves_existing_key(self) -> None:
        req = RequestContext(
            method="POST",
            url="https://api.vectrade.io/v1/webhooks",
            headers={"Idempotency-Key": "my-custom-key"},
        )

        captured = {}

        def handler(request):
            captured.update(request.headers)
            return ResponseContext(
                status_code=201, headers={}, body=b"",
                elapsed_ms=0, request=request,
            )

        stack = MiddlewareStack()
        stack.use(IdempotencyMiddleware())
        stack.execute(req, handler)

        assert captured["Idempotency-Key"] == "my-custom-key"


class TestClientMiddlewareIntegration:
    """Test that VecTrade client accepts middleware parameter."""

    def test_client_accepts_middleware(self, monkeypatch) -> None:
        """VecTrade client constructor accepts middleware list."""
        monkeypatch.setenv("VECTRADE_API_KEY", "vq_test_key_123456789")

        from vectrade import VecTrade

        mw = TimingMiddleware()
        client = VecTrade(middleware=[mw])

        assert len(client._middleware_stack._middlewares) == 1
        client.close()

    def test_client_empty_middleware(self, monkeypatch) -> None:
        """VecTrade client works without middleware."""
        monkeypatch.setenv("VECTRADE_API_KEY", "vq_test_key_123456789")

        from vectrade import VecTrade

        client = VecTrade()
        assert len(client._middleware_stack._middlewares) == 0
        client.close()
