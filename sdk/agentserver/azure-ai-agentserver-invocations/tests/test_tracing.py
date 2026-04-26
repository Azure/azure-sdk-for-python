# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for OpenTelemetry tracing in the invocations protocol."""
import os
import uuid
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from azure.ai.agentserver.invocations import InvocationAgentServerHost


# ---------------------------------------------------------------------------
# Module-level OTel setup with in-memory exporter
# ---------------------------------------------------------------------------
# We use the real OTel SDK to capture spans in memory.

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider as SdkTracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory import InMemorySpanExporter

    _HAS_OTEL = True
except ImportError:
    _HAS_OTEL = False

# Module-level provider so all tests share the same exporter
if _HAS_OTEL:
    _MODULE_EXPORTER = InMemorySpanExporter()
    _MODULE_PROVIDER = SdkTracerProvider()
    _MODULE_PROVIDER.add_span_processor(SimpleSpanProcessor(_MODULE_EXPORTER))
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
    """Create an InvocationAgentServerHost with tracing enabled."""
    with patch("azure.ai.agentserver.core._tracing.TracingHelper._setup_azure_monitor"):
        server = InvocationAgentServerHost(**kwargs)

    @server.invoke_handler
    async def handle(request: Request) -> Response:
        body = await request.body()
        return Response(content=body, media_type="application/octet-stream")

    return server


def _make_tracing_server_with_get_cancel(**kwargs):
    """Create a tracing-enabled server with get/cancel handlers."""
    with patch("azure.ai.agentserver.core._tracing.TracingHelper._setup_azure_monitor"):
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

    @app.cancel_invocation_handler
    async def cancel_handler(request: Request) -> Response:
        inv_id = request.path_params["invocation_id"]
        if inv_id in store:
            del store[inv_id]
            return JSONResponse({"status": "cancelled"})
        return JSONResponse({"error": {"code": "not_found", "message": "Not found"}}, status_code=404)

    return app


def _make_failing_tracing_server(**kwargs):
    """Create a tracing-enabled server whose handler raises."""
    with patch("azure.ai.agentserver.core._tracing.TracingHelper._setup_azure_monitor"):
        server = InvocationAgentServerHost(**kwargs)

    @server.invoke_handler
    async def handle(request: Request) -> Response:
        raise ValueError("tracing error test")

    return server


def _make_streaming_tracing_server(**kwargs):
    """Create a tracing-enabled server with streaming response."""
    with patch("azure.ai.agentserver.core._tracing.TracingHelper._setup_azure_monitor"):
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

@pytest.mark.asyncio
async def test_tracing_disabled_by_default():
    """No spans are created when tracing is not enabled."""
    if _MODULE_EXPORTER:
        _MODULE_EXPORTER.clear()

    app = InvocationAgentServerHost()

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.post("/invocations", content=b"test")

    # No spans should be created (server has no tracing helper)
    # The module-level provider may capture unrelated spans,
    # but none should be from our server
    spans = _get_spans()
    invoke_spans = [s for s in spans if "invoke_agent" in s.name]
    assert len(invoke_spans) == 0


# ---------------------------------------------------------------------------
# Tracing enabled creates invoke span with correct name
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_tracing_enabled_creates_invoke_span():
    """Tracing enabled creates a span named 'invoke_agent'."""
    server = _make_tracing_server()
    transport = ASGITransport(app=server)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.post("/invocations", content=b"test")

    spans = _get_spans()
    invoke_spans = [s for s in spans if "invoke_agent" in s.name]
    assert len(invoke_spans) >= 1
    assert invoke_spans[0].name.startswith("invoke_agent")


# ---------------------------------------------------------------------------
# Invoke error records exception
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_invoke_error_records_exception():
    """When handler raises, the span records the exception."""
    server = _make_failing_tracing_server()
    transport = ASGITransport(app=server)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations", content=b"test")
    assert resp.status_code == 500

    spans = _get_spans()
    invoke_spans = [s for s in spans if "invoke_agent" in s.name]
    assert len(invoke_spans) >= 1
    span = invoke_spans[0]
    # Should have error status
    assert span.status.status_code.name == "ERROR"


