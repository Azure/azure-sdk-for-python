# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Comprehensive tracing validation tests for the invocations protocol.

Validates that traces emitted by the agentserver SDK are consistent with
the GenAI semantic conventions and produce the expected span structure
for downstream consumers (App Insights, Foundry portal).
"""
import os
import uuid
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
    from opentelemetry.trace import StatusCode

    _HAS_OTEL = True
except ImportError:
    _HAS_OTEL = False

if _HAS_OTEL:
    _existing = trace.get_tracer_provider()
    if hasattr(_existing, "add_span_processor"):
        _PROVIDER = _existing
    else:
        _PROVIDER = SdkTracerProvider()
        trace.set_tracer_provider(_PROVIDER)
    _EXPORTER = InMemorySpanExporter()
    _PROVIDER.add_span_processor(SimpleSpanProcessor(_EXPORTER))
else:
    _EXPORTER = None

pytestmark = pytest.mark.skipif(not _HAS_OTEL, reason="opentelemetry not installed")


@pytest.fixture(autouse=True)
def _clear():
    if _EXPORTER:
        _EXPORTER.clear()


def _spans():
    return list(_EXPORTER.get_finished_spans()) if _EXPORTER else []


def _invoke_spans():
    return [s for s in _spans() if "invoke_agent" in s.name]


def _make_server(**env_overrides):
    env = {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=test"}
    env.update(env_overrides)
    with patch.dict(os.environ, env):
        with patch("azure.ai.agentserver.core._tracing._setup_trace_export"):
            with patch("azure.ai.agentserver.core._tracing._setup_log_export"):
                server = InvocationAgentServerHost()

    @server.invoke_handler
    async def handle(request: Request) -> Response:
        return JSONResponse({"response": "ok"})

    return server


def _make_error_server():
    with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=test"}):
        with patch("azure.ai.agentserver.core._tracing._setup_trace_export"):
            with patch("azure.ai.agentserver.core._tracing._setup_log_export"):
                server = InvocationAgentServerHost()

    @server.invoke_handler
    async def handle(request: Request) -> Response:
        raise ValueError("test error for tracing")

    return server


def _make_streaming_server():
    with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=test"}):
        with patch("azure.ai.agentserver.core._tracing._setup_trace_export"):
            with patch("azure.ai.agentserver.core._tracing._setup_log_export"):
                server = InvocationAgentServerHost()

    @server.invoke_handler
    async def handle(request: Request) -> StreamingResponse:
        async def generate():
            yield b"chunk1\n"
            yield b"chunk2\n"
        return StreamingResponse(generate(), media_type="text/plain")

    return server


# ===================================================================
# GenAI Semantic Convention Attributes
# ===================================================================


class TestGenAISemanticConventions:
    """Verify all required GenAI semantic convention attributes."""

    def test_system_attribute(self):
        client = TestClient(_make_server())
        client.post("/invocations", content=b"test")
        span = _invoke_spans()[0]
        assert span.attributes.get("gen_ai.system") == "azure.ai.agentserver"

    def test_provider_name_attribute(self):
        client = TestClient(_make_server())
        client.post("/invocations", content=b"test")
        span = _invoke_spans()[0]
        assert span.attributes.get("gen_ai.provider.name") == "AzureAI Hosted Agents"

    def test_service_name_attribute(self):
        client = TestClient(_make_server())
        client.post("/invocations", content=b"test")
        span = _invoke_spans()[0]
        assert span.attributes.get("service.name") == "azure.ai.agentserver"

    def test_operation_name_is_invoke_agent(self):
        client = TestClient(_make_server())
        client.post("/invocations", content=b"test")
        span = _invoke_spans()[0]
        assert span.attributes.get("gen_ai.operation.name") == "invoke_agent"

    def test_response_id_present(self):
        client = TestClient(_make_server())
        client.post("/invocations", content=b"test")
        span = _invoke_spans()[0]
        resp_id = span.attributes.get("gen_ai.response.id")
        assert resp_id is not None
        assert isinstance(resp_id, str)
        assert len(resp_id) > 0

    def test_agent_id_from_env(self):
        server = _make_server(
            FOUNDRY_AGENT_NAME="test-agent",
            FOUNDRY_AGENT_VERSION="3",
        )
        client = TestClient(server)
        client.post("/invocations", content=b"test")
        span = _invoke_spans()[0]
        assert span.attributes.get("gen_ai.agent.id") == "test-agent:3"

    def test_agent_name_from_env(self):
        server = _make_server(FOUNDRY_AGENT_NAME="test-agent")
        client = TestClient(server)
        client.post("/invocations", content=b"test")
        span = _invoke_spans()[0]
        assert span.attributes.get("gen_ai.agent.name") == "test-agent"

    def test_agent_version_from_env(self):
        server = _make_server(
            FOUNDRY_AGENT_NAME="test-agent",
            FOUNDRY_AGENT_VERSION="5",
        )
        client = TestClient(server)
        client.post("/invocations", content=b"test")
        span = _invoke_spans()[0]
        assert span.attributes.get("gen_ai.agent.version") == "5"

    def test_conversation_id_from_session(self):
        client = TestClient(_make_server())
        client.post("/invocations?agent_session_id=sess-123", content=b"test")
        span = _invoke_spans()[0]
        assert span.attributes.get("gen_ai.conversation.id") == "sess-123"


# ===================================================================
# Span Naming
# ===================================================================


class TestSpanNaming:
    """Verify span names follow conventions."""

    def test_default_span_name(self):
        client = TestClient(_make_server())
        client.post("/invocations", content=b"test")
        span = _invoke_spans()[0]
        assert span.name.startswith("invoke_agent")

    def test_span_name_includes_agent_name(self):
        server = _make_server(FOUNDRY_AGENT_NAME="my-agent")
        client = TestClient(server)
        client.post("/invocations", content=b"test")
        span = _invoke_spans()[0]
        assert "my-agent" in span.name

    def test_span_name_includes_agent_name_and_version(self):
        server = _make_server(
            FOUNDRY_AGENT_NAME="my-agent",
            FOUNDRY_AGENT_VERSION="2",
        )
        client = TestClient(server)
        client.post("/invocations", content=b"test")
        span = _invoke_spans()[0]
        assert "my-agent" in span.name
        assert "2" in span.name


# ===================================================================
# Span Status
# ===================================================================


class TestSpanStatus:
    """Verify span status is set correctly on success and failure."""

    def test_success_span_has_ok_or_unset_status(self):
        client = TestClient(_make_server())
        resp = client.post("/invocations", content=b"test")
        assert resp.status_code == 200
        span = _invoke_spans()[0]
        # UNSET or OK both indicate success in OTel
        assert span.status.status_code in (StatusCode.UNSET, StatusCode.OK)

    def test_error_span_has_error_status(self):
        client = TestClient(_make_error_server())
        resp = client.post("/invocations", content=b"test")
        assert resp.status_code == 500
        span = _invoke_spans()[0]
        assert span.status.status_code == StatusCode.ERROR

    def test_error_span_has_error_type(self):
        client = TestClient(_make_error_server())
        client.post("/invocations", content=b"test")
        span = _invoke_spans()[0]
        error_type = span.attributes.get("error.type")
        assert error_type is not None
        assert "ValueError" in error_type

    def test_error_span_records_exception_event(self):
        client = TestClient(_make_error_server())
        client.post("/invocations", content=b"test")
        span = _invoke_spans()[0]
        exception_events = [e for e in span.events if e.name == "exception"]
        assert len(exception_events) >= 1


# ===================================================================
# Context Propagation
# ===================================================================


class TestContextPropagation:
    """Verify W3C traceparent propagation and span parenting."""

    def test_traceparent_sets_trace_id(self):
        trace_id_hex = uuid.uuid4().hex
        span_id_hex = uuid.uuid4().hex[:16]
        traceparent = f"00-{trace_id_hex}-{span_id_hex}-01"

        client = TestClient(_make_server())
        client.post("/invocations", content=b"test", headers={"traceparent": traceparent})

        span = _invoke_spans()[0]
        actual = format(span.context.trace_id, "032x")
        assert actual == trace_id_hex

    def test_traceparent_sets_parent_span(self):
        trace_id_hex = uuid.uuid4().hex
        span_id_hex = uuid.uuid4().hex[:16]
        traceparent = f"00-{trace_id_hex}-{span_id_hex}-01"

        client = TestClient(_make_server())
        client.post("/invocations", content=b"test", headers={"traceparent": traceparent})

        span = _invoke_spans()[0]
        assert span.parent is not None
        parent_span_id = format(span.parent.span_id, "016x")
        assert parent_span_id == span_id_hex

    def test_child_spans_parented_correctly(self):
        """A span created inside the handler is a child of invoke_agent."""
        with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=test"}):
            with patch("azure.ai.agentserver.core._tracing._setup_trace_export"):
                with patch("azure.ai.agentserver.core._tracing._setup_log_export"):
                    server = InvocationAgentServerHost()

        child_tracer = trace.get_tracer("test.child")

        @server.invoke_handler
        async def handle(request: Request) -> Response:
            with child_tracer.start_as_current_span("child_operation"):
                return Response(content=b"ok")

        client = TestClient(server)
        client.post("/invocations", content=b"test")

        spans = _spans()
        parent = [s for s in spans if "invoke_agent" in s.name and s.name != "child_operation"][0]
        child = [s for s in spans if s.name == "child_operation"][0]
        assert child.parent is not None
        assert child.parent.span_id == parent.context.span_id


# ===================================================================
# Streaming
# ===================================================================


class TestStreaming:
    """Verify tracing works correctly for streaming responses."""

    def test_streaming_creates_span(self):
        client = TestClient(_make_streaming_server())
        resp = client.post("/invocations", content=b"test")
        assert resp.status_code == 200
        assert len(_invoke_spans()) >= 1

    def test_streaming_span_has_ok_or_unset_status(self):
        client = TestClient(_make_streaming_server())
        client.post("/invocations", content=b"test")
        span = _invoke_spans()[0]
        assert span.status.status_code in (StatusCode.UNSET, StatusCode.OK)

    def test_streaming_span_has_genai_attributes(self):
        client = TestClient(_make_streaming_server())
        client.post("/invocations", content=b"test")
        span = _invoke_spans()[0]
        assert span.attributes.get("gen_ai.operation.name") == "invoke_agent"
        assert span.attributes.get("gen_ai.system") == "azure.ai.agentserver"


# ===================================================================
# Span Consistency Across Requests
# ===================================================================


class TestSpanConsistency:
    """Verify spans are consistent across multiple requests."""

    def test_each_request_gets_unique_trace(self):
        client = TestClient(_make_server())
        client.post("/invocations", content=b"req1")
        client.post("/invocations", content=b"req2")
        client.post("/invocations", content=b"req3")

        spans = _invoke_spans()
        assert len(spans) >= 3
        trace_ids = {format(s.context.trace_id, "032x") for s in spans}
        assert len(trace_ids) == len(spans), "Each request should have a unique trace ID"

    def test_each_request_gets_unique_response_id(self):
        client = TestClient(_make_server())
        client.post("/invocations", content=b"req1")
        client.post("/invocations", content=b"req2")

        spans = _invoke_spans()
        resp_ids = {s.attributes.get("gen_ai.response.id") for s in spans}
        assert len(resp_ids) == len(spans), "Each request should have a unique response ID"

    def test_required_attributes_present_on_every_span(self):
        """Every invoke span must have the minimum required attributes."""
        client = TestClient(_make_server())
        for i in range(5):
            client.post("/invocations", content=f"req{i}".encode())

        required_attrs = [
            "gen_ai.system",
            "gen_ai.provider.name",
            "gen_ai.operation.name",
            "service.name",
        ]

        for span in _invoke_spans():
            for attr in required_attrs:
                assert attr in span.attributes, (
                    f"Span {span.name} missing required attribute: {attr}"
                )
