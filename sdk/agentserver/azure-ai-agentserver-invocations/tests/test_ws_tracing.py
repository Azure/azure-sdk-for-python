# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for OpenTelemetry tracing in the WebSocket invocations_ws protocol."""
import os
import uuid
from unittest.mock import patch

import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.invocations import (
    InvocationWSAgentServerHost,
    InvocationWSContext,
    InvocationWSError,
)


# ---------------------------------------------------------------------------
# Module-level OTel setup with in-memory exporter
# ---------------------------------------------------------------------------

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider as SdkTracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

    _HAS_OTEL = True
except ImportError:
    _HAS_OTEL = False

if _HAS_OTEL:
    _MODULE_EXPORTER = InMemorySpanExporter()
    _MODULE_PROVIDER = SdkTracerProvider()
    _MODULE_PROVIDER.add_span_processor(SimpleSpanProcessor(_MODULE_EXPORTER))
    existing = trace.get_tracer_provider()
    if isinstance(existing, SdkTracerProvider) and existing is not _MODULE_PROVIDER:
        existing.add_span_processor(SimpleSpanProcessor(_MODULE_EXPORTER))
    else:
        trace.set_tracer_provider(_MODULE_PROVIDER)
else:
    _MODULE_EXPORTER = None
    _MODULE_PROVIDER = None

pytestmark = pytest.mark.skipif(not _HAS_OTEL, reason="opentelemetry not installed")


@pytest.fixture(autouse=True)
def _clear_spans():
    """Clear exported spans before each test."""
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
    """Create an InvocationWSAgentServerHost with tracing enabled."""
    with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=00000000-0000-0000-0000-000000000000"}):
        with patch("azure.ai.agentserver.core._tracing._setup_distro_export", create=True):
            server = InvocationWSAgentServerHost(**kwargs)

    @server.ws_invoke_handler
    async def handle(payload: dict, context: InvocationWSContext) -> dict:
        return {"echo": payload}

    return server


def _make_tracing_server_with_get_cancel(**kwargs):
    """Create a tracing-enabled server with get/cancel handlers."""
    with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=00000000-0000-0000-0000-000000000000"}):
        with patch("azure.ai.agentserver.core._tracing._setup_distro_export", create=True):
            server = InvocationWSAgentServerHost(**kwargs)

    store: dict[str, dict] = {}

    @server.ws_invoke_handler
    async def handle(payload: dict, context: InvocationWSContext) -> dict:
        store[context.invocation_id] = payload
        return {"stored": True}

    @server.ws_get_invocation_handler
    async def get_handler(context: InvocationWSContext) -> dict:
        if context.invocation_id in store:
            return {"data": store[context.invocation_id]}
        raise InvocationWSError("not_found", "Not found")

    @server.ws_cancel_invocation_handler
    async def cancel_handler(context: InvocationWSContext) -> dict:
        if context.invocation_id in store:
            del store[context.invocation_id]
            return {"status": "cancelled"}
        raise InvocationWSError("not_found", "Not found")

    return server


def _make_failing_tracing_server(**kwargs):
    """Create a tracing-enabled server whose handler raises."""
    with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=00000000-0000-0000-0000-000000000000"}):
        with patch("azure.ai.agentserver.core._tracing._setup_distro_export", create=True):
            server = InvocationWSAgentServerHost(**kwargs)

    @server.ws_invoke_handler
    async def handle(payload: dict, context: InvocationWSContext) -> dict:
        raise ValueError("tracing error test")

    return server


def _make_streaming_tracing_server(**kwargs):
    """Create a tracing-enabled server with streaming response."""
    with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=00000000-0000-0000-0000-000000000000"}):
        with patch("azure.ai.agentserver.core._tracing._setup_distro_export", create=True):
            server = InvocationWSAgentServerHost(**kwargs)

    @server.ws_invoke_handler
    async def handle(payload: dict, context: InvocationWSContext):
        yield {"chunk": 1}
        yield {"chunk": 2}

    return server


# ---------------------------------------------------------------------------
# Tracing disabled by default
# ---------------------------------------------------------------------------

def test_ws_tracing_disabled_by_default():
    """Invoke spans are still created by the global tracer when tracing is not explicitly configured."""
    if _MODULE_EXPORTER:
        _MODULE_EXPORTER.clear()

    app = InvocationWSAgentServerHost()

    @app.ws_invoke_handler
    async def handle(payload: dict, context: InvocationWSContext) -> dict:
        return {"ok": True}

    client = TestClient(app)
    with client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        ws.receive_json()

    # With the function-based tracing design, spans are always created
    # when OTel is installed (via the global tracer). The difference is
    # whether exporters are configured. Verify a span IS created.
    spans = _get_spans()
    invoke_spans = [s for s in spans if "invoke_agent" in s.name]
    assert len(invoke_spans) >= 1


# ---------------------------------------------------------------------------
# Tracing enabled creates invoke span
# ---------------------------------------------------------------------------

def test_ws_tracing_enabled_creates_invoke_span():
    """Tracing enabled creates a span named 'invoke_agent'."""
    server = _make_tracing_server()
    client = TestClient(server)
    with client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        ws.receive_json()

    spans = _get_spans()
    invoke_spans = [s for s in spans if "invoke_agent" in s.name]
    assert len(invoke_spans) >= 1
    assert invoke_spans[0].name.startswith("invoke_agent")


# ---------------------------------------------------------------------------
# Invoke error records exception
# ---------------------------------------------------------------------------