# ---------------------------------------------------------------------------
# GET/cancel create spans
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_invocation_creates_span():
    """GET /invocations/{id} creates a span."""
    server = _make_tracing_server_with_get_cancel()
    transport = ASGITransport(app=server)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations", content=b"data")
        inv_id = resp.headers["x-agent-invocation-id"]
        await client.get(f"/invocations/{inv_id}")

    spans = _get_spans()
    get_spans = [s for s in spans if "get_invocation" in s.name]
    assert len(get_spans) >= 1


@pytest.mark.asyncio
async def test_cancel_invocation_creates_span():
    """POST /invocations/{id}/cancel creates a span."""
    server = _make_tracing_server_with_get_cancel()
    transport = ASGITransport(app=server)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations", content=b"data")
        inv_id = resp.headers["x-agent-invocation-id"]
        await client.post(f"/invocations/{inv_id}/cancel")

    spans = _get_spans()
    cancel_spans = [s for s in spans if "cancel_invocation" in s.name]
    assert len(cancel_spans) >= 1


# ---------------------------------------------------------------------------
# Tracing via env var
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_tracing_via_appinsights_env_var():
    """Tracing is enabled when APPLICATIONINSIGHTS_CONNECTION_STRING is set."""
    with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=test"}):
        with patch("azure.ai.agentserver.core._tracing.TracingHelper._setup_azure_monitor"):
            app = InvocationAgentServerHost()

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        return Response(content=b"ok")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.post("/invocations", content=b"test")

    spans = _get_spans()
    invoke_spans = [s for s in spans if "invoke_agent" in s.name]
    assert len(invoke_spans) >= 1


# ---------------------------------------------------------------------------
# No tracing when no endpoints configured
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_no_tracing_when_no_endpoints():
    """Tracing is disabled when no connection string or OTLP endpoint is set."""
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

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.post("/invocations", content=b"test")

    spans = _get_spans()
    invoke_spans = [s for s in spans if "invoke_agent" in s.name]
    assert len(invoke_spans) == 0


# ---------------------------------------------------------------------------
# Traceparent propagation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_traceparent_propagation():
    """Server propagates traceparent header into span context."""
    server = _make_tracing_server()
    transport = ASGITransport(app=server)

    # Create a traceparent
    trace_id_hex = uuid.uuid4().hex
    span_id_hex = uuid.uuid4().hex[:16]
    traceparent = f"00-{trace_id_hex}-{span_id_hex}-01"

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.post(
            "/invocations",
            content=b"test",
            headers={"traceparent": traceparent},
        )

    spans = _get_spans()
    invoke_spans = [s for s in spans if "invoke_agent" in s.name]
    assert len(invoke_spans) >= 1
    span = invoke_spans[0]
    # The span should have the same trace ID as the traceparent
    actual_trace_id = format(span.context.trace_id, "032x")
    assert actual_trace_id == trace_id_hex


# ---------------------------------------------------------------------------
# Streaming spans
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_streaming_creates_span():
    """Streaming response creates and completes a span."""
    server = _make_streaming_tracing_server()
    transport = ASGITransport(app=server)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations", content=b"test")
    assert resp.status_code == 200

    spans = _get_spans()
    invoke_spans = [s for s in spans if "invoke_agent" in s.name]
    assert len(invoke_spans) >= 1


# ---------------------------------------------------------------------------
# GenAI attributes on invoke span
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_genai_attributes_on_invoke_span():
    """Invoke span has GenAI semantic convention attributes."""
    server = _make_tracing_server()
    transport = ASGITransport(app=server)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.post("/invocations", content=b"test")

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

@pytest.mark.asyncio
async def test_session_id_in_conversation_id():
    """Session ID is set as gen_ai.conversation.id on invoke span."""
    server = _make_tracing_server()
    transport = ASGITransport(app=server)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.post(
            "/invocations?agent_session_id=test-session",
            content=b"test",
        )

    spans = _get_spans()
    invoke_spans = [s for s in spans if "invoke_agent" in s.name]
    assert len(invoke_spans) >= 1
    attrs = dict(invoke_spans[0].attributes)
    assert attrs.get("gen_ai.conversation.id") == "test-session"


