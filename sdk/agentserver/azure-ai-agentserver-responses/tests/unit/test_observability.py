"""Unit tests for observability helpers."""

from __future__ import annotations

from azure.ai.agentserver.responses.hosting._observability import (
    InMemoryCreateSpanHook,
    build_create_span_tags,
    build_platform_server_header,
    start_create_span,
)


def test_observability__build_platform_server_header_includes_extra_identity() -> None:
    value = build_platform_server_header(
        sdk_name="azure-ai-agentserver-responses",
        version="0.1.0",
        runtime="python/3.11",
        extra="integration-suite",
    )

    assert value == "azure-ai-agentserver-responses/0.1.0 (python/3.11) integration-suite"


def test_observability__start_create_span_records_single_lifecycle_event() -> None:
    hook = InMemoryCreateSpanHook()
    span = start_create_span(
        "create_response",
        {"service.name": "svc", "gen_ai.operation.name": "create_response"},
        hook=hook,
    )

    span.set_tag("gen_ai.response.id", "resp_123")
    span.end()
    span.end()  # idempotent

    assert len(hook.spans) == 1
    assert hook.spans[0].name == "create_response"
    assert hook.spans[0].tags["gen_ai.response.id"] == "resp_123"
    assert hook.spans[0].ended_at is not None


def test_observability__build_create_span_tags_uses_agent_name_and_model() -> None:
    tags = build_create_span_tags(
        response_id="resp_abc",
        model="gpt-4o-mini",
        agent_reference={"name": "agent-one", "version": "v1"},
        service_name="azure-ai-agentserver-responses",
    )

    assert tags["service.name"] == "azure-ai-agentserver-responses"
    assert tags["gen_ai.operation.name"] == "create_response"
    assert tags["gen_ai.response.id"] == "resp_abc"
    assert tags["gen_ai.request.model"] == "gpt-4o-mini"
    assert tags["gen_ai.agent.name"] == "agent-one"
    assert tags["gen_ai.agent.id"] == "agent-one:v1"
