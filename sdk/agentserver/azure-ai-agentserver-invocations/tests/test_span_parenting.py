# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests that the invoke_agent span is set as the current span in context,
so that child spans created by framework handlers are correctly parented.

These tests call the endpoint handler directly (bypassing ASGI transport)
because HTTPX's ASGITransport runs the app in a different async context,
which prevents OTel ContextVar propagation from working correctly.
"""
import os
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


def _get_spans():
    return list(_EXPORTER.get_finished_spans()) if _EXPORTER else []


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


def _assert_child_parented(spans, streaming: bool = False):
    """Assert the framework span is a child of the invoke_agent span."""
    parent_spans = [s for s in spans if "invoke_agent" in s.name and s.name != "framework_invoke_agent"]
    child_spans = [s for s in spans if s.name == "framework_invoke_agent"]

    assert len(parent_spans) >= 1, f"Expected invoke_agent span, got: {[s.name for s in spans]}"
    assert len(child_spans) == 1, f"Expected framework span, got: {[s.name for s in spans]}"

    parent = parent_spans[0]
    child = child_spans[0]

    label = "streaming" if streaming else "non-streaming"
    assert child.parent is not None, f"Framework span has no parent in {label} case"
    assert child.parent.span_id == parent.context.span_id, (
        f"Framework span parent ({format(child.parent.span_id, '016x')}) "
        f"!= invoke_agent span ({format(parent.context.span_id, '016x')}). "
        f"Spans are siblings, not parent-child ({label})."
    )


def test_framework_span_is_child_of_invoke_span():
    """A span created inside the handler should be a child of the
    agentserver invoke_agent span, not a sibling."""
    server = _make_server_with_child_span()
    # TestClient runs synchronously in the same thread context,
    # so OTel ContextVar propagation works correctly.
    client = TestClient(server)
    resp = client.post("/invocations", content=b"test")
    assert resp.status_code == 200

    _assert_child_parented(_get_spans(), streaming=False)


def test_framework_span_is_child_streaming():
    """Same parent-child relationship holds for streaming responses."""
    server = _make_streaming_server_with_child_span()
    client = TestClient(server)
    resp = client.post("/invocations", content=b"test")
    assert resp.status_code == 200

    _assert_child_parented(_get_spans(), streaming=True)
