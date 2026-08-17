# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import time
from unittest.mock import AsyncMock
from urllib.parse import urlparse

import jwt
import pytest
from azure.core.credentials import AccessToken, AzureKeyCredential

from azure.messaging.webpubsubservice.chat.aio import WebPubSubChatServiceClient


ACCESS_KEY = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ABCDEFGH"
ENDPOINT = "https://example.webpubsub.azure.com"
HUB = "chat"
CHAT_ROLES = ["webpubsub.getGroupState", "webpubsub.setGroupState"]


class RequestCaptured(Exception):
    pass


class FakeAsyncTokenCredential:
    async def get_token(self, *scopes, **kwargs):
        return AccessToken("entra-token", int(time.time()) + 3600)


async def _capture_list_roles_request(client):
    captured = {}

    def capture(pipeline_request):
        captured["request"] = pipeline_request.http_request
        raise RequestCaptured()

    with pytest.raises(RequestCaptured):
        async for _ in client.list_roles(raw_request_hook=capture):
            pass
    return captured["request"]


@pytest.mark.asyncio
async def test_async_connection_string_and_key_request_match_sync_behavior():
    client = WebPubSubChatServiceClient.from_connection_string(
        f"Endpoint={ENDPOINT};AccessKey={ACCESS_KEY};Port=8443;Version=1.0;",
        HUB,
    )
    try:
        request = await _capture_list_roles_request(client)
        token = request.headers["Authorization"].removeprefix("Bearer ")
        claims = jwt.decode(token, ACCESS_KEY, algorithms=["HS256"], audience=request.url)

        assert client._config.endpoint == f"{ENDPOINT}:8443"
        assert claims["aud"] == request.url
        assert 0 < claims["exp"] - int(time.time()) <= 60
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_async_reverse_proxy_with_key_uses_original_audience():
    proxy_endpoint = "https://proxy.contoso.com"
    client = WebPubSubChatServiceClient(
        ENDPOINT,
        HUB,
        AzureKeyCredential(ACCESS_KEY),
        reverse_proxy_endpoint=proxy_endpoint,
    )
    try:
        request = await _capture_list_roles_request(client)
        original_url = request.url.replace(proxy_endpoint, ENDPOINT, 1)
        token = request.headers["Authorization"].removeprefix("Bearer ")
        claims = jwt.decode(token, ACCESS_KEY, algorithms=["HS256"], audience=original_url)

        assert urlparse(request.url).netloc == "proxy.contoso.com"
        assert claims["aud"] == original_url
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_async_reverse_proxy_with_entra_credential_keeps_bearer_token():
    client = WebPubSubChatServiceClient(
        ENDPOINT,
        HUB,
        FakeAsyncTokenCredential(),
        reverse_proxy_endpoint="https://proxy.contoso.com",
    )
    try:
        request = await _capture_list_roles_request(client)
        assert urlparse(request.url).netloc == "proxy.contoso.com"
        assert request.headers["Authorization"] == "Bearer entra-token"
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_async_client_access_token_delegates_fixed_chat_requirements():
    client = WebPubSubChatServiceClient(ENDPOINT, HUB, AzureKeyCredential(ACCESS_KEY))
    expected = {"baseUrl": "wss://example", "token": "token", "url": "wss://example?access_token=token"}
    client._web_pub_sub_service_client.get_client_access_token = AsyncMock(return_value=expected)
    try:
        result = await client.get_client_access_token(user_id="alice")
        assert result is expected
        client._web_pub_sub_service_client.get_client_access_token.assert_awaited_once_with(
            user_id="alice",
            roles=CHAT_ROLES,
            minutes_to_expire=60,
            groups=[],
            client_protocol="Default",
        )
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_async_entra_client_access_delegation_propagates_reverse_proxy():
    credential = FakeAsyncTokenCredential()
    proxy_endpoint = "https://proxy.contoso.com"
    client = WebPubSubChatServiceClient(
        ENDPOINT,
        HUB,
        credential,
        reverse_proxy_endpoint=proxy_endpoint,
    )
    expected = {"baseUrl": "wss://example", "token": "token", "url": "wss://example?access_token=token"}
    client._web_pub_sub_service_client.get_client_access_token = AsyncMock(return_value=expected)
    try:
        inner = client._web_pub_sub_service_client
        assert inner._config.credential is credential
        assert inner._config.proxy_policy._endpoint == ENDPOINT
        assert inner._config.proxy_policy._reverse_proxy_endpoint == proxy_endpoint
        assert await client.get_client_access_token(user_id="alice") is expected
        inner.get_client_access_token.assert_awaited_once_with(
            user_id="alice",
            roles=CHAT_ROLES,
            minutes_to_expire=60,
            groups=[],
            client_protocol="Default",
        )
    finally:
        await client.close()