# ---------------------------------------------------------------------------
# GenAI attributes on get_invocation span
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_genai_attributes_on_get_span():
    """GET invocation span has GenAI attributes."""
    server = _make_tracing_server_with_get_cancel()
    transport = ASGITransport(app=server)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations", content=b"data")
        inv_id = resp.headers["x-agent-invocation-id"]
        await client.get(f"/invocations/{inv_id}")

    spans = _get_spans()
    get_spans = [s for s in spans if "get_invocation" in s.name]
    assert len(get_spans) >= 1
    attrs = dict(get_spans[0].attributes)
    assert attrs.get("gen_ai.system") == "azure.ai.agentserver"
    assert attrs.get("gen_ai.provider.name") == "AzureAI Hosted Agents"


# ---------------------------------------------------------------------------
# Namespaced invocation_id attribute
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_namespaced_invocation_id_attribute():
    """Invoke span has azure.ai.agentserver.invocations.invocation_id."""
    server = _make_tracing_server()
    transport = ASGITransport(app=server)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations", content=b"test")
        inv_id = resp.headers["x-agent-invocation-id"]

    spans = _get_spans()
    invoke_spans = [s for s in spans if "invoke_agent" in s.name]
    assert len(invoke_spans) >= 1
    attrs = dict(invoke_spans[0].attributes)
    assert attrs.get("azure.ai.agentserver.invocations.invocation_id") == inv_id


# ---------------------------------------------------------------------------
# Baggage tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_baggage_leaf_customer_span_id():
    """Baggage leaf_customer_span_id overrides parent span ID."""
    server = _make_tracing_server()
    transport = ASGITransport(app=server)

    trace_id_hex = uuid.uuid4().hex
    original_span_id = uuid.uuid4().hex[:16]
    leaf_span_id = uuid.uuid4().hex[:16]
    traceparent = f"00-{trace_id_hex}-{original_span_id}-01"
    baggage = f"leaf_customer_span_id={leaf_span_id}"

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.post(
            "/invocations",
            content=b"test",
            headers={
                "traceparent": traceparent,
                "baggage": baggage,
            },
        )

    spans = _get_spans()
    invoke_spans = [s for s in spans if "invoke_agent" in s.name]
    assert len(invoke_spans) >= 1
    span = invoke_spans[0]
    # The parent span ID should be overridden to leaf_span_id
    if span.parent is not None:
        actual_parent_span_id = format(span.parent.span_id, "016x")
        assert actual_parent_span_id == leaf_span_id


# ---------------------------------------------------------------------------
# Agent name/version in span names
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_agent_name_in_span_name():
    """Agent name from env var appears in span name."""
    with patch.dict(os.environ, {
        "FOUNDRY_AGENT_NAME": "my-agent",
        "FOUNDRY_AGENT_VERSION": "2.0",
    }):
        server = _make_tracing_server()

    transport = ASGITransport(app=server)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.post("/invocations", content=b"test")

    spans = _get_spans()
    invoke_spans = [s for s in spans if "invoke_agent" in s.name]
    assert len(invoke_spans) >= 1
    assert "my-agent" in invoke_spans[0].name
    assert "2.0" in invoke_spans[0].name


@pytest.mark.asyncio
async def test_agent_name_only_in_span_name():
    """Agent name without version in span name."""
    env_override = {"FOUNDRY_AGENT_NAME": "solo-agent"}
    env_copy = os.environ.copy()
    env_copy.pop("FOUNDRY_AGENT_VERSION", None)
    env_copy.update(env_override)
    with patch.dict(os.environ, env_copy, clear=True):
        server = _make_tracing_server()

    transport = ASGITransport(app=server)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.post("/invocations", content=b"test")

    spans = _get_spans()
    invoke_spans = [s for s in spans if "invoke_agent" in s.name]
    assert len(invoke_spans) >= 1
    assert "solo-agent" in invoke_spans[0].name


# ---------------------------------------------------------------------------
# Project endpoint attribute
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_project_endpoint_env_var():
    """FOUNDRY_PROJECT_ENDPOINT constant matches the expected env var name."""
    from azure.ai.agentserver.core import Constants
    assert Constants.FOUNDRY_PROJECT_ENDPOINT == "FOUNDRY_PROJECT_ENDPOINT"
