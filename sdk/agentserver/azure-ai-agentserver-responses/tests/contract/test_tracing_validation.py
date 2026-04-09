# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Comprehensive tracing validation tests for the responses protocol.

Validates that the responses protocol emits spans with correct GenAI
semantic convention attributes, names, and structure.
"""
from __future__ import annotations

from typing import Any

import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost, ResponsesServerOptions
from azure.ai.agentserver.responses.hosting._observability import InMemoryCreateSpanHook


# ===================================================================
# Helpers
# ===================================================================


def _noop_handler(request: Any, context: Any, cancellation_signal: Any):
    async def _events():
        if False:
            yield None
    return _events()


def _build(hook: InMemoryCreateSpanHook | None = None) -> TestClient:
    options = ResponsesServerOptions(create_span_hook=hook)
    app = ResponsesAgentServerHost(options=options)
    app.create_handler(_noop_handler)
    return TestClient(app)


def _post(client: TestClient, **json_overrides) -> None:
    body: dict[str, Any] = {"input": "hi", "stream": False}
    body.update(json_overrides)
    client.post("/responses", json=body)


# ===================================================================
# GenAI Semantic Convention Attributes
# ===================================================================


class TestGenAIAttributes:
    """Verify all required GenAI attributes on create_response spans."""

    def test_operation_name_is_invoke_agent(self):
        hook = InMemoryCreateSpanHook()
        client = _build(hook)
        _post(client)
        assert hook.spans[0].tags["gen_ai.operation.name"] == "invoke_agent"

    def test_provider_name(self):
        hook = InMemoryCreateSpanHook()
        client = _build(hook)
        _post(client)
        assert hook.spans[0].tags["gen_ai.provider.name"] == "AzureAI Hosted Agents"

    def test_service_name(self):
        hook = InMemoryCreateSpanHook()
        client = _build(hook)
        _post(client)
        assert hook.spans[0].tags["service.name"] == "azure.ai.agentserver"

    def test_response_id_present(self):
        hook = InMemoryCreateSpanHook()
        client = _build(hook)
        _post(client)
        resp_id = hook.spans[0].tags.get("gen_ai.response.id")
        assert resp_id is not None
        assert isinstance(resp_id, str)
        assert len(resp_id) > 0

    def test_response_id_has_valid_prefix(self):
        hook = InMemoryCreateSpanHook()
        client = _build(hook)
        _post(client)
        resp_id = hook.spans[0].tags["gen_ai.response.id"]
        assert resp_id.startswith("caresp_") or resp_id.startswith("resp_")

    def test_model_attribute(self):
        hook = InMemoryCreateSpanHook()
        client = _build(hook)
        _post(client, model="gpt-4.1")
        assert hook.spans[0].tags.get("gen_ai.request.model") == "gpt-4.1"


# ===================================================================
# Agent Identity Attributes
# ===================================================================


class TestAgentIdentity:
    """Verify agent_reference is correctly mapped to span attributes."""

    def test_agent_name_from_reference(self):
        hook = InMemoryCreateSpanHook()
        client = _build(hook)
        _post(client, agent_reference={"type": "agent_reference", "name": "travel-bot"})
        assert hook.spans[0].tags.get("gen_ai.agent.name") == "travel-bot"

    def test_agent_id_includes_version(self):
        hook = InMemoryCreateSpanHook()
        client = _build(hook)
        _post(client, agent_reference={
            "type": "agent_reference", "name": "travel-bot", "version": "3",
        })
        assert hook.spans[0].tags.get("gen_ai.agent.id") == "travel-bot:3"

    def test_agent_version_attribute(self):
        hook = InMemoryCreateSpanHook()
        client = _build(hook)
        _post(client, agent_reference={
            "type": "agent_reference", "name": "travel-bot", "version": "7",
        })
        assert hook.spans[0].tags.get("gen_ai.agent.version") == "7"

    def test_no_agent_reference_omits_agent_attrs(self):
        hook = InMemoryCreateSpanHook()
        client = _build(hook)
        _post(client)
        # agent_name may still be set from env, but agent_id with version should not
        tags = hook.spans[0].tags
        assert "gen_ai.agent.id" not in tags or ":" not in tags.get("gen_ai.agent.id", "")


# ===================================================================
# Conversation ID
# ===================================================================


class TestConversationId:
    """Verify conversation ID tracking."""

    def test_conversation_id_present(self):
        hook = InMemoryCreateSpanHook()
        client = _build(hook)
        _post(client, conversation="conv_abc123")
        assert hook.spans[0].tags.get("gen_ai.conversation.id") == "conv_abc123"

    def test_conversation_id_absent_when_not_provided(self):
        hook = InMemoryCreateSpanHook()
        client = _build(hook)
        _post(client)
        assert "gen_ai.conversation.id" not in hook.spans[0].tags


# ===================================================================
# Span Naming
# ===================================================================


class TestSpanNaming:
    """Verify span names follow conventions."""

    def test_span_name_is_create_response(self):
        hook = InMemoryCreateSpanHook()
        client = _build(hook)
        _post(client)
        assert hook.spans[0].name == "create_response"

    def test_span_name_consistent_with_model(self):
        hook = InMemoryCreateSpanHook()
        client = _build(hook)
        _post(client, model="gpt-4.1")
        assert hook.spans[0].name == "create_response"

    def test_span_name_consistent_without_model(self):
        hook = InMemoryCreateSpanHook()
        client = _build(hook)
        _post(client)
        assert hook.spans[0].name == "create_response"


# ===================================================================
# Request ID
# ===================================================================


class TestRequestId:
    """Verify request ID propagation from headers."""

    def test_request_id_from_header(self):
        hook = InMemoryCreateSpanHook()
        client = _build(hook)
        client.post(
            "/responses",
            json={"input": "hi", "stream": False},
            headers={"X-Request-Id": "req-123"},
        )
        assert hook.spans[0].tags.get("request.id") == "req-123"

    def test_request_id_absent_when_no_header(self):
        hook = InMemoryCreateSpanHook()
        client = _build(hook)
        _post(client)
        assert "request.id" not in hook.spans[0].tags

    def test_request_id_truncated_at_256(self):
        hook = InMemoryCreateSpanHook()
        client = _build(hook)
        client.post(
            "/responses",
            json={"input": "hi", "stream": False},
            headers={"X-Request-Id": "x" * 300},
        )
        assert len(hook.spans[0].tags.get("request.id", "")) == 256


# ===================================================================
# Span Consistency
# ===================================================================


class TestSpanConsistency:
    """Verify spans are consistent across multiple requests."""

    def test_each_request_creates_one_span(self):
        hook = InMemoryCreateSpanHook()
        client = _build(hook)
        _post(client)
        _post(client)
        _post(client)
        assert len(hook.spans) == 3

    def test_each_request_has_unique_response_id(self):
        hook = InMemoryCreateSpanHook()
        client = _build(hook)
        _post(client)
        _post(client)
        _post(client)
        resp_ids = {s.tags["gen_ai.response.id"] for s in hook.spans}
        assert len(resp_ids) == 3

    def test_required_attributes_on_every_span(self):
        """Every span must have the minimum required GenAI attributes."""
        hook = InMemoryCreateSpanHook()
        client = _build(hook)
        for _ in range(5):
            _post(client)

        required = [
            "gen_ai.operation.name",
            "gen_ai.provider.name",
            "service.name",
            "gen_ai.response.id",
        ]
        for span in hook.spans:
            for attr in required:
                assert attr in span.tags, (
                    f"Span '{span.name}' missing required attribute: {attr}"
                )

    def test_streaming_and_nonstreaming_have_same_attributes(self):
        """Both modes should produce spans with the same attribute set."""
        hook = InMemoryCreateSpanHook()
        client = _build(hook)
        _post(client, stream=False)
        _post(client, stream=True)

        assert len(hook.spans) == 2
        keys_nonstream = set(hook.spans[0].tags.keys())
        keys_stream = set(hook.spans[1].tags.keys())
        # Core attributes should be present in both
        core = {"gen_ai.operation.name", "gen_ai.provider.name", "service.name", "gen_ai.response.id"}
        assert core.issubset(keys_nonstream)
        assert core.issubset(keys_stream)
