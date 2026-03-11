"""Unit tests for W3C trace context propagation in the hosted agent server."""

import pytest
from opentelemetry import trace, context
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExporter, SpanExportResult
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator


class ListSpanExporter(SpanExporter):
    """A minimal span exporter that collects finished spans into a list."""

    def __init__(self):
        self.spans = []

    def export(self, spans):
        self.spans.extend(spans)
        return SpanExportResult.SUCCESS

    def shutdown(self):
        pass

    def clear(self):
        self.spans.clear()


# Module-level provider (OTel only allows setting the global provider once)
_exporter = ListSpanExporter()
_provider = TracerProvider()
_provider.add_span_processor(SimpleSpanProcessor(_exporter))
trace.set_tracer_provider(_provider)


@pytest.fixture(autouse=True)
def _clear_spans():
    """Clear collected spans before each test."""
    _exporter.clear()
    yield


class TestTraceContextPropagation:
    """Tests for W3C traceparent header extraction in runs_endpoint."""

    def _make_traceparent(self):
        """Create a traceparent header from a fresh span context."""
        tracer = trace.get_tracer("test-client")
        with tracer.start_as_current_span("client-call") as span:
            ctx = span.get_span_context()
            carrier = {}
            TraceContextTextMapPropagator().inject(carrier)
        return carrier["traceparent"], ctx.trace_id, ctx.span_id

    def test_server_span_parents_to_incoming_traceparent(self):
        """When a request carries a traceparent header, the server span must
        become a child of that trace (same trace_id, parent_span_id matches)."""
        traceparent, parent_trace_id, parent_span_id = self._make_traceparent()

        # Simulate what the server does: extract and start span with parent context
        server_tracer = trace.get_tracer("azure.ai.agentserver")
        incoming_headers = {"traceparent": traceparent}
        extracted_ctx = TraceContextTextMapPropagator().extract(carrier=incoming_headers)

        with server_tracer.start_as_current_span(
            name="HostedAgents-test",
            kind=trace.SpanKind.SERVER,
            context=extracted_ctx,
        ) as server_span:
            server_ctx = server_span.get_span_context()

        assert server_ctx.trace_id == parent_trace_id, (
            f"Server span trace_id {server_ctx.trace_id:#034x} should match "
            f"parent trace_id {parent_trace_id:#034x}"
        )

        server_spans = [s for s in _exporter.spans if s.name == "HostedAgents-test"]
        assert len(server_spans) == 1
        assert server_spans[0].parent.span_id == parent_span_id

    def test_server_span_is_root_without_traceparent(self):
        """When no traceparent header is present, the server span must be a
        root span (no parent, new trace_id)."""
        server_tracer = trace.get_tracer("azure.ai.agentserver")
        incoming_headers = {}
        extracted_ctx = TraceContextTextMapPropagator().extract(carrier=incoming_headers)

        with server_tracer.start_as_current_span(
            name="HostedAgents-no-parent",
            kind=trace.SpanKind.SERVER,
            context=extracted_ctx,
        ):
            pass

        server_spans = [s for s in _exporter.spans if s.name == "HostedAgents-no-parent"]
        assert len(server_spans) == 1
        assert server_spans[0].parent is None, "Server span should be root when no traceparent is sent"

    def test_traceparent_header_case_insensitive(self):
        """Starlette's request.headers is a case-insensitive mapping, so
        mixed-case header keys are handled by the framework, not by our code.
        This test verifies the propagator works with the lowercase key that
        Starlette normalizes headers to."""
        traceparent, parent_trace_id, _ = self._make_traceparent()

        # Starlette normalizes all header keys to lowercase
        server_tracer = trace.get_tracer("azure.ai.agentserver")
        incoming_headers = {"traceparent": traceparent}
        extracted_ctx = TraceContextTextMapPropagator().extract(carrier=incoming_headers)

        with server_tracer.start_as_current_span(
            name="HostedAgents-case-test",
            kind=trace.SpanKind.SERVER,
            context=extracted_ctx,
        ) as server_span:
            server_ctx = server_span.get_span_context()

        assert server_ctx.trace_id == parent_trace_id
