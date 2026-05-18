# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the per-turn ``ws_invocation`` helper.

Each ``ws_invocation()`` block opens an ``invoke_agent`` span (mirroring the
HTTP ``POST /invocations`` model) parented to the connection-level
``websocket_session`` span, mints an ``invocation_id`` for the turn, and
ensures the OTel context is current for every ``await`` inside the block.
"""
import os
from unittest.mock import patch

from opentelemetry import trace as otel_trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from starlette.testclient import TestClient
from starlette.websockets import WebSocket

from azure.ai.agentserver.invocations import InvocationAgentServerHost
from azure.ai.agentserver.invocations._constants import InvocationsWSConstants


# ---------------------------------------------------------------------------
# Test fixture: module-scoped OTel provider + in-memory exporter
# ---------------------------------------------------------------------------

_EXPORTER = InMemorySpanExporter()
_PROVIDER = TracerProvider()
_PROVIDER.add_span_processor(SimpleSpanProcessor(_EXPORTER))
otel_trace.set_tracer_provider(_PROVIDER)


def _make_server_with_invocations() -> InvocationAgentServerHost:
    """Build a tracing-enabled WS host whose handler opens one ``invoke_agent``
    span per inbound text frame via ``ws_invocation``."""
    with patch.dict(
        os.environ,
        {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=00000000-0000-0000-0000-000000000000"},
    ):
        with patch("azure.ai.agentserver.core._tracing._setup_distro_export", create=True):
            server = InvocationAgentServerHost()

    @server.ws_handler
    async def handler(websocket: WebSocket) -> None:
        async for msg in websocket.iter_text():
            async with server.ws_invocation(websocket) as turn:
                await websocket.send_json(
                    {"invocation_id": turn.invocation_id, "echo": msg}
                )

    return server


def _get_spans():
    return _EXPORTER.get_finished_spans()


def _session_spans(spans):
    return [s for s in spans if "websocket_session" in s.name]


def _invoke_spans(spans):
    return [s for s in spans if "invoke_agent" in s.name]


# ---------------------------------------------------------------------------
# Span shape
# ---------------------------------------------------------------------------

def test_ws_invocation_opens_invoke_agent_span_per_turn():
    """One ``invoke_agent`` span is recorded per ``ws_invocation`` block."""
    _EXPORTER.clear()
    server = _make_server_with_invocations()
    client = TestClient(server)
    with client.websocket_connect("/invocations_ws") as ws:
        ws.send_text("hi")
        ws.receive_json()
        ws.send_text("again")
        ws.receive_json()

    spans = _get_spans()
    invokes = _invoke_spans(spans)
    assert len(invokes) == 2, f"expected 2 invoke_agent spans, got {[s.name for s in spans]}"


def test_ws_invocation_id_is_set_on_invoke_span():
    """``invoke_agent`` span carries the per-turn ``invocation_id``."""
    _EXPORTER.clear()
    server = _make_server_with_invocations()
    client = TestClient(server)
    with client.websocket_connect("/invocations_ws") as ws:
        ws.send_text("hi")
        payload = ws.receive_json()

    invokes = _invoke_spans(_get_spans())
    assert invokes
    span = invokes[-1]
    attr = span.attributes.get(InvocationsWSConstants.ATTR_SPAN_INVOCATION_ID)
    assert attr == payload["invocation_id"]


def test_ws_invocation_unique_per_turn():
    """Each turn mints a fresh ``invocation_id``."""
    _EXPORTER.clear()
    server = _make_server_with_invocations()
    client = TestClient(server)
    with client.websocket_connect("/invocations_ws") as ws:
        ws.send_text("a")
        a = ws.receive_json()["invocation_id"]
        ws.send_text("b")
        b = ws.receive_json()["invocation_id"]
        ws.send_text("c")
        c = ws.receive_json()["invocation_id"]

    assert len({a, b, c}) == 3


def test_ws_invocation_span_is_child_of_websocket_session():
    """``invoke_agent`` is parented to the connection-level ``websocket_session``."""
    _EXPORTER.clear()
    server = _make_server_with_invocations()
    client = TestClient(server)
    with client.websocket_connect("/invocations_ws") as ws:
        ws.send_text("hi")
        ws.receive_json()

    spans = _get_spans()
    sessions = _session_spans(spans)
    invokes = _invoke_spans(spans)
    assert sessions and invokes
    session_span = sessions[-1]
    invoke_span = invokes[-1]
    # Parent-child via OTel SpanContext.span_id linkage.
    assert invoke_span.parent is not None
    assert invoke_span.parent.span_id == session_span.context.span_id


# ---------------------------------------------------------------------------
# Session ID propagation
# ---------------------------------------------------------------------------

def test_ws_invocation_inherits_connection_session_id(monkeypatch):
    """``ws_invocation`` defaults to ``app.config.session_id`` when set."""
    monkeypatch.setenv("FOUNDRY_AGENT_SESSION_ID", "fixed-session")
    _EXPORTER.clear()
    server = _make_server_with_invocations()
    client = TestClient(server)
    with client.websocket_connect("/invocations_ws") as ws:
        ws.send_text("hi")
        ws.receive_json()

    invokes = _invoke_spans(_get_spans())
    assert invokes
    assert (
        invokes[-1].attributes.get(InvocationsWSConstants.ATTR_SPAN_SESSION_ID)
        == "fixed-session"
    )


# ---------------------------------------------------------------------------
# OTel context propagation through awaits
# ---------------------------------------------------------------------------

def test_ws_invocation_propagates_otel_context_across_awaits():
    """A user-opened child span inside ``ws_invocation`` is parented to
    the per-turn ``invoke_agent`` span (proves OTel context survives awaits)."""
    _EXPORTER.clear()
    with patch.dict(
        os.environ,
        {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=00000000-0000-0000-0000-000000000000"},
    ):
        with patch("azure.ai.agentserver.core._tracing._setup_distro_export", create=True):
            server = InvocationAgentServerHost()

    tracer = otel_trace.get_tracer("test")

    @server.ws_handler
    async def handler(websocket: WebSocket) -> None:
        async for msg in websocket.iter_text():
            async with server.ws_invocation(websocket):
                # User-opened child span — must parent to the invoke_agent span.
                with tracer.start_as_current_span("user_work"):
                    await websocket.send_text(msg)

    client = TestClient(server)
    with client.websocket_connect("/invocations_ws") as ws:
        ws.send_text("hi")
        ws.receive_text()

    spans = _get_spans()
    invoke = [s for s in spans if s.name.startswith("invoke_agent") or "invoke_agent" in s.name]
    user_work = [s for s in spans if s.name == "user_work"]
    assert invoke and user_work
    assert user_work[-1].parent is not None
    assert user_work[-1].parent.span_id == invoke[-1].context.span_id
