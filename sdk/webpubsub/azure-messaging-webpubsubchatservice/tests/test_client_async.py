# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import time
from unittest.mock import AsyncMock, Mock, patch
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
        claims = jwt.decode(
            token, ACCESS_KEY, algorithms=["HS256"], audience=request.url
        )

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
        claims = jwt.decode(
            token, ACCESS_KEY, algorithms=["HS256"], audience=original_url
        )

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
async def test_async_token_credential_client_access_token_uses_generated_operation():
    client = WebPubSubChatServiceClient(ENDPOINT, HUB, FakeAsyncTokenCredential())
    try:
        with patch.object(
            client, "_generate_client_token", new_callable=AsyncMock
        ) as generate:
            generate.return_value = Mock(token="token")
            result = await client.get_client_access_token(user_id="alice")

        base_url = f"wss://example.webpubsub.azure.com/client/hubs/{HUB}"
        assert result == {
            "baseUrl": base_url,
            "token": "token",
            "url": f"{base_url}?access_token=token",
        }
        generate.assert_awaited_once_with(
            user_id="alice", role=CHAT_ROLES, minutes_to_expire=60
        )
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_async_key_client_access_token_is_generated_locally():
    client = WebPubSubChatServiceClient(ENDPOINT, HUB, AzureKeyCredential(ACCESS_KEY))
    try:
        with patch.object(
            client, "_generate_client_token", new_callable=AsyncMock
        ) as generate:
            result = await client.get_client_access_token(user_id="alice")

        generate.assert_not_awaited()
        base_url = f"wss://example.webpubsub.azure.com/client/hubs/{HUB}"
        assert result["baseUrl"] == base_url
        assert result["url"] == f"{base_url}?access_token={result['token']}"
        claims = jwt.decode(
            result["token"],
            ACCESS_KEY,
            algorithms=["HS256"],
            audience=result["baseUrl"].replace("wss://", "https://"),
        )
        assert claims["sub"] == "alice"
        assert claims["role"] == CHAT_ROLES
        assert 3595 <= claims["exp"] - claims["iat"] <= 3605
    finally:
        await client.close()
