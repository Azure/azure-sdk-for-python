# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests that incoming W3C trace context is propagated correctly so that
child spans created by framework handlers are properly parented under the
caller's traceparent (no intermediate invoke_agent span).

These tests call the endpoint handler directly (bypassing ASGI transport)
because HTTPX's ASGITransport runs the app in a different async context,
which prevents OTel ContextVar propagation from working correctly.
"""
import os
import uuid
from unittest.mock import patch

import pytest
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from starlette.testclient import TestClient

from azure.ai.agentserver.invocations import InvocationAgentServerHost


try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider as SdkTracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

    _HAS_OTEL = True
except ImportError:
    _HAS_OTEL = False

# Provider setup is deferred to a fixture so that set_tracer_provider() is
# NOT called at import time.  Module-level calls would consume the global
# Once guard and break e2e tests that rely on the distro to set the provider.
_PROVIDER = None
_EXPORTER = None
_SETUP_DONE = False

pytestmark = pytest.mark.skipif(not _HAS_OTEL, reason="opentelemetry not installed")


@pytest.fixture(autouse=True)
def _clear():
    """Set up the OTel provider on first use, then clear spans before each test."""
    global _PROVIDER, _EXPORTER, _SETUP_DONE
    if _HAS_OTEL and not _SETUP_DONE:
        _existing = trace.get_tracer_provider()
        if hasattr(_existing, "add_span_processor"):
            _PROVIDER = _existing
        else:
            _PROVIDER = SdkTracerProvider()
            trace.set_tracer_provider(_PROVIDER)
        _EXPORTER = InMemorySpanExporter()
        _PROVIDER.add_span_processor(SimpleSpanProcessor(_EXPORTER))
        _SETUP_DONE = True
    if _EXPORTER:
        _EXPORTER.clear()


def _make_server_with_child_span():
    """Server whose handler creates a child span (simulating a framework)."""
    with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=00000000-0000-0000-0000-000000000000"}):
        with patch("azure.ai.agentserver.core._tracing._setup_distro_export", create=True):
            app = InvocationAgentServerHost()
    child_tracer = trace.get_tracer("test.framework")

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        with child_tracer.start_as_current_span("framework_invoke_agent") as _span:
            return Response(content=b"ok")

    return app


def _make_streaming_server_with_child_span():
    """Server with streaming response whose handler creates a child span."""
    with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=00000000-0000-0000-0000-000000000000"}):
        with patch("azure.ai.agentserver.core._tracing._setup_distro_export", create=True):
            app = InvocationAgentServerHost()
    child_tracer = trace.get_tracer("test.framework")

    @app.invoke_handler
    async def handle(request: Request) -> StreamingResponse:
        with child_tracer.start_as_current_span("framework_invoke_agent"):
            async def generate():
                yield b"chunk\n"
            return StreamingResponse(generate(), media_type="text/plain")

    return app


def test_framework_span_parented_under_incoming_traceparent():
    """A span created inside the handler should be parented under the incoming
    traceparent — there is no intermediate invoke_agent span."""
    trace_id_hex = uuid.uuid4().hex
    span_id_hex = uuid.uuid4().hex[:16]
    traceparent = f"00-{trace_id_hex}-{span_id_hex}-01"

    server = _make_server_with_child_span()
    client = TestClient(server)
    resp = client.post(
        "/invocations",
        content=b"test",
        headers={"traceparent": traceparent},
    )
    assert resp.status_code == 200

    spans = _EXPORTER.get_finished_spans()
    fw_spans = [s for s in spans if s.name == "framework_invoke_agent"]
    assert len(fw_spans) == 1, f"Expected framework span, got: {[s.name for s in spans]}"

    fw = fw_spans[0]
    # Framework span should share the same trace ID
    assert format(fw.context.trace_id, "032x") == trace_id_hex
    # Framework span should be parented directly under the incoming span
    assert fw.parent is not None, "Framework span has no parent"
    assert format(fw.parent.span_id, "016x") == span_id_hex


def test_framework_span_parented_under_incoming_traceparent_streaming():
    """Same parent-child relationship holds for streaming responses."""
    trace_id_hex = uuid.uuid4().hex
    span_id_hex = uuid.uuid4().hex[:16]
    traceparent = f"00-{trace_id_hex}-{span_id_hex}-01"

    server = _make_streaming_server_with_child_span()
    client = TestClient(server)
    resp = client.post(
        "/invocations",
        content=b"test",
        headers={"traceparent": traceparent},
    )
    assert resp.status_code == 200

    spans = _EXPORTER.get_finished_spans()
    fw_spans = [s for s in spans if s.name == "framework_invoke_agent"]
    assert len(fw_spans) == 1, f"Expected framework span, got: {[s.name for s in spans]}"

    fw = fw_spans[0]
    assert format(fw.context.trace_id, "032x") == trace_id_hex
    assert fw.parent is not None, "Framework span has no parent (streaming)"
    assert format(fw.parent.span_id, "016x") == span_id_hex


def test_no_invoke_agent_span_created():
    """Verify no invoke_agent span is created by the server — only framework spans."""
    server = _make_server_with_child_span()
    client = TestClient(server)
    client.post("/invocations", content=b"test")

    spans = _EXPORTER.get_finished_spans()
    # Only the framework span should exist, not an invoke_agent server span
    invoke_spans = [s for s in spans if "invoke_agent" in s.name and s.name != "framework_invoke_agent"]
    assert len(invoke_spans) == 0, f"Unexpected invoke_agent spans: {[s.name for s in invoke_spans]}"


def test_handler_span_is_child_of_real_caller_span():
    """End-to-end: create a real caller span, propagate its trace context via
    traceparent header to /invocations, create a child span inside the handler,
    and validate the handler span is a child of the caller span.

    This differs from the synthetic-traceparent tests above by using a real
    OTel span as the caller, so both the caller and handler spans appear in
    the in-memory exporter and can be validated together.
    """
    from opentelemetry.propagate import inject

    with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=00000000-0000-0000-0000-000000000000"}):
        with patch("azure.ai.agentserver.core._tracing._setup_distro_export", create=True):
            app = InvocationAgentServerHost()

    handler_tracer = trace.get_tracer("test.handler")

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        with handler_tracer.start_as_current_span("HandleInvocation"):
            body = await request.body()
            return Response(content=body, media_type="application/octet-stream")

    # 1. Create a real caller span to act as the external parent
    caller_tracer = trace.get_tracer("test.caller")
    with caller_tracer.start_as_current_span("CallerOperation") as caller_span:
        caller_trace_id = format(caller_span.context.trace_id, "032x")
        caller_span_id = format(caller_span.context.span_id, "016x")

        # 2. Inject the caller span's context into HTTP headers (traceparent)
        headers: dict[str, str] = {}
        inject(headers)

        # 3. Send the request with the caller's trace context
        client = TestClient(app)
        resp = client.post("/invocations", content=b"e2e-test", headers=headers)
        assert resp.status_code == 200

    # 4. Validate the span hierarchy
    spans = _EXPORTER.get_finished_spans()
    span_by_name = {s.name: s for s in spans}

    assert "CallerOperation" in span_by_name, (
        f"Caller span not found. Spans: {[s.name for s in spans]}"
    )
    assert "HandleInvocation" in span_by_name, (
        f"Handler span not found. Spans: {[s.name for s in spans]}"
    )

    caller = span_by_name["CallerOperation"]
    handler = span_by_name["HandleInvocation"]

    # Handler span must share the same trace ID as the caller
    assert format(handler.context.trace_id, "032x") == caller_trace_id, (
        "Handler span has a different trace ID — trace context was not propagated"
    )

    # Handler span must be a child of the caller span
    assert handler.parent is not None, "Handler span has no parent"
    assert format(handler.parent.span_id, "016x") == caller_span_id, (
        f"Handler span parent {format(handler.parent.span_id, '016x')} "
        f"!= caller span {caller_span_id} — span parenting is broken"
    )
