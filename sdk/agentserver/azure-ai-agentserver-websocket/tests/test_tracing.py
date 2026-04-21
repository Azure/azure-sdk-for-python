# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for OpenTelemetry tracing in the WebSocket websocket protocol."""
import os
import uuid
from unittest.mock import patch

import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.websocket import (
    WebsocketAgentServerHost,
    WebsocketContext,
    WebsocketError,
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
    # If a provider was already set (e.g. by test_span_parenting), add our
    # exporter to the existing provider as well, so we capture spans regardless
    # of module import order.
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
    """Create an WebsocketAgentServerHost with tracing enabled."""
    with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=test"}):
        with patch("azure.ai.agentserver.core._tracing.TracingHelper._setup_azure_monitor"):
            server = WebsocketAgentServerHost(**kwargs)

    @server.invoke_handler
    async def handle(payload: dict, context: WebsocketContext) -> dict:
        return {"echo": payload}

    return server


def _make_tracing_server_with_get_cancel(**kwargs):
    """Create a tracing-enabled server with get/cancel handlers."""
    with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=test"}):
        with patch("azure.ai.agentserver.core._tracing.TracingHelper._setup_azure_monitor"):
            server = WebsocketAgentServerHost(**kwargs)

    store: dict[str, dict] = {}

    @server.invoke_handler
    async def handle(payload: dict, context: WebsocketContext) -> dict:
        store[context.websocket_id] = payload
        return {"stored": True}

    @server.get_websocket_handler
    async def get_handler(context: WebsocketContext) -> dict:
        if context.websocket_id in store:
            return {"data": store[context.websocket_id]}
        raise WebsocketError("not_found", "Not found")

    @server.cancel_websocket_handler
    async def cancel_handler(context: WebsocketContext) -> dict:
        if context.websocket_id in store:
            del store[context.websocket_id]
            return {"status": "cancelled"}
        raise WebsocketError("not_found", "Not found")

    return server


def _make_failing_tracing_server(**kwargs):
    """Create a tracing-enabled server whose handler raises."""
    with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=test"}):
        with patch("azure.ai.agentserver.core._tracing.TracingHelper._setup_azure_monitor"):
            server = WebsocketAgentServerHost(**kwargs)

    @server.invoke_handler
    async def handle(payload: dict, context: WebsocketContext) -> dict:
        raise ValueError("tracing error test")

    return server


def _make_streaming_tracing_server(**kwargs):
    """Create a tracing-enabled server with streaming response."""
    with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=test"}):
        with patch("azure.ai.agentserver.core._tracing.TracingHelper._setup_azure_monitor"):
            server = WebsocketAgentServerHost(**kwargs)

    @server.invoke_handler
    async def handle(payload: dict, context: WebsocketContext):
        yield {"chunk": 1}
        yield {"chunk": 2}

    return server


# ---------------------------------------------------------------------------
# Tracing disabled by default
# ---------------------------------------------------------------------------

def test_tracing_disabled_by_default():
    """No spans are created when tracing is not enabled."""
    if _MODULE_EXPORTER:
        _MODULE_EXPORTER.clear()

    app = WebsocketAgentServerHost()

    @app.invoke_handler
    async def handle(payload: dict, context: WebsocketContext) -> dict:
        return {"ok": True}

    client = TestClient(app)
    with client.websocket_connect("/websocket/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        ws.receive_json()

    spans = _get_spans()
    invoke_spans = [s for s in spans if "invoke_agent" in s.name]
    assert len(invoke_spans) == 0


# ---------------------------------------------------------------------------
# Tracing enabled creates invoke span
# ---------------------------------------------------------------------------

def test_tracing_enabled_creates_invoke_span():
    """Tracing enabled creates a span named 'invoke_agent'."""
    server = _make_tracing_server()
    client = TestClient(server)
    with client.websocket_connect("/websocket/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        ws.receive_json()

    spans = _get_spans()
    invoke_spans = [s for s in spans if "invoke_agent" in s.name]
    assert len(invoke_spans) >= 1
    assert invoke_spans[0].name.startswith("invoke_agent")


# ---------------------------------------------------------------------------
# Invoke error records exception
# ---------------------------------------------------------------------------

def test_invoke_error_records_exception():
    """When handler raises, the span records the exception."""
    server = _make_failing_tracing_server()
    client = TestClient(server)
    with client.websocket_connect("/websocket/ws") as ws:
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

def test_get_websocket_creates_span():
    """get_websocket creates a span."""
    server = _make_tracing_server_with_get_cancel()
    client = TestClient(server)
    with client.websocket_connect("/websocket/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {"key": "data"}})
        invoke_resp = ws.receive_json()
        inv_id = invoke_resp["websocket_id"]

        ws.send_json({"action": "get_websocket", "websocket_id": inv_id})
        ws.receive_json()

    spans = _get_spans()
    get_spans = [s for s in spans if "get_websocket" in s.name]
    assert len(get_spans) >= 1


def test_cancel_websocket_creates_span():
    """cancel_websocket creates a span."""
    server = _make_tracing_server_with_get_cancel()
    client = TestClient(server)
    with client.websocket_connect("/websocket/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {"key": "data"}})
        invoke_resp = ws.receive_json()
        inv_id = invoke_resp["websocket_id"]

        ws.send_json({"action": "cancel_websocket", "websocket_id": inv_id})
        ws.receive_json()

    spans = _get_spans()
    cancel_spans = [s for s in spans if "cancel_websocket" in s.name]
    assert len(cancel_spans) >= 1


# ---------------------------------------------------------------------------
# Tracing via env var
# ---------------------------------------------------------------------------

def test_tracing_via_appinsights_env_var():
    """Tracing is enabled when APPLICATIONINSIGHTS_CONNECTION_STRING is set."""
    with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=test"}):
        with patch("azure.ai.agentserver.core._tracing.TracingHelper._setup_azure_monitor"):
            app = WebsocketAgentServerHost()

    @app.invoke_handler
    async def handle(payload: dict, context: WebsocketContext) -> dict:
        return {"ok": True}

    client = TestClient(app)
    with client.websocket_connect("/websocket/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        ws.receive_json()

    spans = _get_spans()
    invoke_spans = [s for s in spans if "invoke_agent" in s.name]
    assert len(invoke_spans) >= 1


# ---------------------------------------------------------------------------
# No tracing when no endpoints configured
# ---------------------------------------------------------------------------

def test_no_tracing_when_no_endpoints():
    """Tracing is disabled when no connection string or OTLP endpoint is set."""
    env = os.environ.copy()
    env.pop("APPLICATIONINSIGHTS_CONNECTION_STRING", None)
    env.pop("OTEL_EXPORTER_OTLP_ENDPOINT", None)
    with patch.dict(os.environ, env, clear=True):
        app = WebsocketAgentServerHost()

    @app.invoke_handler
    async def handle(payload: dict, context: WebsocketContext) -> dict:
        return {"ok": True}

    if _MODULE_EXPORTER:
        _MODULE_EXPORTER.clear()

    client = TestClient(app)
    with client.websocket_connect("/websocket/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        ws.receive_json()

    spans = _get_spans()
    invoke_spans = [s for s in spans if "invoke_agent" in s.name]
    assert len(invoke_spans) == 0


# ---------------------------------------------------------------------------
# Streaming spans
# ---------------------------------------------------------------------------

def test_streaming_creates_span():
    """Streaming response creates and completes a span."""
    server = _make_streaming_tracing_server()
    client = TestClient(server)
    with client.websocket_connect("/websocket/ws") as ws:
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

def test_genai_attributes_on_invoke_span():
    """Invoke span has GenAI semantic convention attributes."""
    server = _make_tracing_server()
    client = TestClient(server)
    with client.websocket_connect("/websocket/ws") as ws:
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

def test_session_id_in_websocket_id():
    """Session ID is set as gen_ai.conversation.id on invoke span."""
    server = _make_tracing_server()
    client = TestClient(server)
    with client.websocket_connect("/websocket/ws") as ws:
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
    assert attrs.get("gen_ai.conversation.id") == "test-session"
