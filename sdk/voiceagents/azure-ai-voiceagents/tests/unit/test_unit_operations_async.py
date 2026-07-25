# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Asynchronous request/response tests for the generated HTTP operations.

Mirrors ``test_unit_operations.py`` for the async client. The coroutines are
driven with ``asyncio.run`` so the module does not depend on a pytest asyncio
plugin. An in-memory mock transport replays canned responses (no network, no
recordings) so routes, the ``Foundry-Features`` opt-in header, serialization,
paging, and audio streaming are all asserted against the real async pipeline.
"""

import asyncio

import pytest

from azure.core.exceptions import ResourceNotFoundError

from azure.ai.voiceagents.aio import VoiceAgentsClient
from azure.ai.voiceagents.models import AgentDefinitionOptInKeys

from _mock_transport import (
    AsyncMockTransport,
    FakeAsyncCredential,
    request_json,
    request_path,
    request_query,
)

ENDPOINT = "https://example.services.ai.azure.com/api/projects/my-project"
PREVIEW = AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW
# The serialized value the opt-in feature flag flows onto the wire as.
FOUNDRY_FEATURES = "VoiceAgents=V1Preview"


# ---------------------------------------------------------------------------
# Management operations (voice_agents)
# ---------------------------------------------------------------------------


def test_create_voice_agent_posts_body_with_opt_in_header():
    async def run():
        def handler(request):
            return 200, {"object": "agent", "id": "agent-123", "name": "my-agent", "versions": {}}, {}

        transport = AsyncMockTransport(handler)
        client = VoiceAgentsClient(ENDPOINT, FakeAsyncCredential(), transport=transport)
        result = await client.voice_agents.create_voice_agent(
            body={"name": "my-agent", "definition": {"model": "gpt-realtime"}},
            foundry_features=PREVIEW,
        )

        request = transport.requests[0]
        assert request.method == "POST"
        assert request_path(request).endswith("/voice_agents")
        assert request.headers.get("Foundry-Features") == FOUNDRY_FEATURES
        assert request_json(request)["name"] == "my-agent"
        assert result.id == "agent-123"

    asyncio.run(run())


def test_list_voice_agents_paginates_and_propagates_cursor():
    async def run():
        def handler(request):
            if "after=agent-1" in request_query(request):
                return 200, {"object": "list", "data": [{"object": "agent", "id": "agent-2", "name": "second", "versions": {}}], "last_id": None}, {}
            return 200, {"object": "list", "data": [{"object": "agent", "id": "agent-1", "name": "first", "versions": {}}], "last_id": "agent-1"}, {}

        transport = AsyncMockTransport(handler)
        client = VoiceAgentsClient(ENDPOINT, FakeAsyncCredential(), transport=transport)

        agents = []
        async for agent in client.voice_agents.list_voice_agents(foundry_features=PREVIEW):
            agents.append(agent)

        assert [a.name for a in agents] == ["first", "second"]
        assert len(transport.requests) == 2
        assert "after" not in request_query(transport.requests[0])
        assert "after=agent-1" in request_query(transport.requests[1])
        for request in transport.requests:
            assert request_path(request).endswith("/voice_agents")
            assert request.headers.get("Foundry-Features") == FOUNDRY_FEATURES

    asyncio.run(run())


def test_get_voice_agent_route_and_deserialization():
    async def run():
        def handler(request):
            return 200, {"object": "agent", "id": "agent-9", "name": "my-agent", "versions": {}}, {}

        transport = AsyncMockTransport(handler)
        client = VoiceAgentsClient(ENDPOINT, FakeAsyncCredential(), transport=transport)
        result = await client.voice_agents.get_voice_agent("my-agent", foundry_features=PREVIEW)

        request = transport.requests[0]
        assert request.method == "GET"
        assert request_path(request).endswith("/voice_agents/my-agent")
        assert request.headers.get("Foundry-Features") == FOUNDRY_FEATURES
        assert result.id == "agent-9"

    asyncio.run(run())


def test_delete_voice_agent_route_and_deserialization():
    async def run():
        def handler(request):
            return 200, {"object": "agent.deleted", "name": "my-agent", "deleted": True}, {}

        transport = AsyncMockTransport(handler)
        client = VoiceAgentsClient(ENDPOINT, FakeAsyncCredential(), transport=transport)
        result = await client.voice_agents.delete_voice_agent("my-agent", foundry_features=PREVIEW)

        request = transport.requests[0]
        assert request.method == "DELETE"
        assert request_path(request).endswith("/voice_agents/my-agent")
        assert request.headers.get("Foundry-Features") == FOUNDRY_FEATURES
        assert result.deleted is True

    asyncio.run(run())


# ---------------------------------------------------------------------------
# Conversation operations (agent_endpoint_conversations)
# ---------------------------------------------------------------------------


def test_get_agent_conversation_route_and_deserialization():
    async def run():
        def handler(request):
            return 200, {"id": "conv-1", "object": "voice.conversation", "status": "completed", "created_at": 1700000000}, {}

        transport = AsyncMockTransport(handler)
        client = VoiceAgentsClient(ENDPOINT, FakeAsyncCredential(), transport=transport)
        result = await client.agent_endpoint_conversations.get_agent_conversation(
            "my-agent", "conv-1", foundry_features=PREVIEW
        )

        request = transport.requests[0]
        assert request.method == "GET"
        assert request_path(request).endswith(
            "/agents/my-agent/endpoint/protocols/voice/conversations/conv-1"
        )
        assert request.headers.get("Foundry-Features") == FOUNDRY_FEATURES
        assert result.id == "conv-1"

    asyncio.run(run())


def test_list_agent_conversation_items_paginates_and_propagates_cursor():
    async def run():
        def handler(request):
            if "after=item-1" in request_query(request):
                return 200, {"object": "list", "data": [{"id": "item-2", "type": "message"}], "last_id": None}, {}
            return 200, {"object": "list", "data": [{"id": "item-1", "type": "message"}], "last_id": "item-1"}, {}

        transport = AsyncMockTransport(handler)
        client = VoiceAgentsClient(ENDPOINT, FakeAsyncCredential(), transport=transport)

        items = []
        async for item in client.agent_endpoint_conversations.list_agent_conversation_items(
            "my-agent", "conv-1", foundry_features=PREVIEW
        ):
            items.append(item)

        assert [item["id"] for item in items] == ["item-1", "item-2"]
        assert len(transport.requests) == 2
        assert "after=item-1" in request_query(transport.requests[1])
        for request in transport.requests:
            assert request.headers.get("Foundry-Features") == FOUNDRY_FEATURES

    asyncio.run(run())


def test_get_agent_conversation_item_audio_metadata():
    async def run():
        def handler(request):
            return 200, {
                "conversation_id": "conv-1",
                "item_id": "item-1",
                "format": "wav",
                "codec": "pcm16",
                "blob_path": "https://storage.example/blob.wav",
            }, {}

        transport = AsyncMockTransport(handler)
        client = VoiceAgentsClient(ENDPOINT, FakeAsyncCredential(), transport=transport)
        result = await client.agent_endpoint_conversations.get_agent_conversation_item_audio(
            "my-agent", "conv-1", "item-1", foundry_features=PREVIEW
        )

        request = transport.requests[0]
        assert request_path(request).endswith(
            "/agents/my-agent/endpoint/protocols/voice/conversations/conv-1/items/item-1/audio"
        )
        assert result.format == "wav"
        assert result.blob_path == "https://storage.example/blob.wav"

    asyncio.run(run())


def test_get_agent_conversation_audio_content_streams_bytes():
    async def run():
        payload = b"RIFF....WAVEfmt merged-call-audio"

        def handler(request):
            return 200, payload, {"content-type": "audio/wav"}

        transport = AsyncMockTransport(handler)
        client = VoiceAgentsClient(ENDPOINT, FakeAsyncCredential(), transport=transport)
        stream = await client.agent_endpoint_conversations.get_agent_conversation_audio_content(
            "my-agent", "conv-1", foundry_features=PREVIEW
        )
        chunks = [chunk async for chunk in stream]

        request = transport.requests[0]
        assert request_path(request).endswith(
            "/agents/my-agent/endpoint/protocols/voice/conversations/conv-1/audio/content"
        )
        assert request.headers.get("Foundry-Features") == FOUNDRY_FEATURES
        assert b"".join(chunks) == payload

    asyncio.run(run())


def test_error_status_maps_to_typed_exception():
    async def run():
        def handler(request):
            return 404, {"error": {"code": "NotFound", "message": "no such conversation"}}, {}

        transport = AsyncMockTransport(handler)
        client = VoiceAgentsClient(ENDPOINT, FakeAsyncCredential(), transport=transport)
        with pytest.raises(ResourceNotFoundError):
            await client.agent_endpoint_conversations.get_agent_conversation(
                "my-agent", "missing", foundry_features=PREVIEW
            )

    asyncio.run(run())
