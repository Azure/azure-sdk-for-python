# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for OpenTelemetry tracing on the ``invocations_ws`` protocol.

These mirror :mod:`tests.test_tracing` (HTTP /invocations) but target the
WebSocket transport: span creation, GenAI attributes, traceparent
propagation, close-code recording, and error recording.
"""
import os
import uuid
from unittest.mock import patch

import pytest
from starlette.testclient import TestClient
from starlette.websockets import WebSocket, WebSocketDisconnect

from azure.ai.agentserver.invocations import InvocationAgentServerHost


# ---------------------------------------------------------------------------
# Lazy OTel setup with in-memory exporter (mirrors tests/test_tracing.py)
# ---------------------------------------------------------------------------
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


def _ws_session_spans(spans):
    """Filter spans created by the ``/invocations_ws`` route."""
    return [s for s in spans if "websocket_session" in s.name]


# ---------------------------------------------------------------------------
# Helpers: tracing-enabled servers
# ---------------------------------------------------------------------------

def _make_tracing_ws_server(**kwargs) -> InvocationAgentServerHost:
    """Build an echo WS host with tracing enabled."""
    with patch.dict(
        os.environ,
        {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=00000000-0000-0000-0000-000000000000"},
    ):
        with patch("azure.ai.agentserver.core._tracing._setup_distro_export"):
            server = InvocationAgentServerHost(**kwargs)

    @server.ws_handler
    async def handler(websocket: WebSocket) -> None:
        async for msg in websocket.iter_text():
            await websocket.send_text(msg)

    return server


def _make_failing_tracing_ws_server(**kwargs) -> InvocationAgentServerHost:
    """Build a WS host whose handler raises after one received frame."""
    with patch.dict(
        os.environ,
        {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=00000000-0000-0000-0000-000000000000"},
    ):
        with patch("azure.ai.agentserver.core._tracing._setup_distro_export"):
            server = InvocationAgentServerHost(**kwargs)

    @server.ws_handler
    async def handler(websocket: WebSocket) -> None:
        await websocket.receive_text()
        raise ValueError("ws tracing error test")

    return server


def _make_tracing_ws_no_handler(**kwargs) -> InvocationAgentServerHost:
    """Build a tracing-enabled host with NO ws_handler registered."""
    with patch.dict(
        os.environ,
        {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=00000000-0000-0000-0000-000000000000"},
    ):
        with patch("azure.ai.agentserver.core._tracing._setup_distro_export"):
            return InvocationAgentServerHost(**kwargs)


# ---------------------------------------------------------------------------
# Span creation
# ---------------------------------------------------------------------------

def test_ws_tracing_creates_websocket_session_span():
    """A WS connection creates a span named ``websocket_session``."""
    server = _make_tracing_ws_server()
    client = TestClient(server)
    with client.websocket_connect("/invocations_ws") as ws:
        ws.send_text("hello")
        ws.receive_text()

    spans = _ws_session_spans(_get_spans())
    assert len(spans) == 1
    assert spans[0].name.startswith("websocket_session")


def test_ws_tracing_disabled_by_default_still_creates_span():
    """Even without an exporter, the global tracer creates the span."""
    if _MODULE_EXPORTER:
        _MODULE_EXPORTER.clear()

    app = InvocationAgentServerHost()

    @app.ws_handler
    async def handler(websocket: WebSocket) -> None:
        await websocket.send_text("ready")

    client = TestClient(app)
    with client.websocket_connect("/invocations_ws") as ws:
        ws.receive_text()

    spans = _ws_session_spans(_get_spans())
    assert len(spans) >= 1


# ---------------------------------------------------------------------------
# GenAI attributes (parity with test_genai_attributes_on_invoke_span)
# ---------------------------------------------------------------------------

def test_ws_span_has_genai_attributes():
    """WS span carries the standard GenAI / service.name attributes."""
    server = _make_tracing_ws_server()
    client = TestClient(server)
    with client.websocket_connect("/invocations_ws") as ws:
        ws.send_text("hi")
        ws.receive_text()

    spans = _ws_session_spans(_get_spans())
    assert spans
    attrs = dict(spans[0].attributes)
    assert attrs.get("gen_ai.system") == "azure.ai.agentserver"
    assert attrs.get("gen_ai.provider.name") == "AzureAI Hosted Agents"
    assert attrs.get("service.name") == "azure.ai.agentserver"


def test_ws_span_operation_name_attribute():
    """``gen_ai.operation.name`` on the WS span is ``websocket_session``."""
    server = _make_tracing_ws_server()
    client = TestClient(server)
    with client.websocket_connect("/invocations_ws") as ws:
        ws.send_text("hi")
        ws.receive_text()

    spans = _ws_session_spans(_get_spans())
    attrs = dict(spans[0].attributes)
    assert attrs.get("gen_ai.operation.name") == "websocket_session"


# ---------------------------------------------------------------------------
# Session ID attribute (parity with test_session_id_in_conversation_id)
# ---------------------------------------------------------------------------

def test_ws_session_id_attribute_set_on_span():
    """The auto-generated session_id is stored on the span under both keys."""
    server = _make_tracing_ws_server()
    client = TestClient(server)
    with client.websocket_connect("/invocations_ws") as ws:
        ws.send_text("hi")
        ws.receive_text()

    spans = _ws_session_spans(_get_spans())
    attrs = dict(spans[0].attributes)
    # WS-specific key
    ws_session = attrs.get("azure.ai.agentserver.invocations_ws.session_id")
    # General session key (shared with HTTP)
    ms_session = attrs.get("microsoft.session.id")
    assert ws_session and isinstance(ws_session, str)
    uuid.UUID(ws_session)
    assert ms_session == ws_session


def test_ws_session_id_is_unique_per_span():
    """Two WS connections produce two distinct session IDs on their spans."""
    server = _make_tracing_ws_server()
    client = TestClient(server)
    for _ in range(2):
        with client.websocket_connect("/invocations_ws") as ws:
            ws.send_text("x")
            ws.receive_text()

    spans = _ws_session_spans(_get_spans())
    assert len(spans) == 2
    session_ids = {dict(s.attributes).get("azure.ai.agentserver.invocations_ws.session_id") for s in spans}
    assert len(session_ids) == 2


# ---------------------------------------------------------------------------
# Close-code / duration attributes (WS-specific)
# ---------------------------------------------------------------------------

def test_ws_span_records_close_code_1000_on_clean_return():
    """A handler that returns normally records ws.close_code = 1000."""
    server = _make_tracing_ws_server()
    client = TestClient(server)
    with client.websocket_connect("/invocations_ws") as ws:
        ws.send_text("hi")
        ws.receive_text()

    spans = _ws_session_spans(_get_spans())
    attrs = dict(spans[0].attributes)
    assert attrs.get("azure.ai.agentserver.invocations_ws.close_code") == 1000


def test_ws_span_records_close_code_1011_on_handler_exception():
    """A failing handler records ws.close_code = 1011."""
    server = _make_failing_tracing_ws_server()
    client = TestClient(server)
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/invocations_ws") as ws:
            ws.send_text("trigger")
            ws.receive_text()

    spans = _ws_session_spans(_get_spans())
    attrs = dict(spans[0].attributes)
    assert attrs.get("azure.ai.agentserver.invocations_ws.close_code") == 1011


def test_ws_span_records_duration_ms():
    """``azure.ai.agentserver.invocations_ws.duration_ms`` is set as a non-negative integer."""
    server = _make_tracing_ws_server()
    client = TestClient(server)
    with client.websocket_connect("/invocations_ws") as ws:
        ws.send_text("hi")
        ws.receive_text()

    spans = _ws_session_spans(_get_spans())
    attrs = dict(spans[0].attributes)
    duration_ms = attrs.get("azure.ai.agentserver.invocations_ws.duration_ms")
    assert isinstance(duration_ms, int)
    assert duration_ms >= 0


def test_ws_span_records_client_close_code():
    """A client closing with a custom code lands on the span as ws.close_code."""
    server_with_recv = _make_tracing_ws_server()

    # Override the handler so receive_text raises with the client's code
    # (iter_text swallows WebSocketDisconnect — see _invocation_ws docs).
    @server_with_recv.ws_handler
    async def handler(websocket: WebSocket) -> None:
        while True:
            await websocket.receive_text()

    client = TestClient(server_with_recv)
    with client.websocket_connect("/invocations_ws") as ws:
        ws.send_text("ping")
        ws.close(code=4010)

    spans = _ws_session_spans(_get_spans())
    attrs = dict(spans[0].attributes)
    assert attrs.get("azure.ai.agentserver.invocations_ws.close_code") == 4010


# ---------------------------------------------------------------------------
# Error recording on span (parity with test_invoke_error_records_exception)
# ---------------------------------------------------------------------------

def test_ws_handler_exception_records_exception_on_span():
    """When the handler raises, the span has ERROR status and exception event."""
    server = _make_failing_tracing_ws_server()
    client = TestClient(server)
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/invocations_ws") as ws:
            ws.send_text("trigger")
            ws.receive_text()

    spans = _ws_session_spans(_get_spans())
    assert spans
    span = spans[0]
    assert span.status.status_code.name == "ERROR"
    # Exception is recorded as an event by record_error.
    event_names = [e.name for e in span.events]
    assert "exception" in event_names
    # Exactly one exception event — belt-and-suspenders against future
    # double-recording on the same span.
    assert event_names.count("exception") == 1


def test_ws_no_handler_produces_no_span():
    """Without @ws_handler the route is absent, so no WS span is created."""
    app = _make_tracing_ws_no_handler()
    client = TestClient(app)
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/invocations_ws"):
            pass

    spans = _ws_session_spans(_get_spans())
    assert spans == []


# ---------------------------------------------------------------------------
# Traceparent propagation (parity with test_traceparent_propagation)
# ---------------------------------------------------------------------------

def test_ws_traceparent_propagation():
    """A client-supplied traceparent header parents the WS span."""
    server = _make_tracing_ws_server()
    trace_id_hex = uuid.uuid4().hex
    span_id_hex = uuid.uuid4().hex[:16]
    traceparent = f"00-{trace_id_hex}-{span_id_hex}-01"

    client = TestClient(server)
    with client.websocket_connect(
        "/invocations_ws",
        headers={"traceparent": traceparent},
    ) as ws:
        ws.send_text("hi")
        ws.receive_text()

    spans = _ws_session_spans(_get_spans())
    assert spans
    actual_trace_id = format(spans[0].context.trace_id, "032x")
    assert actual_trace_id == trace_id_hex


# ---------------------------------------------------------------------------
# Agent name / version in span name (parity with test_agent_name_in_span_name)
# ---------------------------------------------------------------------------

def test_ws_agent_name_and_version_in_span_name():
    """``FOUNDRY_AGENT_NAME``/``_VERSION`` appear in the WS span name."""
    with patch.dict(
        os.environ,
        {
            "FOUNDRY_AGENT_NAME": "my-ws-agent",
            "FOUNDRY_AGENT_VERSION": "3.1",
        },
    ):
        server = _make_tracing_ws_server()

    client = TestClient(server)
    with client.websocket_connect("/invocations_ws") as ws:
        ws.send_text("hi")
        ws.receive_text()

    spans = _ws_session_spans(_get_spans())
    assert spans
    name = spans[0].name
    assert "my-ws-agent" in name
    assert "3.1" in name


def test_ws_agent_name_only_in_span_name(monkeypatch):
    """Agent name without version still appears in span name."""
    monkeypatch.setenv("FOUNDRY_AGENT_NAME", "ws-solo")
    monkeypatch.delenv("FOUNDRY_AGENT_VERSION", raising=False)
    server = _make_tracing_ws_server()

    client = TestClient(server)
    with client.websocket_connect("/invocations_ws") as ws:
        ws.send_text("hi")
        ws.receive_text()

    spans = _ws_session_spans(_get_spans())
    assert spans
    assert "ws-solo" in spans[0].name


# ---------------------------------------------------------------------------
# Span kind / shape
# ---------------------------------------------------------------------------

def test_ws_span_kind_is_server():
    """The WS span is created with ``kind=SERVER``."""
    server = _make_tracing_ws_server()
    client = TestClient(server)
    with client.websocket_connect("/invocations_ws") as ws:
        ws.send_text("hi")
        ws.receive_text()

    spans = _ws_session_spans(_get_spans())
    assert spans
    # SpanKind.SERVER == 2; compare by name to avoid pinning the enum value.
    assert spans[0].kind.name == "SERVER"


def test_ws_span_has_no_parent_when_no_traceparent():
    """Without traceparent the WS span is a root span (parent is None)."""
    server = _make_tracing_ws_server()
    client = TestClient(server)
    with client.websocket_connect("/invocations_ws") as ws:
        ws.send_text("hi")
        ws.receive_text()

    spans = _ws_session_spans(_get_spans())
    assert spans
    assert spans[0].parent is None


# ---------------------------------------------------------------------------
# Coexistence: invoke + ws spans on the same host
# ---------------------------------------------------------------------------

def test_ws_and_invoke_spans_coexist():
    """A host serving both HTTP /invocations and /invocations_ws produces both spans."""
    from starlette.requests import Request
    from starlette.responses import Response

    with patch.dict(
        os.environ,
        {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=00000000-0000-0000-0000-000000000000"},
    ):
        with patch("azure.ai.agentserver.core._tracing._setup_distro_export"):
            server = InvocationAgentServerHost()

    @server.invoke_handler
    async def http_handler(request: Request) -> Response:
        return Response(content=b"ok")

    @server.ws_handler
    async def ws_handler(websocket: WebSocket) -> None:
        async for msg in websocket.iter_text():
            await websocket.send_text(msg)

    client = TestClient(server)
    client.post("/invocations", content=b"data")
    with client.websocket_connect("/invocations_ws") as ws:
        ws.send_text("hi")
        ws.receive_text()

    spans = _get_spans()
    invoke = [s for s in spans if "invoke_agent" in s.name]
    ws_spans = _ws_session_spans(spans)
    assert invoke and ws_spans
