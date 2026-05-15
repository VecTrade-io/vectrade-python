"""Optional OpenTelemetry integration for the VecTrade SDK.

Install with: pip install vectrade[telemetry]

Usage:
    from vectrade import VecTrade
    from vectrade.telemetry import OpenTelemetryMiddleware

    client = VecTrade(middleware=[OpenTelemetryMiddleware()])
"""

from __future__ import annotations

from typing import Any, Callable

from vectrade._middleware import RequestContext, ResponseContext


class OpenTelemetryMiddleware:
    """Middleware that creates OpenTelemetry spans and records metrics for API requests.

    Requires `opentelemetry-api` and `opentelemetry-sdk` to be installed.

    Produces:
        - Traces: One span per request with HTTP attributes
        - Metrics:
            - `vectrade.sdk.requests` (counter): Total API requests
            - `vectrade.sdk.request_duration_ms` (histogram): Request latency
            - `vectrade.sdk.errors` (counter): Failed requests (4xx/5xx)
    """

    def __init__(
        self,
        tracer_name: str = "vectrade-sdk",
        meter_name: str = "vectrade-sdk",
        record_request_body: bool = False,
    ) -> None:
        self._tracer_name = tracer_name
        self._meter_name = meter_name
        self._record_body = record_request_body
        self._tracer: Any = None
        self._meter: Any = None
        self._request_counter: Any = None
        self._duration_histogram: Any = None
        self._error_counter: Any = None

    def _get_tracer(self) -> Any:
        if self._tracer is None:
            from opentelemetry import trace
            self._tracer = trace.get_tracer(self._tracer_name)
        return self._tracer

    def _get_meter(self) -> Any:
        if self._meter is None:
            from opentelemetry import metrics
            self._meter = metrics.get_meter(self._meter_name)
            self._request_counter = self._meter.create_counter(
                "vectrade.sdk.requests",
                unit="1",
                description="Total number of API requests made",
            )
            self._duration_histogram = self._meter.create_histogram(
                "vectrade.sdk.request_duration_ms",
                unit="ms",
                description="API request duration in milliseconds",
            )
            self._error_counter = self._meter.create_counter(
                "vectrade.sdk.errors",
                unit="1",
                description="Total number of failed API requests",
            )
        return self._meter

    def __call__(
        self,
        request: RequestContext,
        call_next: Callable[[RequestContext], ResponseContext],
    ) -> ResponseContext:
        tracer = self._get_tracer()
        self._get_meter()
        from opentelemetry import trace
        from opentelemetry.context import attach, detach
        from opentelemetry.trace.propagation import set_span_in_context

        span_name = f"vectrade.{request.method} {request.url.split('/')[-1]}"

        with tracer.start_as_current_span(
            span_name,
            kind=trace.SpanKind.CLIENT,
        ) as span:
            # Inject trace context into outgoing headers for distributed tracing
            try:
                from opentelemetry.propagate import inject
                inject(request.headers)
            except ImportError:
                pass

            # Set request attributes
            span.set_attribute("http.method", request.method)
            span.set_attribute("http.url", request.url)
            span.set_attribute("vectrade.sdk.version", _get_sdk_version())

            metric_attrs = {
                "http.method": request.method,
                "vectrade.resource": _extract_resource(request.url),
            }

            try:
                response = call_next(request)
            except Exception as exc:
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(exc)))
                span.record_exception(exc)
                self._error_counter.add(1, {**metric_attrs, "error.type": type(exc).__name__})
                raise

            # Record metrics
            metric_attrs["http.status_code"] = str(response.status_code)
            self._request_counter.add(1, metric_attrs)
            self._duration_histogram.record(response.elapsed_ms, metric_attrs)

            if response.status_code >= 400:
                self._error_counter.add(1, metric_attrs)

            # Set response attributes
            span.set_attribute("http.status_code", response.status_code)
            span.set_attribute("http.response_time_ms", response.elapsed_ms)

            if "X-Request-Id" in response.headers:
                span.set_attribute("vectrade.request_id", response.headers["X-Request-Id"])

            # Rate limit info
            if "X-VQ-RateLimit-Remaining" in response.headers:
                span.set_attribute(
                    "vectrade.ratelimit.remaining",
                    int(response.headers["X-VQ-RateLimit-Remaining"]),
                )

            if response.status_code >= 400:
                span.set_status(
                    trace.Status(trace.StatusCode.ERROR, f"HTTP {response.status_code}")
                )

            return response


def _get_sdk_version() -> str:
    try:
        from vectrade._version import __version__
        return __version__
    except ImportError:
        return "unknown"


def _extract_resource(url: str) -> str:
    """Extract the resource name from the URL path for metric labels."""
    # e.g., "https://api.vectrade.io/v1/vq/quotes/AAPL" -> "quotes"
    parts = url.rstrip("/").split("/")
    # Find the segment after "vq"
    try:
        vq_idx = parts.index("vq")
        if vq_idx + 1 < len(parts):
            return parts[vq_idx + 1]
    except ValueError:
        pass
    return parts[-1] if parts else "unknown"
