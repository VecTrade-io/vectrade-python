"""Tests for middleware classes and async AI stream."""

from unittest.mock import MagicMock

import pytest
import respx

from vectrade._middleware import (
    IdempotencyMiddleware,
    LoggingMiddleware,
    MiddlewareStack,
    RequestContext,
    ResponseContext,
    TimingMiddleware,
)

BASE_URL = "https://api.vectrade.io/v1"


def _make_request(method: str = "GET", url: str = "https://api.vectrade.io/v1/vq/quotes/AAPL") -> RequestContext:
    return RequestContext(method=method, url=url, headers={"X-API-Key": "vq_test"})


def _make_response(request: RequestContext, status: int = 200) -> ResponseContext:
    return ResponseContext(
        status_code=status,
        headers={"Content-Type": "application/json"},
        body=b'{}',
        elapsed_ms=10.0,
        request=request,
    )


class TestMiddlewareStack:
    def test_empty_stack_calls_handler(self) -> None:
        stack = MiddlewareStack()
        request = _make_request()
        handler = MagicMock(return_value=_make_response(request))
        result = stack.execute(request, handler)
        handler.assert_called_once_with(request)
        assert result.status_code == 200

    def test_single_middleware(self) -> None:
        stack = MiddlewareStack()
        stack.use(TimingMiddleware())
        request = _make_request()
        handler = MagicMock(return_value=_make_response(request))
        result = stack.execute(request, handler)
        assert "timing_ms" in result.metadata

    def test_middleware_order(self) -> None:
        """First added = outermost (executes first)."""
        order = []

        class MW1:
            def __call__(self, req, call_next):
                order.append("mw1_before")
                resp = call_next(req)
                order.append("mw1_after")
                return resp

        class MW2:
            def __call__(self, req, call_next):
                order.append("mw2_before")
                resp = call_next(req)
                order.append("mw2_after")
                return resp

        stack = MiddlewareStack()
        stack.use(MW1())
        stack.use(MW2())
        request = _make_request()
        stack.execute(request, lambda r: _make_response(r))
        assert order == ["mw1_before", "mw2_before", "mw2_after", "mw1_after"]


class TestLoggingMiddleware:
    def test_logs_request_response(self) -> None:
        logger = MagicMock()
        mw = LoggingMiddleware(logger=logger)
        request = _make_request()
        response = _make_response(request)
        result = mw(request, lambda r: response)
        assert result.status_code == 200
        assert logger.debug.call_count == 2

    def test_no_logger(self) -> None:
        mw = LoggingMiddleware()
        request = _make_request()
        response = _make_response(request)
        result = mw(request, lambda r: response)
        assert result.status_code == 200


class TestIdempotencyMiddleware:
    def test_adds_key_for_post(self) -> None:
        mw = IdempotencyMiddleware()
        request = _make_request(method="POST")
        mw(request, lambda r: _make_response(r))
        assert "Idempotency-Key" in request.headers

    def test_adds_key_for_put(self) -> None:
        mw = IdempotencyMiddleware()
        request = _make_request(method="PUT")
        mw(request, lambda r: _make_response(r))
        assert "Idempotency-Key" in request.headers

    def test_no_key_for_get(self) -> None:
        mw = IdempotencyMiddleware()
        request = _make_request(method="GET")
        mw(request, lambda r: _make_response(r))
        assert "Idempotency-Key" not in request.headers

    def test_does_not_overwrite_existing_key(self) -> None:
        mw = IdempotencyMiddleware()
        request = _make_request(method="POST")
        request.headers["Idempotency-Key"] = "my-custom-key"
        mw(request, lambda r: _make_response(r))
        assert request.headers["Idempotency-Key"] == "my-custom-key"

    def test_custom_key_generator(self) -> None:
        mw = IdempotencyMiddleware(key_generator=lambda: "fixed-key-123")
        request = _make_request(method="DELETE")
        mw(request, lambda r: _make_response(r))
        assert request.headers["Idempotency-Key"] == "fixed-key-123"


class TestTimingMiddleware:
    def test_adds_timing_metadata(self) -> None:
        mw = TimingMiddleware()
        request = _make_request()
        result = mw(request, lambda r: _make_response(r))
        assert "timing_ms" in result.metadata
        assert result.metadata["timing_ms"] >= 0


class TestAsyncAIStream:
    """Test the AsyncAI.stream method."""

    @respx.mock
    @pytest.mark.asyncio
    async def test_stream(self) -> None:
        import os

        os.environ["VECTRADE_API_KEY"] = "vq_test_abcdefghijklmnop1234"
        try:
            from vectrade import AsyncVecTrade

            # Mock the streaming POST endpoint
            sse_content = (
                'data: {"content": "Apple", "type": "text"}\n'
                'data: {"content": " looks bullish", "type": "text"}\n'
                'data: {"type": "done"}\n'
            )
            respx.post(f"{BASE_URL}/vq/ai/analyze").respond(
                200,
                content=sse_content,
                headers={"Content-Type": "text/event-stream"},
            )

            client = AsyncVecTrade(max_retries=0)
            try:
                chunks = []
                async for chunk in client.ai.stream("Analyze AAPL"):
                    chunks.append(chunk)
                assert len(chunks) == 2
                assert chunks[0].text == "Apple"
                assert chunks[1].text == " looks bullish"
            finally:
                await client.close()
        finally:
            del os.environ["VECTRADE_API_KEY"]
