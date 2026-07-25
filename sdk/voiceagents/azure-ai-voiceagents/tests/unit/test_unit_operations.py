# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Synchronous request/response tests for the generated HTTP operations.

These tests drive the real client pipeline through an in-memory mock transport
(no network, no recordings). They assert the wire contract that would otherwise
only be exercised against a live service: the request route and method, the
``Foundry-Features`` preview opt-in header, request/response serialization,
paging cursor propagation, and audio byte streaming.
"""

import pytest

from azure.core.exceptions import ResourceNotFoundError

from azure.ai.voiceagents import VoiceAgentsClient
from azure.ai.voiceagents.models import AgentDefinitionOptInKeys

from _mock_transport import (
    FakeCredential,
    MockTransport,
    request_json,
    request_path,
    request_query,
)

ENDPOINT = "https://example.services.ai.azure.com/api/projects/my-project"
PREVIEW = AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW
# The serialized value the opt-in feature flag flows onto the wire as.
FOUNDRY_FEATURES = "VoiceAgents=V1Preview"


def _client(handler) -> VoiceAgentsClient:
    return VoiceAgentsClient(ENDPOINT, FakeCredential(), transport=MockTransport(handler))


# ---------------------------------------------------------------------------
# Management operations (voice_agents)
# ---------------------------------------------------------------------------


def test_create_voice_agent_posts_body_with_opt_in_header():
    def handler(request):
        return 200, {"object": "agent", "id": "agent-123", "name": "my-agent", "versions": {}}, {}

    transport = MockTransport(handler)
    client = VoiceAgentsClient(ENDPOINT, FakeCredential(), transport=transport)

    result = client.voice_agents.create_voice_agent(
        body={"name": "my-agent", "definition": {"model": "gpt-realtime"}},
        foundry_features=PREVIEW,
    )

    request = transport.requests[0]
    assert request.method == "POST"
    assert request_path(request).endswith("/voice_agents")
    assert request.headers.get("Foundry-Features") == FOUNDRY_FEATURES
    assert request_json(request)["name"] == "my-agent"
    assert result.id == "agent-123"
    assert result.name == "my-agent"


def test_list_voice_agents_paginates_and_propagates_cursor():
    def handler(request):
        if "after=agent-1" in request_query(request):
            return 200, {"object": "list", "data": [{"object": "agent", "id": "agent-2", "name": "second", "versions": {}}], "last_id": None}, {}
        return 200, {"object": "list", "data": [{"object": "agent", "id": "agent-1", "name": "first", "versions": {}}], "last_id": "agent-1"}, {}

    transport = MockTransport(handler)
    client = VoiceAgentsClient(ENDPOINT, FakeCredential(), transport=transport)

    agents = list(client.voice_agents.list_voice_agents(foundry_features=PREVIEW))

    assert [a.name for a in agents] == ["first", "second"]
    # Two pages were fetched; the second carried the cursor from the first page.
    assert len(transport.requests) == 2
    assert "after" not in request_query(transport.requests[0])
    assert "after=agent-1" in request_query(transport.requests[1])
    for request in transport.requests:
        assert request_path(request).endswith("/voice_agents")
        assert request.headers.get("Foundry-Features") == FOUNDRY_FEATURES


def test_get_voice_agent_route_and_deserialization():
    def handler(request):
        return 200, {"object": "agent", "id": "agent-9", "name": "my-agent", "versions": {}}, {}

    transport = MockTransport(handler)
    client = VoiceAgentsClient(ENDPOINT, FakeCredential(), transport=transport)

    result = client.voice_agents.get_voice_agent("my-agent", foundry_features=PREVIEW)

    request = transport.requests[0]
    assert request.method == "GET"
    assert request_path(request).endswith("/voice_agents/my-agent")
    assert request.headers.get("Foundry-Features") == FOUNDRY_FEATURES
    assert result.id == "agent-9"


def test_update_voice_agent_route_and_body():
    def handler(request):
        return 200, {"object": "agent", "id": "agent-9", "name": "my-agent", "versions": {}}, {}

    transport = MockTransport(handler)
    client = VoiceAgentsClient(ENDPOINT, FakeCredential(), transport=transport)

    result = client.voice_agents.update_voice_agent(
        "my-agent",
        body={"description": "updated"},
        foundry_features=PREVIEW,
    )

    request = transport.requests[0]
    assert request.method == "POST"
    assert request_path(request).endswith("/voice_agents/my-agent")
    assert request.headers.get("Foundry-Features") == FOUNDRY_FEATURES
    assert request_json(request)["description"] == "updated"
    assert result.name == "my-agent"


def test_delete_voice_agent_route_and_deserialization():
    def handler(request):
        return 200, {"object": "agent.deleted", "name": "my-agent", "deleted": True}, {}

    transport = MockTransport(handler)
    client = VoiceAgentsClient(ENDPOINT, FakeCredential(), transport=transport)

    result = client.voice_agents.delete_voice_agent("my-agent", foundry_features=PREVIEW)

    request = transport.requests[0]
    assert request.method == "DELETE"
    assert request_path(request).endswith("/voice_agents/my-agent")
    assert request.headers.get("Foundry-Features") == FOUNDRY_FEATURES
    assert result.deleted is True
    assert result.name == "my-agent"


# ---------------------------------------------------------------------------
# Conversation operations (agent_endpoint_conversations)
# ---------------------------------------------------------------------------


def test_get_agent_conversation_route_and_deserialization():
    def handler(request):
        return 200, {"id": "conv-1", "object": "voice.conversation", "status": "completed", "created_at": 1700000000}, {}

    transport = MockTransport(handler)
    client = VoiceAgentsClient(ENDPOINT, FakeCredential(), transport=transport)

    result = client.agent_endpoint_conversations.get_agent_conversation(
        "my-agent", "conv-1", foundry_features=PREVIEW
    )

    request = transport.requests[0]
    assert request.method == "GET"
    assert request_path(request).endswith(
        "/agents/my-agent/endpoint/protocols/voice/conversations/conv-1"
    )
    assert request.headers.get("Foundry-Features") == FOUNDRY_FEATURES
    assert result.id == "conv-1"
    assert result.status == "completed"


def test_list_agent_conversation_items_paginates_and_propagates_cursor():
    def handler(request):
        if "after=item-1" in request_query(request):
            return 200, {"object": "list", "data": [{"id": "item-2", "type": "message"}], "last_id": None}, {}
        return 200, {"object": "list", "data": [{"id": "item-1", "type": "message"}], "last_id": "item-1"}, {}

    transport = MockTransport(handler)
    client = VoiceAgentsClient(ENDPOINT, FakeCredential(), transport=transport)

    items = list(
        client.agent_endpoint_conversations.list_agent_conversation_items(
            "my-agent", "conv-1", foundry_features=PREVIEW
        )
    )

    assert [item["id"] for item in items] == ["item-1", "item-2"]
    assert len(transport.requests) == 2
    assert "after=item-1" in request_query(transport.requests[1])
    for request in transport.requests:
        assert request_path(request).endswith(
            "/agents/my-agent/endpoint/protocols/voice/conversations/conv-1/items"
        )
        assert request.headers.get("Foundry-Features") == FOUNDRY_FEATURES


def test_get_agent_conversation_item_audio_metadata():
    def handler(request):
        return 200, {
            "conversation_id": "conv-1",
            "item_id": "item-1",
            "format": "wav",
            "codec": "pcm16",
            "blob_path": "https://storage.example/blob.wav",
        }, {}

    transport = MockTransport(handler)
    client = VoiceAgentsClient(ENDPOINT, FakeCredential(), transport=transport)

    result = client.agent_endpoint_conversations.get_agent_conversation_item_audio(
        "my-agent", "conv-1", "item-1", foundry_features=PREVIEW
    )

    request = transport.requests[0]
    assert request_path(request).endswith(
        "/agents/my-agent/endpoint/protocols/voice/conversations/conv-1/items/item-1/audio"
    )
    assert request.headers.get("Foundry-Features") == FOUNDRY_FEATURES
    assert result.format == "wav"
    assert result.blob_path == "https://storage.example/blob.wav"


def test_get_agent_conversation_audio_content_streams_bytes():
    payload = b"RIFF....WAVEfmt merged-call-audio"

    def handler(request):
        return 200, payload, {"content-type": "audio/wav"}

    transport = MockTransport(handler)
    client = VoiceAgentsClient(ENDPOINT, FakeCredential(), transport=transport)

    stream = client.agent_endpoint_conversations.get_agent_conversation_audio_content(
        "my-agent", "conv-1", foundry_features=PREVIEW
    )
    data = b"".join(stream)

    request = transport.requests[0]
    assert request_path(request).endswith(
        "/agents/my-agent/endpoint/protocols/voice/conversations/conv-1/audio/content"
    )
    assert request.headers.get("Foundry-Features") == FOUNDRY_FEATURES
    assert data == payload


def test_get_agent_conversation_item_audio_content_streams_bytes():
    payload = b"RIFF....WAVEfmt single-turn-audio"

    def handler(request):
        return 200, payload, {"content-type": "audio/wav"}

    transport = MockTransport(handler)
    client = VoiceAgentsClient(ENDPOINT, FakeCredential(), transport=transport)

    stream = client.agent_endpoint_conversations.get_agent_conversation_item_audio_content(
        "my-agent", "conv-1", "item-1", foundry_features=PREVIEW
    )
    data = b"".join(stream)

    request = transport.requests[0]
    assert request_path(request).endswith(
        "/agents/my-agent/endpoint/protocols/voice/conversations/conv-1/items/item-1/audio/content"
    )
    assert data == payload


def test_error_status_maps_to_typed_exception():
    def handler(request):
        return 404, {"error": {"code": "NotFound", "message": "no such conversation"}}, {}

    transport = MockTransport(handler)
    client = VoiceAgentsClient(ENDPOINT, FakeCredential(), transport=transport)

    with pytest.raises(ResourceNotFoundError):
        client.agent_endpoint_conversations.get_agent_conversation(
            "my-agent", "missing", foundry_features=PREVIEW
        )
