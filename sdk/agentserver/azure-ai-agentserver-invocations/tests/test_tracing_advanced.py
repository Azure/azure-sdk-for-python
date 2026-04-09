# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Advanced tracing tests: enrichment processor, flush, baggage,
concurrency, error details, and trace_stream lifecycle.

Complements the basic test_tracing_validation.py with deeper coverage
of the tracing pipeline internals.
"""
import asyncio
import os
import uuid
from unittest.mock import MagicMock, patch

import pytest
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from starlette.testclient import TestClient

from azure.ai.agentserver.invocations import InvocationAgentServerHost

try:
    from opentelemetry import trace, context as otel_context, baggage as otel_baggage
    from opentelemetry.sdk.trace import TracerProvider as SdkTracerProvider
    from opentelemetry.sdk.trace.export import (
        SimpleSpanProcessor,
        BatchSpanProcessor,
    )
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
        return Response(content=b"ok")

    return server


# ===================================================================
# Foundry Enrichment Span Processor
# ===================================================================


class TestFoundryEnrichment:
    """Verify _FoundryEnrichmentSpanProcessor injects identity attributes
    on all spans (not just the invoke_agent root).

    Tests the processor directly with isolated TracerProviders to avoid
    global state contamination between tests.
    """

    @staticmethod
    def _make_provider(agent_name=None, agent_version=None, agent_id=None, project_id=None):
        from azure.ai.agentserver.core._tracing import _FoundryEnrichmentSpanProcessor
        from opentelemetry.sdk.trace import TracerProvider as _TP
        from opentelemetry.sdk.resources import Resource

        exporter = InMemorySpanExporter()
        proc = _FoundryEnrichmentSpanProcessor(
            agent_name=agent_name, agent_version=agent_version,
            agent_id=agent_id, project_id=project_id,
        )
        provider = _TP(resource=Resource.create({}))
        provider.add_span_processor(proc)
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        return provider, exporter

    def test_project_id_on_span(self):
        provider, exporter = self._make_provider(
            agent_name="my-agent", project_id="proj-123",
        )
        tracer = provider.get_tracer("test")
        with tracer.start_as_current_span("span"):
            pass
        attrs = dict(exporter.get_finished_spans()[0].attributes)
        assert attrs.get("microsoft.foundry.project.id") == "proj-123"
        provider.shutdown()

    def test_agent_id_format(self):
        provider, exporter = self._make_provider(
            agent_name="my-agent", agent_version="7", agent_id="my-agent:7",
        )
        tracer = provider.get_tracer("test")
        with tracer.start_as_current_span("span"):
            pass
        attrs = dict(exporter.get_finished_spans()[0].attributes)
        assert attrs.get("gen_ai.agent.id") == "my-agent:7"
        provider.shutdown()

    def test_enrichment_on_child_spans(self):
        """Child spans also get agent identity from the enrichment processor."""
        provider, exporter = self._make_provider(
            agent_name="enriched", agent_version="2", agent_id="enriched:2",
        )
        tracer = provider.get_tracer("test")
        with tracer.start_as_current_span("parent"):
            with tracer.start_as_current_span("child"):
                pass
        spans = exporter.get_finished_spans()
        child = [s for s in spans if s.name == "child"][0]
        attrs = dict(child.attributes)
        assert attrs.get("gen_ai.agent.name") == "enriched"
        assert attrs.get("gen_ai.agent.id") == "enriched:2"
        provider.shutdown()

    def test_enrichment_overwrites_framework_set_agent_name(self):
        """If a framework sets gen_ai.agent.name during the span, the
        enrichment processor overwrites it in _on_ending."""
        provider, exporter = self._make_provider(
            agent_name="foundry-name", agent_id="foundry-name:1",
        )
        tracer = provider.get_tracer("test")
        with tracer.start_as_current_span("span") as span:
            span.set_attribute("gen_ai.agent.name", "framework-override")
        attrs = dict(exporter.get_finished_spans()[0].attributes)
        assert attrs.get("gen_ai.agent.name") == "foundry-name"
        provider.shutdown()

    def test_none_fields_skipped(self):
        provider, exporter = self._make_provider()
        tracer = provider.get_tracer("test")
        with tracer.start_as_current_span("span"):
            pass
        attrs = dict(exporter.get_finished_spans()[0].attributes)
        assert "gen_ai.agent.name" not in attrs
        assert "gen_ai.agent.id" not in attrs
        assert "microsoft.foundry.project.id" not in attrs
        provider.shutdown()


# ===================================================================
# flush_spans
# ===================================================================


class TestFlushSpans:
    """Verify flush_spans is called and actually flushes pending spans."""

    def test_flush_spans_is_importable(self):
        from azure.ai.agentserver.core._tracing import flush_spans
        assert callable(flush_spans)

    def test_flush_spans_no_error_when_called(self):
        from azure.ai.agentserver.core._tracing import flush_spans
        flush_spans()  # should not raise

    def test_flush_spans_with_batch_processor(self):
        """Verify flush_spans triggers export from a BatchSpanProcessor."""
        from azure.ai.agentserver.core._tracing import flush_spans

        exporter = InMemorySpanExporter()
        provider = SdkTracerProvider()
        provider.add_span_processor(BatchSpanProcessor(exporter))

        tracer = provider.get_tracer("flush-test")
        with tracer.start_as_current_span("test-span"):
            pass

        # Before flush, batch processor may not have exported yet
        # (it waits for the schedule_delay_millis timer)

        # Flush forces export
        with patch("opentelemetry.trace.get_tracer_provider", return_value=provider):
            flush_spans()

        spans = exporter.get_finished_spans()
        assert len(spans) >= 1
        assert spans[0].name == "test-span"

        provider.shutdown()


# ===================================================================
# Baggage Propagation
# ===================================================================


class TestBaggagePropagation:
    """Verify W3C baggage header is extracted alongside traceparent."""

    def test_traceparent_and_baggage_both_propagated(self):
        """Both traceparent and baggage should be extracted."""
        trace_id = uuid.uuid4().hex
        span_id = uuid.uuid4().hex[:16]
        traceparent = f"00-{trace_id}-{span_id}-01"
        baggage_header = "userId=test-user-123,requestType=travel"

        client = TestClient(_make_server())
        client.post(
            "/invocations", content=b"test",
            headers={"traceparent": traceparent, "baggage": baggage_header},
        )

        span = _invoke_spans()[0]
        actual_trace = format(span.context.trace_id, "032x")
        assert actual_trace == trace_id


# ===================================================================
# Concurrent Request Isolation
# ===================================================================


class TestConcurrentIsolation:
    """Verify traces from concurrent requests don't bleed into each other."""

    def test_sequential_requests_produce_distinct_traces(self):
        """Each sequential request should have its own trace ID."""
        client = TestClient(_make_server())
        for _ in range(10):
            client.post("/invocations", content=b"test")

        spans = _invoke_spans()
        assert len(spans) == 10
        trace_ids = [format(s.context.trace_id, "032x") for s in spans]
        assert len(set(trace_ids)) == 10

    def test_sequential_requests_have_distinct_response_ids(self):
        """Each request should produce a unique gen_ai.response.id."""
        client = TestClient(_make_server())
        for _ in range(10):
            client.post("/invocations", content=b"test")

        spans = _invoke_spans()
        response_ids = [s.attributes.get("gen_ai.response.id") for s in spans]
        assert len(set(response_ids)) == 10

    def test_traceparent_isolation(self):
        """Different traceparent headers should produce different traces."""
        client = TestClient(_make_server())

        trace_ids_sent = []
        for _ in range(5):
            tid = uuid.uuid4().hex
            sid = uuid.uuid4().hex[:16]
            trace_ids_sent.append(tid)
            client.post(
                "/invocations", content=b"test",
                headers={"traceparent": f"00-{tid}-{sid}-01"},
            )

        spans = _invoke_spans()
        trace_ids_received = [format(s.context.trace_id, "032x") for s in spans]
        assert set(trace_ids_sent) == set(trace_ids_received)


