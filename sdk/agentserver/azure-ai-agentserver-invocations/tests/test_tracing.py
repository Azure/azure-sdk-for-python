# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for OpenTelemetry tracing in the invocations protocol."""
import os
import uuid
from unittest.mock import patch

import pytest
from starlette.testclient import TestClient
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from azure.ai.agentserver.invocations import InvocationAgentServerHost


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

    app = InvocationAgentServerHost()

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
        app = InvocationAgentServerHost()

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
    """Server propagates traceparent header into OTel context for framework spans."""
    from opentelemetry import trace as _trace

    trace_id_hex = uuid.uuid4().hex
    span_id_hex = uuid.uuid4().hex[:16]
    traceparent = f"00-{trace_id_hex}-{span_id_hex}-01"

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
    client.post(
        "/invocations",
        content=b"test",
        headers={"traceparent": traceparent},
    )

    assert captured_trace_id == trace_id_hex
    assert captured_parent_id == span_id_hex


# ---------------------------------------------------------------------------
# Streaming responses still work
# ---------------------------------------------------------------------------

def test_streaming_returns_response():
    """Streaming response is returned successfully."""
    server = _make_streaming_tracing_server()
    client = TestClient(server)
    resp = client.post("/invocations", content=b"test")
    assert resp.status_code == 200


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
    incoming traceparent (no intermediate invoke_agent span)."""
    from opentelemetry import trace as _trace

    trace_id_hex = uuid.uuid4().hex
    span_id_hex = uuid.uuid4().hex[:16]
    traceparent = f"00-{trace_id_hex}-{span_id_hex}-01"

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
    client.post(
        "/invocations",
        content=b"test",
        headers={
            "traceparent": traceparent,
            "baggage": "user.id=test-user-456",
        },
    )

    # Framework span inherits trace ID and parents directly under incoming span
    assert captured_trace_id == trace_id_hex
    assert captured_parent_id == span_id_hex


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
    """Incoming W3C baggage entries (including invocation_id) are stamped
    as span attributes on spans created inside the handler via the
    FoundryEnrichmentSpanProcessor."""
    from opentelemetry import trace as _trace
    from azure.ai.agentserver.core._tracing import _FoundryEnrichmentSpanProcessor

    # Add the enrichment processor to the test provider so baggage → span attrs works
    proc = _FoundryEnrichmentSpanProcessor()
    _MODULE_PROVIDER.add_span_processor(proc)

    with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=00000000-0000-0000-0000-000000000000"}):
        with patch("azure.ai.agentserver.core._tracing._setup_distro_export", create=True):
            server = InvocationAgentServerHost()

    @server.invoke_handler
    async def handle(request: Request) -> Response:
        tracer = _trace.get_tracer("test-handler")
        with tracer.start_as_current_span("handler_work"):
            body = await request.body()
        return Response(content=body, media_type="application/octet-stream")

    trace_id_hex = uuid.uuid4().hex
    span_id_hex = uuid.uuid4().hex[:16]
    traceparent = f"00-{trace_id_hex}-{span_id_hex}-01"

    client = TestClient(server)
    client.post(
        "/invocations",
        content=b"test",
        headers={
            "traceparent": traceparent,
            "baggage": "user.id=test-user-789,custom.key=custom-value",
        },
    )

    spans = _get_spans()
    handler_spans = [s for s in spans if s.name == "handler_work"]
    assert handler_spans, f"Expected handler_work span, found: {[s.name for s in spans]}"

    attrs = dict(handler_spans[0].attributes)
    # invocation_id is set by the invocations package and stamped by the enricher
    assert "azure.ai.agentserver.invocations.invocation_id" in attrs
    # session_id is also set as baggage and stamped by the enricher
    assert "microsoft.session.id" in attrs


# ---------------------------------------------------------------------------
# Project endpoint attribute
# ---------------------------------------------------------------------------

def test_project_endpoint_env_var():
    """FOUNDRY_PROJECT_ENDPOINT constant matches the expected env var name."""

