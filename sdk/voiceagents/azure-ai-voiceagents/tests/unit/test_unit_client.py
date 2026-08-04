# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Unit tests for client construction and configuration defaults.

These tests never issue network calls; they only build the client objects and
inspect their configuration.
"""

import time

from azure.core.credentials import AccessToken

from azure.ai.voiceagents import VoiceAgentsClient
from azure.ai.voiceagents.aio import VoiceAgentsClient as AsyncVoiceAgentsClient

ENDPOINT = "https://example.services.ai.azure.com/api/projects/my-project"


class FakeCredential:
    """Minimal synchronous TokenCredential stand-in (never actually called)."""

    def get_token(self, *scopes, **kwargs):
        return AccessToken("fake-token", int(time.time()) + 3600)


class FakeAsyncCredential:
    """Minimal asynchronous TokenCredential stand-in (never actually called)."""

    async def get_token(self, *scopes, **kwargs):
        return AccessToken("fake-token", int(time.time()) + 3600)

    async def close(self):
        return None


def test_sync_client_default_api_version():
    client = VoiceAgentsClient(ENDPOINT, FakeCredential())
    assert client._config.api_version == "v1"


def test_sync_client_default_credential_scopes():
    client = VoiceAgentsClient(ENDPOINT, FakeCredential())
    assert client._config.credential_scopes == ["https://ai.azure.com/.default"]


def test_sync_client_endpoint_preserved():
    client = VoiceAgentsClient(ENDPOINT, FakeCredential())
    assert client._config.endpoint == ENDPOINT


def test_sync_client_api_version_override():
    client = VoiceAgentsClient(ENDPOINT, FakeCredential(), api_version="v1")
    assert client._config.api_version == "v1"


def test_sync_client_exposes_operation_groups():
    client = VoiceAgentsClient(ENDPOINT, FakeCredential())
    assert client.voice_agents is not None
    assert client.agent_endpoint_conversations is not None


def test_async_client_defaults():
    client = AsyncVoiceAgentsClient(ENDPOINT, FakeAsyncCredential())
    assert client._config.api_version == "v1"
    assert client._config.credential_scopes == ["https://ai.azure.com/.default"]


def test_async_client_exposes_realtime_property():
    client = AsyncVoiceAgentsClient(ENDPOINT, FakeAsyncCredential())
    # The realtime surface is exposed on the async client only.
    assert client.realtime is not None
