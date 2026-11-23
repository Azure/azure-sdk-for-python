# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for OpenTelemetry tracing in the invocations protocol."""
import os
import logging
import uuid
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import InMemoryLogRecordExporter, SimpleLogRecordProcessor
from starlette.testclient import TestClient
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from azure.ai.agentserver.invocations import InvocationAgentServerHost
from azure.ai.agentserver.core import _tracing
from azure.ai.agentserver.invocations import _invocation


# ---------------------------------------------------------------------------
# Lazy OTel setup with in-memory exporter
# ---------------------------------------------------------------------------
# We use the real OTel SDK to capture spans in memory.
# IMPORTANT: Provider setup is deferred to a fixture so that
# set_tracer_provider() is NOT called at import time.  When pytest collects
# tests it imports every module — module-level set_tracer_provider() would
# consume the global Once guard and break e2e tests that rely on the
# microsoft-opentelemetry distro to set the provider.

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider as SdkTracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

    _HAS_OTEL = True
except ImportError:
    _HAS_OTEL = False

_MODULE_PROVIDER = None
_MODULE_EXPORTER = None
_MODULE_SETUP_DONE = False

pytestmark = pytest.mark.skipif(not _HAS_OTEL, reason="opentelemetry not installed")


@pytest.fixture(autouse=True)
def _clear_spans():
    """Set up the OTel provider on first use, then clear spans before each test."""
    global _MODULE_PROVIDER, _MODULE_EXPORTER, _MODULE_SETUP_DONE
    if _HAS_OTEL and not _MODULE_SETUP_DONE:
        _existing = trace.get_tracer_provider()
        if hasattr(_existing, "add_span_processor"):
            _MODULE_PROVIDER = _existing
        else:
            _MODULE_PROVIDER = SdkTracerProvider()
            trace.set_tracer_provider(_MODULE_PROVIDER)
        _MODULE_EXPORTER = InMemorySpanExporter()
        _MODULE_PROVIDER.add_span_processor(SimpleSpanProcessor(_MODULE_EXPORTER))
        _MODULE_SETUP_DONE = True
    if _MODULE_EXPORTER:
        _MODULE_EXPORTER.clear()


def _get_spans():
    """Return all captured spans."""
    if _MODULE_EXPORTER:
        return _MODULE_EXPORTER.get_finished_spans()
    return []


# ---------------------------------------------------------------------------
# Helper: create tracing-enabled server
# ---------------------------------------------------------------------------

def _make_tracing_server(**kwargs):
    """Create an InvocationAgentServerHost with tracing enabled."""
    with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=00000000-0000-0000-0000-000000000000"}):
        with patch("azure.ai.agentserver.core._tracing._setup_distro_export", create=True):
            server = InvocationAgentServerHost(**kwargs)

    @server.invoke_handler
    async def handle(request: Request) -> Response:
        body = await request.body()
        return Response(content=body, media_type="application/octet-stream")

    return server


def _make_tracing_server_with_get_cancel(**kwargs):
    """Create a tracing-enabled server with get/cancel handlers."""
    with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=00000000-0000-0000-0000-000000000000"}):
        with patch("azure.ai.agentserver.core._tracing._setup_distro_export", create=True):
            server = InvocationAgentServerHost(**kwargs)

    store: dict[str, bytes] = {}

    @server.invoke_handler
    async def handle(request: Request) -> Response:
        body = await request.body()
        store[request.state.invocation_id] = body
        return Response(content=body, media_type="application/octet-stream")

    @server.get_invocation_handler
    async def get_handler(request: Request) -> Response:
        inv_id = request.path_params["invocation_id"]
        if inv_id in store:
            return Response(content=store[inv_id])
        return JSONResponse({"error": {"code": "not_found", "message": "Not found"}}, status_code=404)

    @server.cancel_invocation_handler
    async def cancel_handler(request: Request) -> Response:
        inv_id = request.path_params["invocation_id"]
        if inv_id in store:
            del store[inv_id]
            return JSONResponse({"status": "cancelled"})
        return JSONResponse({"error": {"code": "not_found", "message": "Not found"}}, status_code=404)

    return server


