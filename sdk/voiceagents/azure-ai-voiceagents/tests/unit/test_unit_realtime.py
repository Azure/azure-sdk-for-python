# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Unit tests for the async realtime (WebSocket) interface.

Realtime streaming is an interface-only preview: the service-side route is not
wired up yet, so ``connect()`` raises ``NotImplementedError`` up front. These
tests assert that contract plus the URL-derivation helper. No network is used.
"""

import time

import pytest

from azure.core.credentials import AccessToken

from azure.ai.voiceagents.aio import VoiceAgentsClient
from azure.ai.voiceagents.aio._realtime import AsyncRealtime, _to_ws_url

ENDPOINT = "https://example.services.ai.azure.com/api/projects/my-project"


class FakeAsyncCredential:
    async def get_token(self, *scopes, **kwargs):
        return AccessToken("fake-token", int(time.time()) + 3600)

    async def close(self):
        return None


def test_to_ws_url_https_to_wss():
    url = _to_ws_url("https://host.example.com/api/projects/p", "my-agent")
    assert url == "wss://host.example.com/api/projects/p/agents/my-agent/endpoint/protocols/voice"


def test_to_ws_url_http_to_ws():
    url = _to_ws_url("http://localhost:8080", "agent-1")
    assert url == "ws://localhost:8080/agents/agent-1/endpoint/protocols/voice"


def test_to_ws_url_strips_trailing_slash():
    url = _to_ws_url("https://host.example.com/api/projects/p/", "agent-1")
    assert url == "wss://host.example.com/api/projects/p/agents/agent-1/endpoint/protocols/voice"


def test_realtime_property_returns_async_realtime():
    client = VoiceAgentsClient(ENDPOINT, FakeAsyncCredential())
    assert isinstance(client.realtime, AsyncRealtime)


def test_connect_raises_not_implemented():
    client = VoiceAgentsClient(ENDPOINT, FakeAsyncCredential())
    with pytest.raises(NotImplementedError):
        client.realtime.connect(agent_name="my-agent")


def test_connect_not_implemented_message_mentions_streaming():
    client = VoiceAgentsClient(ENDPOINT, FakeAsyncCredential())
    with pytest.raises(NotImplementedError) as exc_info:
        client.realtime.connect(agent_name="my-agent")
    assert "streaming" in str(exc_info.value).lower()