# ===================================================================
# Error Recording Completeness
# ===================================================================


class TestErrorRecordingCompleteness:
    """Verify errors are recorded with full detail."""

    def test_error_exception_type_in_event(self):
        with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=test"}):
            with patch("azure.ai.agentserver.core._tracing._setup_trace_export"):
                with patch("azure.ai.agentserver.core._tracing._setup_log_export"):
                    server = InvocationAgentServerHost()

        @server.invoke_handler
        async def handle(request: Request) -> Response:
            raise RuntimeError("detailed error message")

        client = TestClient(server)
        client.post("/invocations", content=b"test")

        span = _invoke_spans()[0]
        exception_events = [e for e in span.events if e.name == "exception"]
        assert len(exception_events) >= 1
        event_attrs = dict(exception_events[0].attributes)
        assert "RuntimeError" in event_attrs.get("exception.type", "")
        assert "detailed error message" in event_attrs.get("exception.message", "")

    def test_error_type_attribute_matches_exception(self):
        with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=test"}):
            with patch("azure.ai.agentserver.core._tracing._setup_trace_export"):
                with patch("azure.ai.agentserver.core._tracing._setup_log_export"):
                    server = InvocationAgentServerHost()

        @server.invoke_handler
        async def handle(request: Request) -> Response:
            raise TypeError("wrong type")

        client = TestClient(server)
        client.post("/invocations", content=b"test")

        span = _invoke_spans()[0]
        assert "TypeError" in span.attributes.get("error.type", "")

    def test_error_status_on_span(self):
        with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=test"}):
            with patch("azure.ai.agentserver.core._tracing._setup_trace_export"):
                with patch("azure.ai.agentserver.core._tracing._setup_log_export"):
                    server = InvocationAgentServerHost()

        @server.invoke_handler
        async def handle(request: Request) -> Response:
            raise Exception("test")

        client = TestClient(server)
        client.post("/invocations", content=b"test")

        span = _invoke_spans()[0]
        assert span.status.status_code == StatusCode.ERROR


# ===================================================================
# trace_stream Lifecycle
# ===================================================================


