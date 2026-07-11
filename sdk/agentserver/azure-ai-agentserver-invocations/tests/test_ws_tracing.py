# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for OpenTelemetry propagation through ``/invocations_ws``."""
from opentelemetry import baggage as _otel_baggage
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from starlette.testclient import TestClient
from starlette.websockets import WebSocket

from azure.ai.agentserver.core._tracing import _FoundryEnrichmentSpanProcessor
from azure.ai.agentserver.invocations import InvocationAgentServerHost


def test_ws_merges_incoming_and_session_baggage(monkeypatch):
    """Caller baggage and the platform session ID are available to the handler."""
    monkeypatch.setenv("FOUNDRY_AGENT_SESSION_ID", "ws-session-123")
    captured_baggage = {}
    app = InvocationAgentServerHost(configure_observability=None)

    @app.ws_handler
    async def handler(websocket: WebSocket) -> None:
        captured_baggage.update(_otel_baggage.get_all())
        await websocket.send_text("ready")

    client = TestClient(app)
    with client.websocket_connect(
        "/invocations_ws",
        headers={"baggage": "caller.key=caller-value"},
    ) as websocket:
        assert websocket.receive_text() == "ready"

    assert captured_baggage["caller.key"] == "caller-value"
    assert (
        captured_baggage["azure.ai.agentserver.session_id"]
        == "ws-session-123"
    )


def test_ws_handler_span_has_a365_context(monkeypatch):
    """WS child spans inherit trace context and A365 correlation attributes."""
    monkeypatch.setenv("FOUNDRY_AGENT_SESSION_ID", "ws-session-456")

    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(_FoundryEnrichmentSpanProcessor())
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer("test.ws.handler")

    app = InvocationAgentServerHost(configure_observability=None)

    @app.ws_handler
    async def handler(websocket: WebSocket) -> None:
        with tracer.start_as_current_span("ws_handler_work"):
            await websocket.send_text("ready")

    trace_id = "0af7651916cd43dd8448eb211c80319c"
    parent_span_id = "b7ad6b7169203331"
    traceparent = f"00-{trace_id}-{parent_span_id}-01"

    client = TestClient(app)
    with client.websocket_connect(
        "/invocations_ws",
        headers={"traceparent": traceparent},
    ) as websocket:
        assert websocket.receive_text() == "ready"

    spans = exporter.get_finished_spans()
    assert len(spans) == 1
    span = spans[0]
    assert format(span.context.trace_id, "032x") == trace_id
    assert span.parent is not None
    assert format(span.parent.span_id, "016x") == parent_span_id
    assert span.attributes["microsoft.session.id"] == "ws-session-456"
