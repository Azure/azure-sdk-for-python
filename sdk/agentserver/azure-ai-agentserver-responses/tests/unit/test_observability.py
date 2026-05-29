# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for observability helpers."""

from __future__ import annotations

from types import SimpleNamespace

from azure.ai.agentserver.responses.hosting._observability import (
    InMemoryCreateSpanHook,
    build_create_otel_attrs,
    build_create_span_tags,
    build_platform_server_header,
    extract_request_id,
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
    ctx = SimpleNamespace(
        response_id="resp_abc",
        model="gpt-4o-mini",
        agent_reference={"name": "agent-one", "version": "v1"},
        conversation_id=None,
        stream=False,
    )
    tags = build_create_span_tags(ctx)

    assert tags["service.name"] == "azure.ai.agentserver"
    assert tags["gen_ai.operation.name"] == "invoke_agent"
    assert tags["gen_ai.provider.name"] == "AzureAI Hosted Agents"
    assert tags["gen_ai.response.id"] == "resp_abc"
    assert tags["gen_ai.request.model"] == "gpt-4o-mini"
    assert tags["gen_ai.agent.name"] == "agent-one"
    assert tags["gen_ai.agent.id"] == "agent-one:v1"
    assert tags["gen_ai.agent.version"] == "v1"


def test_observability__build_create_span_tags_includes_conversation_id() -> None:
    ctx = SimpleNamespace(
        response_id="resp_xyz",
        model="gpt-4o",
        agent_reference=None,
        conversation_id="conv_123",
        stream=False,
    )
    tags = build_create_span_tags(ctx)

    assert tags["gen_ai.conversation.id"] == "conv_123"
    assert "gen_ai.agent.version" not in tags


def test_observability__build_create_span_tags_omits_conversation_id_when_absent() -> None:
    ctx = SimpleNamespace(
        response_id="resp_xyz",
        model="gpt-4o",
        agent_reference=None,
        conversation_id=None,
        stream=False,
    )
    tags = build_create_span_tags(ctx)

    assert "gen_ai.conversation.id" not in tags


def test_observability__build_create_span_tags_omits_agent_version_when_absent() -> None:
    ctx = SimpleNamespace(
        response_id="resp_xyz",
        model="gpt-4o",
        agent_reference={"name": "my-agent"},
        conversation_id=None,
        stream=False,
    )
    tags = build_create_span_tags(ctx)

    assert tags["gen_ai.agent.name"] == "my-agent"
    assert tags["gen_ai.agent.id"] == ""
    assert "gen_ai.agent.version" not in tags


def test_observability__build_create_span_tags_includes_request_id() -> None:
    ctx = SimpleNamespace(
        response_id="resp_r",
        model="gpt-4o",
        agent_reference=None,
        conversation_id=None,
        stream=False,
    )
    tags = build_create_span_tags(ctx, request_id="req-1")

    assert tags["request.id"] == "req-1"


def test_observability__build_create_span_tags_omits_request_id_when_absent() -> None:
    ctx = SimpleNamespace(
        response_id="resp_r",
        model="gpt-4o",
        agent_reference=None,
        conversation_id=None,
        stream=False,
    )
    tags = build_create_span_tags(ctx)

    assert "request.id" not in tags


# ---------------------------------------------------------------------------
# extract_request_id
# ---------------------------------------------------------------------------


def test_observability__extract_request_id_returns_value_from_header() -> None:
    assert extract_request_id({"x-request-id": "req-abc"}) == "req-abc"


def test_observability__extract_request_id_truncates_to_256_chars() -> None:
    long_id = "z" * 300
    result = extract_request_id({"x-request-id": long_id})
    assert result == "z" * 256


def test_observability__extract_request_id_returns_none_when_absent() -> None:
    assert extract_request_id({}) is None


# ---------------------------------------------------------------------------
# build_create_otel_attrs
# ---------------------------------------------------------------------------


def test_observability__build_create_otel_attrs_includes_all_fields() -> None:
    ctx = SimpleNamespace(
        response_id="resp_1",
        model="gpt-4o",
        agent_reference={"name": "bot", "version": "2.0"},
        conversation_id="conv_x",
        stream=False,
    )
    attrs = build_create_otel_attrs(ctx, request_id="req-1")

    assert attrs["gen_ai.response.id"] == "resp_1"
    assert attrs["service.name"] == "azure.ai.agentserver"
    assert attrs["gen_ai.provider.name"] == "AzureAI Hosted Agents"
    assert attrs["gen_ai.operation.name"] == "invoke_agent"
    assert attrs["gen_ai.request.model"] == "gpt-4o"
    assert attrs["gen_ai.conversation.id"] == "conv_x"
    assert attrs["gen_ai.agent.name"] == "bot"
    assert attrs["gen_ai.agent.id"] == "bot:2.0"
    assert attrs["gen_ai.agent.version"] == "2.0"
    assert attrs["request.id"] == "req-1"


def test_observability__build_create_otel_attrs_omits_optional_fields_when_absent() -> None:
    ctx = SimpleNamespace(
        response_id="resp_2",
        model=None,
        agent_reference=None,
        conversation_id=None,
        stream=False,
    )
    attrs = build_create_otel_attrs(ctx, request_id=None)

    assert "gen_ai.conversation.id" not in attrs
    assert "gen_ai.agent.name" not in attrs
    assert attrs["gen_ai.agent.id"] == ""
    assert "gen_ai.agent.version" not in attrs
    assert "request.id" not in attrs
    assert attrs["gen_ai.request.model"] == ""