def _make_failing_tracing_server(**kwargs):
    """Create a tracing-enabled server whose handler raises."""
    with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=00000000-0000-0000-0000-000000000000"}):
        with patch("azure.ai.agentserver.core._tracing._setup_distro_export", create=True):
            server = InvocationAgentServerHost(**kwargs)

    @server.invoke_handler
    async def handle(request: Request) -> Response:
        raise ValueError("tracing error test")

    return server


def _make_streaming_tracing_server(**kwargs):
    """Create a tracing-enabled server with streaming response."""
    with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=00000000-0000-0000-0000-000000000000"}):
        with patch("azure.ai.agentserver.core._tracing._setup_distro_export", create=True):
            server = InvocationAgentServerHost(**kwargs)

    @server.invoke_handler
    async def handle(request: Request) -> StreamingResponse:
        async def generate():
            yield b"chunk1\n"
            yield b"chunk2\n"

        return StreamingResponse(generate(), media_type="text/plain")

    return server


# ---------------------------------------------------------------------------
# Tracing disabled by default
# ---------------------------------------------------------------------------

def test_tracing_disabled_by_default():
    """No invoke_agent span is created — only framework/user spans appear."""
    if _MODULE_EXPORTER:
        _MODULE_EXPORTER.clear()

    app = InvocationAgentServerHost(configure_observability=None)

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    client = TestClient(app)
    client.post("/invocations", content=b"test")

    # No invoke_agent SERVER span is created (request_context only propagates context)
    spans = _get_spans()
    invoke_spans = [s for s in spans if "invoke_agent" in s.name]
    assert len(invoke_spans) == 0


# ---------------------------------------------------------------------------
# Tracing enabled — no invoke_agent span created
# ---------------------------------------------------------------------------

def test_tracing_enabled_no_invoke_span():
    """Tracing enabled does NOT create an invoke_agent span (context-only propagation)."""
    server = _make_tracing_server()
    client = TestClient(server)
    client.post("/invocations", content=b"test")

    spans = _get_spans()
    invoke_spans = [s for s in spans if "invoke_agent" in s.name]
    assert len(invoke_spans) == 0


# ---------------------------------------------------------------------------
# Invoke error returns 500
# ---------------------------------------------------------------------------

def test_invoke_error_returns_500():
    """When handler raises, a 500 response is returned."""
    server = _make_failing_tracing_server()
    client = TestClient(server)
    resp = client.post("/invocations", content=b"test")
    assert resp.status_code == 500


# ---------------------------------------------------------------------------
# GET/cancel endpoints still work
# ---------------------------------------------------------------------------

def test_get_invocation_returns_response():
    """GET /invocations/{id} returns the stored response."""
    server = _make_tracing_server_with_get_cancel()
    client = TestClient(server)
    resp = client.post("/invocations", content=b"data")
    inv_id = resp.headers["x-agent-invocation-id"]
    get_resp = client.get(f"/invocations/{inv_id}")
    assert get_resp.status_code == 200


def test_cancel_invocation_returns_response():
    """POST /invocations/{id}/cancel returns cancelled status."""
    server = _make_tracing_server_with_get_cancel()
    client = TestClient(server)
    resp = client.post("/invocations", content=b"data")
    inv_id = resp.headers["x-agent-invocation-id"]
    cancel_resp = client.post(f"/invocations/{inv_id}/cancel")
    assert cancel_resp.status_code == 200


# ---------------------------------------------------------------------------
# Tracing via env var
# ---------------------------------------------------------------------------