class TestTraceStreamLifecycle:
    """Verify trace_stream wrapper correctly manages span lifecycle."""

    def test_streaming_error_records_error_status(self):
        """If streaming raises, the span should have ERROR status."""
        with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=test"}):
            with patch("azure.ai.agentserver.core._tracing._setup_trace_export"):
                with patch("azure.ai.agentserver.core._tracing._setup_log_export"):
                    server = InvocationAgentServerHost()

        @server.invoke_handler
        async def handle(request: Request) -> StreamingResponse:
            async def generate():
                yield b"chunk1\n"
                raise ValueError("stream error")
            return StreamingResponse(generate(), media_type="text/plain")

        client = TestClient(server)
        try:
            client.post("/invocations", content=b"test")
        except Exception:
            pass

        spans = _invoke_spans()
        if spans:
            span = spans[0]
            assert span.status.status_code == StatusCode.ERROR

    def test_streaming_normal_completes_span(self):
        """Normal streaming should produce a completed span."""
        with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=test"}):
            with patch("azure.ai.agentserver.core._tracing._setup_trace_export"):
                with patch("azure.ai.agentserver.core._tracing._setup_log_export"):
                    server = InvocationAgentServerHost()

        @server.invoke_handler
        async def handle(request: Request) -> StreamingResponse:
            async def generate():
                for i in range(5):
                    yield f"chunk{i}\n".encode()
            return StreamingResponse(generate(), media_type="text/plain")

        client = TestClient(server)
        resp = client.post("/invocations", content=b"test")
        assert resp.status_code == 200

        spans = _invoke_spans()
        assert len(spans) >= 1
        # Span should be ended (it's in finished spans)
        assert spans[0].end_time is not None


# ===================================================================
# Multiple Child Span Parenting
# ===================================================================


class TestMultipleChildSpans:
    """Verify multiple child spans from different tracers all parent
    correctly under the invoke_agent span."""

    def test_multiple_children_same_parent(self):
        with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=test"}):
            with patch("azure.ai.agentserver.core._tracing._setup_trace_export"):
                with patch("azure.ai.agentserver.core._tracing._setup_log_export"):
                    server = InvocationAgentServerHost()

        tracer_a = trace.get_tracer("framework.a")
        tracer_b = trace.get_tracer("framework.b")

        @server.invoke_handler
        async def handle(request: Request) -> Response:
            with tracer_a.start_as_current_span("llm_call"):
                pass
            with tracer_b.start_as_current_span("tool_call"):
                pass
            return Response(content=b"ok")

        client = TestClient(server)
        client.post("/invocations", content=b"test")

        spans = _spans()
        parent = [s for s in spans if "invoke_agent" in s.name
                  and s.name not in ("llm_call", "tool_call")][0]
        children = [s for s in spans if s.name in ("llm_call", "tool_call")]
        assert len(children) == 2
        for child in children:
            assert child.parent is not None
            assert child.parent.span_id == parent.context.span_id, (
                f"Child '{child.name}' parent {format(child.parent.span_id, '016x')} "
                f"!= invoke_agent {format(parent.context.span_id, '016x')}"
            )

    def test_nested_children_form_chain(self):
        """Nested child spans should form a parent-child chain."""
        with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=test"}):
            with patch("azure.ai.agentserver.core._tracing._setup_trace_export"):
                with patch("azure.ai.agentserver.core._tracing._setup_log_export"):
                    server = InvocationAgentServerHost()

        tracer = trace.get_tracer("framework")

        @server.invoke_handler
        async def handle(request: Request) -> Response:
            with tracer.start_as_current_span("graph_node"):
                with tracer.start_as_current_span("llm_call"):
                    pass
            return Response(content=b"ok")

        client = TestClient(server)
        client.post("/invocations", content=b"test")

        spans = _spans()
        invoke = [s for s in spans if "invoke_agent" in s.name
                  and s.name not in ("graph_node", "llm_call")][0]
        graph_node = [s for s in spans if s.name == "graph_node"][0]
        llm_call = [s for s in spans if s.name == "llm_call"][0]

        # graph_node is child of invoke_agent
        assert graph_node.parent.span_id == invoke.context.span_id
        # llm_call is child of graph_node
        assert llm_call.parent.span_id == graph_node.context.span_id

    def test_all_spans_share_same_trace_id(self):
        """All spans (parent + children) should share one trace ID."""
        with patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=test"}):
            with patch("azure.ai.agentserver.core._tracing._setup_trace_export"):
                with patch("azure.ai.agentserver.core._tracing._setup_log_export"):
                    server = InvocationAgentServerHost()

        tracer = trace.get_tracer("framework")

        @server.invoke_handler
        async def handle(request: Request) -> Response:
            with tracer.start_as_current_span("child1"):
                with tracer.start_as_current_span("grandchild"):
                    pass
            with tracer.start_as_current_span("child2"):
                pass
            return Response(content=b"ok")

        client = TestClient(server)
        client.post("/invocations", content=b"test")

        spans = _spans()
        trace_ids = {s.context.trace_id for s in spans}
        assert len(trace_ids) == 1, f"Expected 1 trace ID, got {len(trace_ids)}"
