# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests that agentserver spans are set as the current span in context,
so that child spans created by framework handlers are correctly parented.

These tests use Starlette's ``TestClient`` which runs synchronously in the
same thread context, so OTel ContextVar propagation works correctly.
"""
import os
from unittest.mock import patch

import pytest
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse
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

# Span name used by all framework child spans in these tests.
_FRAMEWORK_CHILD_SPAN = "framework_child_span"


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


def _make_tracing_app(**kwargs):
    """Create an InvocationAgentServerHost with tracing enabled (exporters mocked)."""
    with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=00000000-0000-0000-0000-000000000000"}):
        with patch("azure.ai.agentserver.core._tracing._setup_distro_export", create=True):
            return InvocationAgentServerHost(**kwargs)


def _find_parent_from_child(child_span, spans, expected_parent_operation: str):
    """Starting from the child span, use its parent span ID and trace ID to
    locate the parent in the exported spans and validate the relationship.

    This approach is parallel-safe: even if leaked spans from other tests
    exist in the exporter, we only look up the specific parent that the
    child references.

    :param child_span: The framework child span (captured directly in the test).
    :param spans: All exported spans.
    :param expected_parent_operation: Expected agentserver operation name in the parent span.
    """
    # Child must have a parent link
    assert child_span.parent is not None, (
        f"Child span '{child_span.name}' has no parent — it is a root span."
    )

    child_parent_span_id = child_span.parent.span_id
    child_trace_id = child_span.context.trace_id

    # Find the parent span by matching the span_id the child points to
    parent_matches = [
        s for s in spans
        if s.context.span_id == child_parent_span_id
    ]
    assert len(parent_matches) == 1, (
        f"Expected exactly 1 span with span_id={format(child_parent_span_id, '016x')}, "
        f"got {len(parent_matches)}: {[s.name for s in parent_matches]}"
    )
    parent = parent_matches[0]

    # Validate the parent is the expected agentserver operation
    assert expected_parent_operation in parent.name, (
        f"Child's parent span is '{parent.name}', expected it to contain '{expected_parent_operation}'."
    )

    # Validate both are in the same trace
    assert parent.context.trace_id == child_trace_id, (
        f"Parent trace ({format(parent.context.trace_id, '032x')}) "
        f"!= child trace ({format(child_trace_id, '032x')})."
    )


# ---------------------------------------------------------------------------
# Invoke: non-streaming
# ---------------------------------------------------------------------------


def test_framework_span_is_child_of_invoke_span():
    """A span created inside the handler should be a child of invoke_agent."""
    app = _make_tracing_app()
    child_tracer = trace.get_tracer("test.framework")
    captured_child = {}

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        with child_tracer.start_as_current_span(_FRAMEWORK_CHILD_SPAN) as span:
            captured_child["span"] = span
            return Response(content=b"ok")

    client = TestClient(app)
    resp = client.post("/invocations", content=b"test")
    assert resp.status_code == 200

    _find_parent_from_child(captured_child["span"], _get_spans(), "invoke_agent")


# ---------------------------------------------------------------------------
# Invoke: streaming — child span created before returning StreamingResponse
# ---------------------------------------------------------------------------


def test_framework_span_is_child_streaming_before_return():
    """Child span created in handler body (before StreamingResponse) is parented."""
    app = _make_tracing_app()
    child_tracer = trace.get_tracer("test.framework")
    captured_child = {}

    @app.invoke_handler
    async def handle(request: Request) -> StreamingResponse:
        with child_tracer.start_as_current_span(_FRAMEWORK_CHILD_SPAN) as span:
            captured_child["span"] = span
            async def generate():
                yield b"chunk\n"
            return StreamingResponse(generate(), media_type="text/plain")

    client = TestClient(app)
    resp = client.post("/invocations", content=b"test")
    assert resp.status_code == 200

    _find_parent_from_child(captured_child["span"], _get_spans(), "invoke_agent")


# ---------------------------------------------------------------------------
# Invoke: streaming — child span created DURING async iteration
# ---------------------------------------------------------------------------


def test_framework_span_is_child_streaming_during_iteration():
    """Child span created inside the async generator (while yielding chunks)
    is correctly parented via _wrap_streaming_response's context re-attachment."""
    app = _make_tracing_app()
    child_tracer = trace.get_tracer("test.framework")
    captured_child = {}

    @app.invoke_handler
    async def handle(request: Request) -> StreamingResponse:
        async def generate():
            # Child span created mid-stream — tests set_current_span / detach_context
            with child_tracer.start_as_current_span(_FRAMEWORK_CHILD_SPAN) as span:
                captured_child["span"] = span
                yield b"chunk1\n"
            yield b"chunk2\n"

        return StreamingResponse(generate(), media_type="text/plain")

    client = TestClient(app)
    resp = client.post("/invocations", content=b"test")
    assert resp.status_code == 200

    _find_parent_from_child(captured_child["span"], _get_spans(), "invoke_agent")


# ---------------------------------------------------------------------------
# Invoke: error path — child span is still parented when handler raises
# ---------------------------------------------------------------------------


def test_framework_span_is_child_when_handler_raises():
    """If the handler creates a child span then raises, the child is still
    correctly parented under invoke_agent."""
    app = _make_tracing_app()
    child_tracer = trace.get_tracer("test.framework")
    captured_child = {}

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        with child_tracer.start_as_current_span(_FRAMEWORK_CHILD_SPAN) as span:
            captured_child["span"] = span
            raise ValueError("boom")

    client = TestClient(app)
    resp = client.post("/invocations", content=b"test")
    assert resp.status_code == 500

    _find_parent_from_child(captured_child["span"], _get_spans(), "invoke_agent")


# ---------------------------------------------------------------------------
# GET invocation: child span parenting via _traced_invocation_endpoint
# ---------------------------------------------------------------------------


def test_framework_span_is_child_of_get_invocation_span():
    """Child span inside get_handler is parented under get_invocation span."""
    app = _make_tracing_app()
    child_tracer = trace.get_tracer("test.framework")
    captured_child = {}
    store: dict[str, bytes] = {}

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        store[request.state.invocation_id] = await request.body()
        return Response(content=b"ok")

    @app.get_invocation_handler
    async def get_handler(request: Request) -> Response:
        with child_tracer.start_as_current_span(_FRAMEWORK_CHILD_SPAN) as span:
            captured_child["span"] = span
            inv_id = request.path_params["invocation_id"]
            if inv_id in store:
                return Response(content=store[inv_id])
            return JSONResponse({"error": {"code": "not_found", "message": "Not found"}}, status_code=404)

    client = TestClient(app)
    resp = client.post("/invocations", content=b"data")
    inv_id = resp.headers["x-agent-invocation-id"]

    # Clear invoke spans so only get_invocation + child remain
    _EXPORTER.clear()
    client.get(f"/invocations/{inv_id}")

    _find_parent_from_child(captured_child["span"], _get_spans(), "get_invocation")