def test_tracing_via_appinsights_env_var():
    """Tracing is enabled when APPLICATIONINSIGHTS_CONNECTION_STRING is set."""
    with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=00000000-0000-0000-0000-000000000000"}):
        with patch("azure.ai.agentserver.core._tracing._setup_distro_export", create=True):
            app = InvocationAgentServerHost()

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    client = TestClient(app)
    client.post("/invocations", content=b"test")

    # No invoke_agent span (context-only propagation)
    spans = _get_spans()
    invoke_spans = [s for s in spans if "invoke_agent" in s.name]
    assert len(invoke_spans) == 0


# ---------------------------------------------------------------------------
# No tracing when no endpoints configured
# ---------------------------------------------------------------------------

def test_no_tracing_when_no_endpoints():
    """When no connection string or OTLP endpoint is set, configure_observability
    still runs (for console logging) but tracing spans are not exported."""
    env = os.environ.copy()
    env.pop("APPLICATIONINSIGHTS_CONNECTION_STRING", None)
    env.pop("OTEL_EXPORTER_OTLP_ENDPOINT", None)
    with patch.dict(os.environ, env, clear=True):
        app = InvocationAgentServerHost(configure_observability=None)

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    if _MODULE_EXPORTER:
        _MODULE_EXPORTER.clear()

    client = TestClient(app)
    client.post("/invocations", content=b"test")

    # No invoke_agent span
    spans = _get_spans()
    invoke_spans = [s for s in spans if "invoke_agent" in s.name]
    assert len(invoke_spans) == 0


# ---------------------------------------------------------------------------
# Traceparent propagation — context is set even without a span
# ---------------------------------------------------------------------------

def test_traceparent_propagation():
    """Server propagates traceparent header into OTel context for framework spans.

    Uses a real OTel span + ``inject(headers)`` instead of a synthetic
    traceparent string for CI reliability.
    """
    from opentelemetry import trace as _trace
    from opentelemetry.propagate import inject

    captured_trace_id = None
    captured_parent_id = None

    with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=00000000-0000-0000-0000-000000000000"}):
        with patch("azure.ai.agentserver.core._tracing._setup_distro_export", create=True):
            server = InvocationAgentServerHost()

    @server.invoke_handler
    async def handle(request: Request) -> Response:
        nonlocal captured_trace_id, captured_parent_id
        # Create a framework span — it should inherit the incoming traceparent
        tracer = _trace.get_tracer("test-framework")
        with tracer.start_as_current_span("framework_op") as span:
            captured_trace_id = format(span.context.trace_id, "032x")
            captured_parent_id = format(span.parent.span_id, "016x") if span.parent else None
        return Response(content=b"ok")

    client = TestClient(server)

    caller_tracer = _trace.get_tracer("test.caller")
    with caller_tracer.start_as_current_span("CallerOp") as caller_span:
        caller_trace_id = format(caller_span.context.trace_id, "032x")
        caller_span_id = format(caller_span.context.span_id, "016x")

        headers: dict[str, str] = {}
        inject(headers)

        client.post(
            "/invocations",
            content=b"test",
            headers=headers,
        )

    assert captured_trace_id == caller_trace_id
    assert captured_parent_id == caller_span_id


# ---------------------------------------------------------------------------
# Streaming responses still work
# ---------------------------------------------------------------------------

def test_streaming_returns_response():
    """Streaming response is returned successfully."""
    server = _make_streaming_tracing_server()
    client = TestClient(server)
    resp = client.post("/invocations", content=b"test")
    assert resp.status_code == 200


def test_streaming_iteration_exception_records_trace_error():
    """Exceptions raised while iterating streaming responses are traced and re-raised."""
    server = _make_streaming_tracing_server()
    client = TestClient(server)

    @server.invoke_handler
    async def handle(request: Request) -> StreamingResponse:
        async def generate():
            yield b"chunk1\n"
            raise RuntimeError("stream exploded")

        return StreamingResponse(generate(), media_type="text/plain")

    with patch("azure.ai.agentserver.invocations._invocation.logger.error") as mock_log_error:
        with patch("azure.ai.agentserver.invocations._invocation.trace.get_current_span") as mock_get_span:
            mock_span = mock_get_span.return_value
            mock_span.is_recording.return_value = True

            with pytest.raises(RuntimeError, match="stream exploded"):
                client.post("/invocations", content=b"test")

            mock_span.set_status.assert_called_once_with(trace.StatusCode.ERROR, "stream exploded")
            mock_span.set_attribute.assert_called_once_with("error.type", "RuntimeError")
            mock_span.record_exception.assert_called_once()
            assert isinstance(mock_span.record_exception.call_args.args[0], RuntimeError)
            mock_log_error.assert_called_once()