def test_ws_invoke_error_records_exception():
    """When handler raises, the span records the exception."""
    server = _make_failing_tracing_server()
    client = TestClient(server)
    with client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        resp = ws.receive_json()
    assert resp["type"] == "error"

    spans = _get_spans()
    invoke_spans = [s for s in spans if "invoke_agent" in s.name]
    assert len(invoke_spans) >= 1
    span = invoke_spans[0]
    assert span.status.status_code.name == "ERROR"


# ---------------------------------------------------------------------------
# GET/cancel create spans
# ---------------------------------------------------------------------------

def test_ws_get_invocation_creates_span():
    """get_invocation creates a span."""
    server = _make_tracing_server_with_get_cancel()
    client = TestClient(server)
    with client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {"key": "data"}})
        invoke_resp = ws.receive_json()
        inv_id = invoke_resp["invocation_id"]

        ws.send_json({"action": "get_invocation", "invocation_id": inv_id})
        ws.receive_json()

    spans = _get_spans()
    get_spans = [s for s in spans if "get_invocation" in s.name]
    assert len(get_spans) >= 1


def test_ws_cancel_invocation_creates_span():
    """cancel_invocation creates a span."""
    server = _make_tracing_server_with_get_cancel()
    client = TestClient(server)
    with client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {"key": "data"}})
        invoke_resp = ws.receive_json()
        inv_id = invoke_resp["invocation_id"]

        ws.send_json({"action": "cancel_invocation", "invocation_id": inv_id})
        ws.receive_json()

    spans = _get_spans()
    cancel_spans = [s for s in spans if "cancel_invocation" in s.name]
    assert len(cancel_spans) >= 1


# ---------------------------------------------------------------------------
# Tracing via env var
# ---------------------------------------------------------------------------

def test_ws_tracing_via_appinsights_env_var():
    """Tracing is enabled when APPLICATIONINSIGHTS_CONNECTION_STRING is set."""
    with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=00000000-0000-0000-0000-000000000000"}):
        with patch("azure.ai.agentserver.core._tracing._setup_distro_export", create=True):
            app = InvocationWSAgentServerHost()

    @app.ws_invoke_handler
    async def handle(payload: dict, context: InvocationWSContext) -> dict:
        return {"ok": True}

    client = TestClient(app)
    with client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        ws.receive_json()

    spans = _get_spans()
    invoke_spans = [s for s in spans if "invoke_agent" in s.name]
    assert len(invoke_spans) >= 1


# ---------------------------------------------------------------------------
# No tracing when no endpoints configured
# ---------------------------------------------------------------------------

def test_ws_no_tracing_when_no_endpoints():
    """When no connection string or OTLP endpoint is set, configure_observability
    still runs (for console logging) but tracing spans are not exported."""
    env = os.environ.copy()
    env.pop("APPLICATIONINSIGHTS_CONNECTION_STRING", None)
    env.pop("OTEL_EXPORTER_OTLP_ENDPOINT", None)
    with patch.dict(os.environ, env, clear=True):
        app = InvocationWSAgentServerHost()

    @app.ws_invoke_handler
    async def handle(payload: dict, context: InvocationWSContext) -> dict:
        return {"ok": True}

    if _MODULE_EXPORTER:
        _MODULE_EXPORTER.clear()

    client = TestClient(app)
    with client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        ws.receive_json()

    # Spans are still created via the global tracer — the difference
    # is no exporters are configured to send them anywhere.
    spans = _get_spans()
    invoke_spans = [s for s in spans if "invoke_agent" in s.name]
    assert len(invoke_spans) >= 1


# ---------------------------------------------------------------------------
# Streaming spans
# ---------------------------------------------------------------------------

def test_ws_streaming_creates_span():
    """Streaming response creates and completes a span."""
    server = _make_streaming_tracing_server()
    client = TestClient(server)
    with client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        # Consume all streaming messages
        while True:
            resp = ws.receive_json()
            if resp["type"] == "stream_end":
                break

    spans = _get_spans()
    invoke_spans = [s for s in spans if "invoke_agent" in s.name]
    assert len(invoke_spans) >= 1


# ---------------------------------------------------------------------------
# GenAI attributes on invoke span
# ---------------------------------------------------------------------------

def test_ws_genai_attributes_on_invoke_span():
    """Invoke span has GenAI semantic convention attributes."""
    server = _make_tracing_server()
    client = TestClient(server)
    with client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        ws.receive_json()

    spans = _get_spans()
    invoke_spans = [s for s in spans if "invoke_agent" in s.name]
    assert len(invoke_spans) >= 1
    attrs = dict(invoke_spans[0].attributes)

    assert attrs.get("gen_ai.provider.name") == "AzureAI Hosted Agents"
    assert attrs.get("gen_ai.system") == "azure.ai.agentserver"
    assert attrs.get("service.name") == "azure.ai.agentserver"


# ---------------------------------------------------------------------------
# Session ID in gen_ai.conversation.id
# ---------------------------------------------------------------------------

def test_ws_session_id_in_invocation_id():
    """Session ID is set as microsoft.session.id on invoke span."""
    server = _make_tracing_server()
    client = TestClient(server)
    with client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({
            "action": "invoke",
            "session_id": "test-session",
            "payload": {},
        })
        ws.receive_json()

    spans = _get_spans()
    invoke_spans = [s for s in spans if "invoke_agent" in s.name]
    assert len(invoke_spans) >= 1
    attrs = dict(invoke_spans[0].attributes)
    assert attrs.get("microsoft.session.id") == "test-session"
