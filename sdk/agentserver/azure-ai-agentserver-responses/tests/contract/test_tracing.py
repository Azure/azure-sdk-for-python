# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests for distributed tracing on POST /responses.

These tests verify the span display name, GenAI parity tags, additional OTEL
tags, request ID propagation, and baggage items emitted by ``handle_create``.
"""

from __future__ import annotations

from typing import Any

import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost, ResponsesServerOptions
from azure.ai.agentserver.responses.hosting._observability import InMemoryCreateSpanHook


def _noop_handler(request: Any, context: Any, cancellation_signal: Any):
    async def _events():
        if False:  # pragma: no cover
            yield None

    return _events()


def _build_client(hook: InMemoryCreateSpanHook | None = None) -> TestClient:
    options = ResponsesServerOptions(create_span_hook=hook)
    app = ResponsesAgentServerHost(options=options)
    app.response_handler(_noop_handler)
    return TestClient(app)


# ---------------------------------------------------------------------------
# Span display name
# ---------------------------------------------------------------------------


def test_tracing__span_name_includes_model() -> None:
    hook = InMemoryCreateSpanHook()
    client = _build_client(hook)

    client.post(
        "/responses",
        json={"model": "gpt-4o-mini", "input": "hi", "stream": False},
    )

    assert len(hook.spans) == 1
    assert hook.spans[0].name == "create_response"


def test_tracing__span_name_without_model_falls_back_to_create_response() -> None:
    """When model is absent the span name should still be emitted."""
    hook = InMemoryCreateSpanHook()
    client = _build_client(hook)

    client.post(
        "/responses",
        json={"input": "hi", "stream": False},
    )

    # Span must be recorded regardless.
    assert len(hook.spans) == 1
    assert hook.spans[0].name == "create_response"


# ---------------------------------------------------------------------------
# GenAI parity tags
# ---------------------------------------------------------------------------


def test_tracing__span_tags_include_genai_parity_fields() -> None:
    hook = InMemoryCreateSpanHook()
    client = _build_client(hook)

    client.post(
        "/responses",
        json={
            "model": "gpt-4o",
            "input": "hello",
            "stream": False,
            "agent_reference": {"type": "agent_reference", "name": "my-agent", "version": "v2"},
        },
    )

    assert len(hook.spans) == 1
    tags = hook.spans[0].tags

    assert isinstance(tags.get("gen_ai.response.id"), str)
    assert tags["gen_ai.response.id"].startswith("caresp_") or tags["gen_ai.response.id"].startswith("resp_")
    assert tags["gen_ai.agent.name"] == "my-agent"
    assert tags["gen_ai.agent.id"] == "my-agent:v2"
    assert tags["gen_ai.provider.name"] == "AzureAI Hosted Agents"
    assert tags["service.name"] == "azure.ai.agentserver"


# ---------------------------------------------------------------------------
# Additional OTEL tags
# ---------------------------------------------------------------------------


def test_tracing__span_tags_include_operation_name_invoke_agent() -> None:
    hook = InMemoryCreateSpanHook()
    client = _build_client(hook)

    client.post(
        "/responses",
        json={"model": "gpt-4o-mini", "input": "hi", "stream": False},
    )

    assert hook.spans[0].tags["gen_ai.operation.name"] == "invoke_agent"


def test_tracing__span_tags_include_model() -> None:
    hook = InMemoryCreateSpanHook()
    client = _build_client(hook)

    client.post(
        "/responses",
        json={"model": "gpt-4o-mini", "input": "hi", "stream": False},
    )

    assert hook.spans[0].tags["gen_ai.request.model"] == "gpt-4o-mini"


def test_tracing__span_tags_include_conversation_id_when_present() -> None:
    hook = InMemoryCreateSpanHook()
    client = _build_client(hook)

    client.post(
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hi",
            "stream": False,
            "conversation": "conv_abc123",
        },
    )

    assert hook.spans[0].tags.get("gen_ai.conversation.id") == "conv_abc123"


def test_tracing__span_tags_omit_conversation_id_when_absent() -> None:
    hook = InMemoryCreateSpanHook()
    client = _build_client(hook)

    client.post(
        "/responses",
        json={"model": "gpt-4o-mini", "input": "hi", "stream": False},
    )

    assert "gen_ai.conversation.id" not in hook.spans[0].tags


def test_tracing__span_tags_include_agent_version() -> None:
    hook = InMemoryCreateSpanHook()
    client = _build_client(hook)

    client.post(
        "/responses",
        json={
            "model": "gpt-4o-mini",
            "input": "hi",
            "stream": False,
            "agent_reference": {"type": "agent_reference", "name": "bot", "version": "1.0"},
        },
    )

    assert hook.spans[0].tags.get("gen_ai.agent.version") == "1.0"


# ---------------------------------------------------------------------------
# Request ID propagation
# ---------------------------------------------------------------------------


def test_tracing__span_tags_include_request_id_from_header() -> None:
    hook = InMemoryCreateSpanHook()
    client = _build_client(hook)

    client.post(
        "/responses",
        json={"model": "gpt-4o-mini", "input": "hi", "stream": False},
        headers={"X-Request-Id": "req-abc-123"},
    )

    assert hook.spans[0].tags.get("request.id") == "req-abc-123"


def test_tracing__request_id_truncated_to_256_characters() -> None:
    hook = InMemoryCreateSpanHook()
    client = _build_client(hook)

    long_id = "x" * 300

    client.post(
        "/responses",
        json={"model": "gpt-4o-mini", "input": "hi", "stream": False},
        headers={"X-Request-Id": long_id},
    )

    value = hook.spans[0].tags.get("request.id")
    assert value is not None
    assert len(value) == 256
    assert value == "x" * 256


def test_tracing__span_tags_omit_request_id_when_header_absent() -> None:
    hook = InMemoryCreateSpanHook()
    client = _build_client(hook)

    client.post(
        "/responses",
        json={"model": "gpt-4o-mini", "input": "hi", "stream": False},
    )

    assert "request.id" not in hook.spans[0].tags


# ---------------------------------------------------------------------------
# Incoming W3C baggage propagation
# ---------------------------------------------------------------------------


def test_tracing__incoming_baggage_merged_into_context() -> None:
    """Incoming W3C baggage header entries are merged into OTel context."""
    try:
        from opentelemetry import baggage as _otel_baggage
    except ImportError:
        pytest.skip("opentelemetry SDK not installed")

    captured_baggage: dict = {}

    def _baggage_capture_handler(request, context, cancellation_signal):
        captured_baggage.update(_otel_baggage.get_all())

        async def _events():
            if False:  # pragma: no cover
                yield None

        return _events()

    options = ResponsesServerOptions()
    app = ResponsesAgentServerHost(options=options)
    app.response_handler(_baggage_capture_handler)
    client = TestClient(app)

    client.post(
        "/responses",
        json={"model": "gpt-4o-mini", "input": "hi", "stream": False},
        headers={"baggage": "user.id=test-user-789,custom.key=custom-value"},
    )

    # Incoming baggage entries should be present
    assert captured_baggage.get("user.id") == "test-user-789"
    assert captured_baggage.get("custom.key") == "custom-value"


def test_tracing__framework_span_parented_under_incoming_traceparent() -> None:
    """A span created inside the handler is parented directly under the
    incoming traceparent — no intermediate invoke_agent span."""
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider as SdkTracerProvider
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor
        from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    except ImportError:
        pytest.skip("opentelemetry SDK not installed")

    import uuid

    exporter = InMemorySpanExporter()
    existing = trace.get_tracer_provider()
    if hasattr(existing, "add_span_processor"):
        existing.add_span_processor(SimpleSpanProcessor(exporter))
    else:
        provider = SdkTracerProvider()
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        trace.set_tracer_provider(provider)

    trace_id_hex = uuid.uuid4().hex
    span_id_hex = uuid.uuid4().hex[:16]
    traceparent = f"00-{trace_id_hex}-{span_id_hex}-01"

    captured_trace_id = None
    captured_parent_id = None

    def _span_handler(request, context, cancellation_signal):
        nonlocal captured_trace_id, captured_parent_id
        tracer = trace.get_tracer("test.framework")
        with tracer.start_as_current_span("framework_create_response") as span:
            captured_trace_id = format(span.context.trace_id, "032x")
            captured_parent_id = format(span.parent.span_id, "016x") if span.parent else None

        async def _events():
            if False:  # pragma: no cover
                yield None

        return _events()

    options = ResponsesServerOptions()
    app = ResponsesAgentServerHost(options=options)
    app.response_handler(_span_handler)
    client = TestClient(app)

    resp = client.post(
        "/responses",
        json={"model": "gpt-4o-mini", "input": "hi", "stream": False},
        headers={
            "traceparent": traceparent,
            "baggage": "user.id=test-user-parenting",
        },
    )
    assert resp.status_code == 200

    # Framework span should share the same trace ID as the incoming traceparent
    assert captured_trace_id == trace_id_hex
    # Framework span should be parented directly under the incoming span
    assert captured_parent_id == span_id_hex

    # Verify via exporter as well
    spans = exporter.get_finished_spans()
    fw_spans = [s for s in spans if s.name == "framework_create_response"]
    assert len(fw_spans) == 1
    fw = fw_spans[0]
    assert format(fw.context.trace_id, "032x") == trace_id_hex
    assert fw.parent is not None
    assert format(fw.parent.span_id, "016x") == span_id_hex


def test_tracing__incoming_baggage_empty_header_no_error() -> None:
    """Empty baggage header does not cause errors."""
    client = _build_client()
    resp = client.post(
        "/responses",
        json={"model": "gpt-4o-mini", "input": "hi", "stream": False},
        headers={"baggage": ""},
    )
    assert resp.status_code == 200