class TestErrorTelemetry:
    @pytest.fixture()
    def telemetry(self, monkeypatch):
        monkeypatch.setattr(_tracing, "_configured_sensitive_data_capture", None, raising=False)
        span_exporter = InMemorySpanExporter()
        span_provider = SdkTracerProvider()
        span_provider.add_span_processor(SimpleSpanProcessor(span_exporter))
        log_exporter = InMemoryLogRecordExporter()
        log_provider = LoggerProvider()
        log_provider.add_log_record_processor(SimpleLogRecordProcessor(log_exporter))
        handler = LoggingHandler(level=logging.ERROR, logger_provider=log_provider)
        sdk_logger = logging.getLogger("azure.ai.agentserver")
        previous_level = sdk_logger.level
        sdk_logger.setLevel(logging.ERROR)
        sdk_logger.addHandler(handler)
        try:
            yield span_provider.get_tracer("test-error-capture"), span_exporter, log_exporter
        finally:
            sdk_logger.removeHandler(handler)
            sdk_logger.setLevel(previous_level)
            handler.close()
            log_provider.shutdown()
            span_provider.shutdown()

    @staticmethod
    def _assert_logs(log_exporter, enabled, exception_type):
        records = [record.log_record for record in log_exporter.get_finished_logs()]
        assert len(records) == 1
        rendered = str(records[0].body) + str(dict(records[0].attributes))
        if enabled:
            assert "private-error-marker" in rendered
        else:
            assert "private-error-marker" not in rendered
            assert exception_type in records[0].body
            assert "exception.message" not in records[0].attributes
            assert "exception.stacktrace" not in records[0].attributes

    @pytest.mark.asyncio
    @pytest.mark.parametrize("enabled", [False, True])
    @pytest.mark.parametrize("setting", ["environment", "callback"])
    async def test_streaming_error_capture_preserves_propagation(self, telemetry, monkeypatch, enabled, setting):
        tracer, span_exporter, log_exporter = telemetry
        environment_enabled = enabled if setting == "environment" else not enabled
        monkeypatch.setenv(
            "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT",
            "true" if environment_enabled else "false",
        )
        # Older supported core releases expose only the environment-based fallback.
        expected_capture = enabled if hasattr(_tracing, "_is_sensitive_data_enabled") else environment_enabled

        def configure(**kwargs):
            kwargs["enable_sensitive_data"] = enabled
            _tracing.configure_observability(**kwargs)

        app = InvocationAgentServerHost(
            **({"configure_observability": configure} if setting == "callback" else {}),
        )
        error = RuntimeError("private-error-marker")

        @app.invoke_handler
        async def handle(request: Request) -> StreamingResponse:
            async def chunks():
                yield b"first\n"
                raise error

            return StreamingResponse(chunks(), media_type="text/plain")

        # Agent Server propagates context; the application's instrumentation creates spans.
        route = next(route for route in app.routes if getattr(route, "path", None) == "/invocations")
        route_app = route.app

        async def traced_route(scope, receive, send):
            with tracer.start_as_current_span(
                "request",
                record_exception=False,
                set_status_on_exception=False,
            ):
                await route_app(scope, receive, send)

        route.app = traced_route
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
            with pytest.raises(RuntimeError) as raised:
                await client.post("/invocations", headers={"x-agent-invocation-id": "inv-safe"})
        assert raised.value is error

        exported = span_exporter.get_finished_spans()
        assert len(exported) == 1
        assert exported[0].status.status_code == trace.StatusCode.ERROR
        assert exported[0].attributes["error.type"] == "RuntimeError"
        if expected_capture:
            assert exported[0].status.description == "private-error-marker"
            assert exported[0].events[0].attributes["exception.message"] == "private-error-marker"
        else:
            assert exported[0].status.description is None
            assert not exported[0].events
            assert "private-error-marker" not in exported[0].to_json()
        self._assert_logs(log_exporter, expected_capture, "RuntimeError")

    @pytest.mark.asyncio
    async def test_streaming_opt_out_supports_older_core(self, telemetry, monkeypatch):
        tracer, span_exporter, log_exporter = telemetry
        monkeypatch.setenv("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "false")
        app = InvocationAgentServerHost(configure_observability=None)
        old_core = SimpleNamespace(record_error=Mock())
        monkeypatch.setattr(_invocation, "_tracing", old_core)
        error = RuntimeError("private-error-marker")

        async def chunks():
            yield b"first"
            raise error

        response = app._wrap_streaming_response(StreamingResponse(chunks()), "inv-safe", "session-safe")
        with tracer.start_as_current_span("stream", record_exception=False, set_status_on_exception=False):
            with pytest.raises(RuntimeError) as raised:
                async for _ in response.body_iterator:
                    pass
        assert raised.value is error
        old_core.record_error.assert_not_called()
        exported = span_exporter.get_finished_spans()[0]
        assert exported.status.status_code == trace.StatusCode.ERROR
        assert exported.attributes["error.type"] == "RuntimeError"
        assert not exported.events
        self._assert_logs(log_exporter, False, "RuntimeError")

    @pytest.mark.asyncio
    @pytest.mark.parametrize("enabled", [False, True])
    async def test_skipped_setup_error_logging_follows_supported_core_policy(self, telemetry, monkeypatch, enabled):
        _, _, log_exporter = telemetry
        _tracing.configure_observability(enable_sensitive_data=enabled)
        environment_enabled = not enabled
        monkeypatch.setenv(
            "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "true" if environment_enabled else "false"
        )
        expected_capture = enabled if hasattr(_tracing, "_is_sensitive_data_enabled") else environment_enabled
        app = InvocationAgentServerHost(configure_observability=None)

        @app.invoke_handler
        async def handle(request: Request) -> Response:
            raise ValueError("private-error-marker")

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
            response = await client.post("/invocations")
        assert response.status_code == 500
        self._assert_logs(log_exporter, expected_capture, "ValueError")

    @pytest.mark.asyncio
    @pytest.mark.parametrize("enabled", [False, True])
    @pytest.mark.parametrize("operation", ["invoke", "get", "cancel", "not_implemented"])
    async def test_http_error_capture_preserves_responses(self, telemetry, monkeypatch, enabled, operation):
        _, _, log_exporter = telemetry
        monkeypatch.setenv("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "true" if enabled else "false")
        app = InvocationAgentServerHost()

        async def fail(request: Request) -> Response:
            if operation == "not_implemented":
                raise NotImplementedError("private-error-marker")
            raise ValueError("private-error-marker")

        app.invoke_handler(fail)
        app.get_invocation_handler(fail)
        app.cancel_invocation_handler(fail)
        routes = {
            "invoke": ("POST", "/invocations"),
            "not_implemented": ("POST", "/invocations"),
            "get": ("GET", "/invocations/inv-safe"),
            "cancel": ("POST", "/invocations/inv-safe/cancel"),
        }
        method, path = routes[operation]
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
            response = await client.request(method, path, headers={"x-agent-invocation-id": "inv-safe"})

        assert response.headers["x-agent-invocation-id"] == "inv-safe"
        if operation == "not_implemented":
            assert response.status_code == 501
            assert response.json()["error"] == {"code": "not_implemented", "message": "private-error-marker"}
            exception_type = "NotImplementedError"
        else:
            assert response.status_code == 500
            assert response.json()["error"] == {"code": "internal_error", "message": "Internal server error"}
            exception_type = "ValueError"
        self._assert_logs(log_exporter, enabled, exception_type)


def test_streaming_wrapper_resets_contextvars():
    """Streaming wrapper resets the contextvar tokens it sets."""
    server = _make_streaming_tracing_server()
    client = TestClient(server)

    @server.invoke_handler
    async def handle(request: Request) -> StreamingResponse:
        async def generate():
            yield b"chunk1\n"

        return StreamingResponse(generate(), media_type="text/plain")

    class _FakeContextVar:
        def __init__(self):
            self.set_tokens = []
            self.reset_tokens = []

        def set(self, value):
            token = (len(self.set_tokens), value)
            self.set_tokens.append(token)
            return token

        def reset(self, token):
            self.reset_tokens.append(token)

        def get(self, default=""):
            return default

    fake_inv = _FakeContextVar()
    fake_session = _FakeContextVar()
    with patch("azure.ai.agentserver.invocations._invocation._invocation_id_var", fake_inv):
        with patch("azure.ai.agentserver.invocations._invocation._session_id_var", fake_session):
            resp = client.post("/invocations", content=b"test")

    assert resp.status_code == 200
    assert len(fake_inv.set_tokens) == 2
    assert len(fake_session.set_tokens) == 2
    assert fake_inv.reset_tokens == fake_inv.set_tokens
    assert fake_session.reset_tokens == fake_session.set_tokens


# ---------------------------------------------------------------------------
# Incoming W3C baggage propagation
# ---------------------------------------------------------------------------

def test_incoming_baggage_merged_into_context():
    """Incoming W3C baggage header entries are merged into OTel context."""
    from opentelemetry import baggage as _otel_baggage

    captured_baggage = {}

    with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=00000000-0000-0000-0000-000000000000"}):
        with patch("azure.ai.agentserver.core._tracing._setup_distro_export", create=True):
            server = InvocationAgentServerHost()

    @server.invoke_handler
    async def handle(request: Request) -> Response:
        captured_baggage.update(_otel_baggage.get_all())
        return Response(content=b"ok")

    client = TestClient(server)
    client.post(
        "/invocations",
        content=b"test",
        headers={"baggage": "user.id=test-user-123,custom.key=custom-value"},
    )

    # Incoming baggage entries should be present
    assert captured_baggage.get("user.id") == "test-user-123"
    assert captured_baggage.get("custom.key") == "custom-value"


def test_sdk_set_baggage_available_in_handler():
    """SDK-set baggage entries (invocation_id, session_id) are available in handler context."""
    from opentelemetry import baggage as _otel_baggage

    captured_baggage = {}

    with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=00000000-0000-0000-0000-000000000000"}):
        with patch("azure.ai.agentserver.core._tracing._setup_distro_export", create=True):
            server = InvocationAgentServerHost()

    @server.invoke_handler
    async def handle(request: Request) -> Response:
        captured_baggage.update(_otel_baggage.get_all())
        return Response(content=b"ok")

    client = TestClient(server)
    client.post(
        "/invocations",
        content=b"test",
        headers={
            "x-agent-invocation-id": "inv-test-42",
            "baggage": "caller.key=caller-value",
        },
    )

    # SDK-set baggage entries
    assert captured_baggage.get("azure.ai.agentserver.invocation_id") == "inv-test-42"
    assert "azure.ai.agentserver.session_id" in captured_baggage
    # Incoming caller baggage is also preserved
    assert captured_baggage.get("caller.key") == "caller-value"


def test_incoming_baggage_does_not_break_span_parenting():
    """Incoming baggage header does not break parent-child span relationships.
    Framework spans created inside the handler should be parented under the
    incoming traceparent (no intermediate invoke_agent span).

    Uses a real OTel span + ``inject(headers)`` for CI reliability.
    """
    from opentelemetry import trace as _trace
    from opentelemetry.propagate import inject

    captured_trace_id = None
    captured_parent_id = None

    with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=00000000-0000-0000-0000-000000000000"}):
        with patch("azure.ai.agentserver.core._tracing._setup_distro_export", create=True):
            server = InvocationAgentServerHost()

    @server.invoke_handler
    async def handle(request: Request) -> Response:
        nonlocal captured_trace_id, captured_parent_id
        tracer = _trace.get_tracer("test-framework")
        with tracer.start_as_current_span("framework_op") as span:
            captured_trace_id = format(span.context.trace_id, "032x")
            captured_parent_id = format(span.parent.span_id, "016x") if span.parent else None
        return Response(content=b"ok")

    client = TestClient(server)

    caller_tracer = _trace.get_tracer("test.caller")
    with caller_tracer.start_as_current_span("CallerBaggageOp") as caller_span:
        caller_trace_id = format(caller_span.context.trace_id, "032x")
        caller_span_id = format(caller_span.context.span_id, "016x")

        headers: dict[str, str] = {"baggage": "user.id=test-user-456"}
        inject(headers)

        client.post(
            "/invocations",
            content=b"test",
            headers=headers,
        )

    # Framework span inherits trace ID and parents directly under incoming span
    assert captured_trace_id == caller_trace_id
    assert captured_parent_id == caller_span_id


def test_incoming_baggage_empty_header():
    """Empty baggage header does not cause errors."""
    server = _make_tracing_server()
    client = TestClient(server)
    resp = client.post(
        "/invocations",
        content=b"test",
        headers={"baggage": ""},
    )
    assert resp.status_code == 200


def test_incoming_baggage_stamped_on_handler_spans():
    """FoundryEnrichmentSpanProcessor stamps baggage entries as span attributes.

    Tests the enrichment processor in isolation to avoid CI-specific context
    propagation differences through TestClient/ASGI.  The full baggage flow
    through the invocations server is already covered by
    ``test_sdk_set_baggage_available_in_handler``.
    """
    from opentelemetry import trace as _trace
    from opentelemetry import context as _otel_context
    from opentelemetry import baggage as _otel_baggage
    from opentelemetry.sdk.trace import TracerProvider as SdkTracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    from azure.ai.agentserver.core._tracing import _FoundryEnrichmentSpanProcessor

    # Set up an isolated provider with just the enrichment processor
    exporter = InMemorySpanExporter()
    provider = SdkTracerProvider()
    provider.add_span_processor(_FoundryEnrichmentSpanProcessor())
    provider.add_span_processor(SimpleSpanProcessor(exporter))

    tracer = provider.get_tracer("test-enrichment")

    # Simulate the context that the invocations handler would create:
    # baggage entries for invocation_id and session_id
    ctx = _otel_context.get_current()
    ctx = _otel_baggage.set_baggage("azure.ai.agentserver.invocation_id", "inv-enrich-42", context=ctx)
    ctx = _otel_baggage.set_baggage("azure.ai.agentserver.session_id", "sess-enrich-99", context=ctx)
    ctx = _otel_baggage.set_baggage("user.id", "test-user-789", context=ctx)
    token = _otel_context.attach(ctx)
    try:
        with tracer.start_as_current_span("handler_work"):
            pass
    finally:
        _otel_context.detach(token)

    spans = exporter.get_finished_spans()
    handler_spans = [s for s in spans if s.name == "handler_work"]
    assert handler_spans, f"Expected handler_work span, found: {[s.name for s in spans]}"

    attrs = dict(handler_spans[0].attributes)
    # invocation_id baggage → span attribute
    assert attrs.get("azure.ai.agentserver.invocations.invocation_id") == "inv-enrich-42"
    # session_id baggage → span attribute
    assert attrs.get("microsoft.session.id") == "sess-enrich-99"


# ---------------------------------------------------------------------------
# Project endpoint attribute
# ---------------------------------------------------------------------------

def test_project_endpoint_env_var():
    """FOUNDRY_PROJECT_ENDPOINT constant matches the expected env var name."""
