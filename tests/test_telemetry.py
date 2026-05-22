"""Tests for the OpenTelemetry middleware."""

import sys
from unittest.mock import MagicMock, patch

import pytest

from vectrade._middleware import RequestContext, ResponseContext
from vectrade.telemetry import _extract_resource, _get_sdk_version


class TestExtractResource:
    def test_extracts_quotes(self) -> None:
        assert _extract_resource("https://api.vectrade.io/v1/vq/quotes/AAPL") == "quotes"

    def test_extracts_fundamentals(self) -> None:
        assert (
            _extract_resource("https://api.vectrade.io/v1/vq/fundamentals/MSFT") == "fundamentals"
        )

    def test_extracts_screener(self) -> None:
        assert _extract_resource("https://api.vectrade.io/v1/vq/screener") == "screener"

    def test_fallback_last_segment(self) -> None:
        assert _extract_resource("https://api.vectrade.io/health") == "health"

    def test_empty_url(self) -> None:
        result = _extract_resource("")
        # Empty string split yields [''], last element is ''
        assert result == ""

    def test_no_vq_segment(self) -> None:
        assert _extract_resource("https://example.com/api/data") == "data"


class TestGetSDKVersion:
    def test_returns_version_string(self) -> None:
        version = _get_sdk_version()
        assert version  # Not empty

    def test_returns_unknown_on_import_error(self) -> None:
        # Remove version module temporarily
        original = sys.modules.get("vectrade._version")
        sys.modules["vectrade._version"] = None  # type: ignore[assignment]
        try:
            # Re-import to force fresh import attempt
            from importlib import reload

            import vectrade.telemetry

            reload(vectrade.telemetry)
            # The function catches ImportError and returns "unknown"
            result = vectrade.telemetry._get_sdk_version()
            assert result == "unknown"
        finally:
            if original is not None:
                sys.modules["vectrade._version"] = original
            else:
                sys.modules.pop("vectrade._version", None)


class TestOpenTelemetryMiddleware:
    """Test the OpenTelemetry middleware using mocked otel modules."""

    def _make_request_context(self) -> RequestContext:
        return RequestContext(
            method="GET",
            url="https://api.vectrade.io/v1/vq/quotes/AAPL",
            headers={"X-API-Key": "vq_test_key"},
        )

    def _make_response_context(
        self, request: RequestContext, status_code: int = 200
    ) -> ResponseContext:
        return ResponseContext(
            status_code=status_code,
            headers={"X-Request-Id": "req-123", "X-VQ-RateLimit-Remaining": "99"},
            body=b'{"ticker": "AAPL"}',
            elapsed_ms=42.5,
            request=request,
        )

    def _setup_otel_mocks(self):
        """Create mock otel trace/metrics modules."""
        mock_trace = MagicMock()
        mock_metrics = MagicMock()
        mock_propagate = MagicMock()

        mock_tracer = MagicMock()
        mock_span = MagicMock()
        mock_tracer.start_as_current_span.return_value.__enter__ = MagicMock(return_value=mock_span)
        mock_tracer.start_as_current_span.return_value.__exit__ = MagicMock(return_value=False)
        mock_trace.get_tracer.return_value = mock_tracer
        mock_trace.SpanKind.CLIENT = "CLIENT"
        mock_trace.Status = MagicMock()
        mock_trace.StatusCode.ERROR = "ERROR"

        mock_meter = MagicMock()
        mock_metrics.get_meter.return_value = mock_meter
        mock_counter = MagicMock()
        mock_histogram = MagicMock()
        mock_error_counter = MagicMock()
        mock_meter.create_counter.side_effect = [mock_counter, mock_error_counter]
        mock_meter.create_histogram.return_value = mock_histogram

        return {
            "trace": mock_trace,
            "metrics": mock_metrics,
            "propagate": mock_propagate,
            "tracer": mock_tracer,
            "span": mock_span,
            "counter": mock_counter,
            "histogram": mock_histogram,
            "error_counter": mock_error_counter,
        }

    def test_init_params(self) -> None:
        from vectrade.telemetry import OpenTelemetryMiddleware

        mw = OpenTelemetryMiddleware(
            tracer_name="custom-tracer",
            meter_name="custom-meter",
            record_request_body=True,
        )
        assert mw._tracer_name == "custom-tracer"
        assert mw._meter_name == "custom-meter"
        assert mw._record_body is True

    def test_successful_request(self) -> None:
        """Test middleware creates span and records metrics for success."""
        mocks = self._setup_otel_mocks()

        with patch.dict(
            "sys.modules",
            {
                "opentelemetry": MagicMock(trace=mocks["trace"], metrics=mocks["metrics"]),
                "opentelemetry.trace": mocks["trace"],
                "opentelemetry.metrics": mocks["metrics"],
                "opentelemetry.propagate": mocks["propagate"],
            },
        ):
            from importlib import reload

            import vectrade.telemetry

            reload(vectrade.telemetry)
            middleware = vectrade.telemetry.OpenTelemetryMiddleware()

            request = self._make_request_context()
            response = self._make_response_context(request)

            def call_next(req):
                return response

            result = middleware(request, call_next)

        assert result.status_code == 200
        mocks["tracer"].start_as_current_span.assert_called_once()

    def test_error_response_records_error(self) -> None:
        """4xx/5xx responses are recorded as errors."""
        mocks = self._setup_otel_mocks()

        with patch.dict(
            "sys.modules",
            {
                "opentelemetry": MagicMock(trace=mocks["trace"], metrics=mocks["metrics"]),
                "opentelemetry.trace": mocks["trace"],
                "opentelemetry.metrics": mocks["metrics"],
                "opentelemetry.propagate": mocks["propagate"],
            },
        ):
            from importlib import reload

            import vectrade.telemetry

            reload(vectrade.telemetry)
            middleware = vectrade.telemetry.OpenTelemetryMiddleware()

            request = self._make_request_context()
            response = self._make_response_context(request, status_code=403)

            def call_next(req):
                return response

            result = middleware(request, call_next)

        assert result.status_code == 403
        mocks["error_counter"].add.assert_called()

    def test_exception_propagation(self) -> None:
        """Exceptions from call_next propagate and are recorded."""
        mocks = self._setup_otel_mocks()

        with patch.dict(
            "sys.modules",
            {
                "opentelemetry": MagicMock(trace=mocks["trace"], metrics=mocks["metrics"]),
                "opentelemetry.trace": mocks["trace"],
                "opentelemetry.metrics": mocks["metrics"],
                "opentelemetry.propagate": mocks["propagate"],
            },
        ):
            from importlib import reload

            import vectrade.telemetry

            reload(vectrade.telemetry)
            middleware = vectrade.telemetry.OpenTelemetryMiddleware()

            request = self._make_request_context()

            def call_next(req):
                raise ConnectionError("timeout")

            with pytest.raises(ConnectionError):
                middleware(request, call_next)

        mocks["span"].record_exception.assert_called_once()
