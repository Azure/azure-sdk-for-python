# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Unit tests for the Brotli/aiohttp workaround in aio/_patch.py. No network calls.

azure-core's AioHttpTransport disables aiohttp's native response decompression
and only re-implements gzip/deflate, while aiohttp advertises "Accept-Encoding:
br" by default. The async VoiceAgentsClient works around this by injecting its
own transport (unless the caller already supplied one) that only advertises
encodings azure-core can actually decompress.

These tests must be `async def` because constructing the injected transport
builds an aiohttp.ClientSession, which requires a running event loop.
"""
import aiohttp
from azure.core.pipeline.transport import AioHttpTransport

from azure.ai.voiceagents.aio import VoiceAgentsClient

ENDPOINT = "https://example.services.ai.azure.com/api/projects/p"


class _FakeAsyncCredential:
    async def get_token(self, *scopes, **kwargs):
        raise NotImplementedError

    async def close(self):
        pass


async def test_default_transport_only_advertises_gzip_deflate():
    async with VoiceAgentsClient(endpoint=ENDPOINT, credential=_FakeAsyncCredential()) as client:
        transport = client._client._pipeline._transport
        assert isinstance(transport, AioHttpTransport)
        assert transport.session.headers.get("Accept-Encoding") == "gzip, deflate"


async def test_explicit_transport_bypasses_workaround():
    custom_session = aiohttp.ClientSession()
    custom_transport = AioHttpTransport(session=custom_session)
    try:
        async with VoiceAgentsClient(
            endpoint=ENDPOINT, credential=_FakeAsyncCredential(), transport=custom_transport
        ) as client:
            assert client._client._pipeline._transport is custom_transport
    finally:
        await custom_session.close()
