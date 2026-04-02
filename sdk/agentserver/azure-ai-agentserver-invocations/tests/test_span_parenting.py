# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests that the invoke_agent span is set as the current span in context,
so that child spans created by framework handlers are correctly parented."""
import os
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse

from azure.ai.agentserver.invocations import InvocationAgentServerHost


try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider as SdkTracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

    _HAS_OTEL = True
except ImportError:
    _HAS_OTEL = False

if _HAS_OTEL:
    _EXPORTER = InMemorySpanExporter()
    _PROVIDER = SdkTracerProvider()
    _PROVIDER.add_span_processor(SimpleSpanProcessor(_EXPORTER))
    trace.set_tracer_provider(_PROVIDER)
else:
    _EXPORTER = None

pytestmark = pytest.mark.skipif(not _HAS_OTEL, reason="opentelemetry not installed")


@pytest.fixture(autouse=True)
def _clear():
    if _EXPORTER:
        _EXPORTER.clear()


def _get_spans():
    return list(_EXPORTER.get_finished_spans()) if _EXPORTER else []


def _make_server_with_child_span():
    """Server whose handler creates a child span (simulating a framework)."""
    with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=test"}):
        with patch("azure.ai.agentserver.core._tracing.TracingHelper._setup_azure_monitor"):
            app = InvocationAgentServerHost()
    child_tracer = trace.get_tracer("test.framework")

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        # Simulate a framework creating its own invoke_agent span
        with child_tracer.start_as_current_span("framework_invoke_agent") as _span:
            return Response(content=b"ok")

    return app


def _make_streaming_server_with_child_span():
    """Server with streaming response whose handler creates a child span."""
    with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=test"}):
        with patch("azure.ai.agentserver.core._tracing.TracingHelper._setup_azure_monitor"):
            app = InvocationAgentServerHost()
    child_tracer = trace.get_tracer("test.framework")

    @app.invoke_handler
    async def handle(request: Request) -> StreamingResponse:
        with child_tracer.start_as_current_span("framework_invoke_agent"):
            async def generate():
                yield b"chunk\n"
            return StreamingResponse(generate(), media_type="text/plain")

    return app


@pytest.mark.asyncio
async def test_framework_span_is_child_of_invoke_span():
    """A span created inside the handler should be a child of the
    agentserver invoke_agent span, not a sibling."""
    server = _make_server_with_child_span()
    transport = ASGITransport(app=server)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.post("/invocations", content=b"test")

    spans = _get_spans()
    parent_spans = [s for s in spans if "invoke_agent" in s.name]
    child_spans = [s for s in spans if s.name == "framework_invoke_agent"]

    assert len(parent_spans) >= 1, f"Expected invoke_agent span, got: {[s.name for s in spans]}"
    assert len(child_spans) == 1, f"Expected framework span, got: {[s.name for s in spans]}"

    parent = parent_spans[0]
    child = child_spans[0]

    # The child span's parent should be the agentserver invoke_agent span
    assert child.parent is not None, "Framework span has no parent — it's a root span (sibling)"
    assert child.parent.span_id == parent.context.span_id, (
        f"Framework span parent ({format(child.parent.span_id, '016x')}) "
        f"!= invoke_agent span ({format(parent.context.span_id, '016x')}). "
        "Spans are siblings, not parent-child."
    )


@pytest.mark.asyncio
async def test_framework_span_is_child_streaming():
    """Same parent-child relationship holds for streaming responses."""
    server = _make_streaming_server_with_child_span()
    transport = ASGITransport(app=server)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations", content=b"test")
        assert resp.status_code == 200

    spans = _get_spans()
    parent_spans = [s for s in spans if "invoke_agent" in s.name]
    child_spans = [s for s in spans if s.name == "framework_invoke_agent"]

    assert len(parent_spans) >= 1
    assert len(child_spans) == 1

    parent = parent_spans[0]
    child = child_spans[0]

    assert child.parent is not None, "Framework span has no parent in streaming case"
    assert child.parent.span_id == parent.context.span_id
