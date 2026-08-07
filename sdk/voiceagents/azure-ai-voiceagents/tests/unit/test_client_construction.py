# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Unit tests for sync/async client construction. No network calls.

Note: constructing the async client requires a running event loop (it builds
an aiohttp.ClientSession by default -- see test_brotli_workaround.py), so the
async cases below are `async def` tests.
"""
from azure.ai.voiceagents import VoiceAgentsClient
from azure.ai.voiceagents.aio import VoiceAgentsClient as AsyncVoiceAgentsClient
from azure.ai.voiceagents.operations import (
    AgentEndpointConversationsOperations,
    VoiceAgentsOperations,
)

ENDPOINT = "https://example.services.ai.azure.com/api/projects/p"


class _FakeCredential:
    def get_token(self, *scopes, **kwargs):
        raise NotImplementedError


class _FakeAsyncCredential:
    async def get_token(self, *scopes, **kwargs):
        raise NotImplementedError

    async def close(self):
        pass


def test_sync_client_exposes_operation_groups():
    client = VoiceAgentsClient(endpoint=ENDPOINT, credential=_FakeCredential())
    try:
        assert isinstance(client.voice_agents, VoiceAgentsOperations)
        assert isinstance(client.agent_endpoint_conversations, AgentEndpointConversationsOperations)
    finally:
        client.close()


def test_sync_client_is_a_context_manager():
    with VoiceAgentsClient(endpoint=ENDPOINT, credential=_FakeCredential()) as client:
        assert client.voice_agents is not None


async def test_async_client_exposes_operation_groups():
    async with AsyncVoiceAgentsClient(endpoint=ENDPOINT, credential=_FakeAsyncCredential()) as client:
        assert client.voice_agents is not None
        assert client.agent_endpoint_conversations is not None


async def test_async_client_realtime_property_is_lazy_and_cached():
    async with AsyncVoiceAgentsClient(endpoint=ENDPOINT, credential=_FakeAsyncCredential()) as client:
        assert client._realtime is None
        realtime = client.realtime
        assert realtime is not None
        assert client.realtime is realtime  # cached, not recreated on each access
