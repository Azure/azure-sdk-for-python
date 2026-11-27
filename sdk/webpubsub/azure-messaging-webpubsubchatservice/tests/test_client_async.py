# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import runpy
import time
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch
from urllib.parse import urlparse

import jwt
import pytest
from azure.core.credentials import AccessToken, AzureKeyCredential
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.core.rest import HttpRequest

from azure.messaging.webpubsubchatservice.aio import WebPubSubChatServiceClient
from azure.messaging.webpubsubchatservice.models import (
    ChatMessageUpdate,
    ChatRoleCreateOrReplace,
    ChatRoomCreateOrReplace,
    ChatRoomMemberCreateOrReplace,
    ChatTopicCreateOrReplace,
    ChatTopicUpdate,
    HumanChatUserCreateOrReplace,
    MessageContent,
)



ACCESS_KEY = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ABCDEFGH"
ENDPOINT = "https://example.webpubsub.azure.com"
HUB = "chat"
CHAT_ROLES = ["webpubsub.getGroupState", "webpubsub.setGroupState"]


class RequestCaptured(Exception):
    pass


class FakeAsyncTokenCredential:
    async def get_token(self, *_scopes, **_kwargs):
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
        conn_str=f"Endpoint={ENDPOINT};AccessKey={ACCESS_KEY};Port=8443;Version=1.0;",
        hub=HUB,
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
@pytest.mark.parametrize("endpoint_suffix", ["", "/"])
@pytest.mark.parametrize("proxy_suffix", ["", "/"])
async def test_async_reverse_proxy_with_key_uses_original_audience(endpoint_suffix, proxy_suffix):
    proxy_endpoint = "https://proxy.contoso.com"
    async with WebPubSubChatServiceClient(ENDPOINT, HUB, AzureKeyCredential(ACCESS_KEY)) as direct_client:
        original_url = (await _capture_list_roles_request(direct_client)).url
    client = WebPubSubChatServiceClient(
        ENDPOINT + endpoint_suffix,
        HUB,
        AzureKeyCredential(ACCESS_KEY),
        reverse_proxy_endpoint=proxy_endpoint + proxy_suffix,
    )
    try:
        request = await _capture_list_roles_request(client)
        assert request.url == original_url.replace(ENDPOINT, proxy_endpoint, 1)
        token = request.headers["Authorization"].removeprefix("Bearer ")
        claims = jwt.decode(token, ACCESS_KEY, algorithms=["HS256"], audience=original_url)

        assert urlparse(request.url).netloc == "proxy.contoso.com"
        assert claims["aud"] == original_url
    finally:
        await client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint_suffix", ["", "/"])
@pytest.mark.parametrize("proxy_suffix", ["", "/"])
async def test_async_reverse_proxy_with_entra_credential_keeps_bearer_token(endpoint_suffix, proxy_suffix):
    proxy_endpoint = "https://proxy.contoso.com"
    async with WebPubSubChatServiceClient(ENDPOINT, HUB, FakeAsyncTokenCredential()) as direct_client:
        original_url = (await _capture_list_roles_request(direct_client)).url
    client = WebPubSubChatServiceClient(
        ENDPOINT + endpoint_suffix,
        HUB,
        FakeAsyncTokenCredential(),
        reverse_proxy_endpoint=proxy_endpoint + proxy_suffix,
    )
    try:
        request = await _capture_list_roles_request(client)
        assert request.url == original_url.replace(ENDPOINT, proxy_endpoint, 1)
        assert urlparse(request.url).netloc == "proxy.contoso.com"
        assert request.headers["Authorization"] == "Bearer entra-token"
    finally:
        await client.close()


@pytest.mark.asyncio
async def test_async_token_credential_client_access_token_uses_generated_operation():
    client = WebPubSubChatServiceClient(ENDPOINT, HUB, FakeAsyncTokenCredential())
    try:
        with patch.object(client, "_generate_client_token", new_callable=AsyncMock) as generate:
            generate.return_value = Mock(token="token")
            result = await client.get_client_access_token(user_id="alice")

        base_url = f"wss://example.webpubsub.azure.com/client/hubs/{HUB}"
        assert result == {
            "baseUrl": base_url,
            "token": "token",
            "url": f"{base_url}?access_token=token",
        }
        generate.assert_awaited_once_with(user_id="alice", role=CHAT_ROLES, minutes_to_expire=60)
    finally:
        await client.close()


# Keep the capsys name: pytest uses it to inject the fixture that captures stdout and stderr.
@pytest.mark.asyncio
async def test_async_client_access_sample_does_not_log_token(monkeypatch, capsys):
    monkeypatch.setenv("WPS_CHAT_CONNECTION_STRING", f"Endpoint={ENDPOINT};AccessKey={ACCESS_KEY}")
    base_url = f"wss://example.webpubsub.azure.com/client/hubs/{HUB}"
    access = {"baseUrl": base_url, "token": "secret-token", "url": f"{base_url}?access_token=secret-token"}
    sample_path = Path(__file__).resolve().parents[1] / "samples" / "sample_client_access_async.py"
    sample = runpy.run_path(str(sample_path))

    with patch.object(WebPubSubChatServiceClient, "get_client_access_token", return_value=access):
        await sample["main"]()

    captured = capsys.readouterr()
    assert captured.out == f"{base_url}\n"
    assert captured.err == ""


@pytest.mark.asyncio
async def test_async_key_client_access_token_is_generated_locally():
    client = WebPubSubChatServiceClient(ENDPOINT, HUB, AzureKeyCredential(ACCESS_KEY))
    try:
        with patch.object(client, "_generate_client_token", new_callable=AsyncMock) as generate:
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


@pytest.mark.asyncio
@pytest.mark.parametrize("credential", [AzureKeyCredential(ACCESS_KEY), FakeAsyncTokenCredential()])
@pytest.mark.parametrize("minutes_to_expire", [0, -1])
async def test_async_client_access_token_rejects_invalid_expiration(credential, minutes_to_expire):
    client = WebPubSubChatServiceClient(ENDPOINT, HUB, credential)
    try:
        with patch.object(client, "_generate_client_token", new_callable=AsyncMock) as generate:
            with pytest.raises(ValueError, match="minutes_to_expire must be at least 1"):
                await client.get_client_access_token(minutes_to_expire=minutes_to_expire)
        generate.assert_not_awaited()
    finally:
        await client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint", ["example.com", "ftp://example.com"])
@pytest.mark.parametrize("use_key", [True, False])
async def test_async_client_access_token_rejects_unsupported_endpoint(endpoint, use_key):
    credential = AzureKeyCredential(ACCESS_KEY) if use_key else FakeAsyncTokenCredential()
    async with WebPubSubChatServiceClient(endpoint, HUB, credential) as client:
        with patch.object(client, "_generate_client_token", new_callable=AsyncMock) as generate:
            generate.return_value = Mock(token="token")
            with pytest.raises(ValueError, match="HTTP or HTTPS"):
                await client.get_client_access_token()
        generate.assert_not_awaited()


@pytest.mark.parametrize("dot_segment", [".", "..", "%2e", "%2E", "%2e%2e", ".%2e", "%2e.", "%252e", "%252e%252e"])
def test_async_hub_rejects_dot_path_segments(dot_segment):
    with pytest.raises(ValueError, match="must not be '\\.' or '\\.\\.'"):
        WebPubSubChatServiceClient(ENDPOINT, dot_segment, AzureKeyCredential(ACCESS_KEY))


async def _consume_async_iter(iterable):
    return [item async for item in iterable]


@pytest.mark.asyncio
@pytest.mark.parametrize("dot_segment", [".", "..", "%2e", "%2E", "%2e%2e", ".%2e", "%2e.", "%252e", "%252e%252e"])
@pytest.mark.parametrize(
    "invoke",
    [
        lambda client, seg: client.create_or_replace_role(seg, ChatRoleCreateOrReplace(permissions=[])),
        lambda client, seg: client.get_role(seg),
        lambda client, seg: client.delete_role(seg),
        lambda client, seg: client.create_or_replace_room(seg, ChatRoomCreateOrReplace(title="Room")),
        lambda client, seg: client.get_room(seg),
        lambda client, seg: client.delete_room(seg),
        lambda client, seg: _consume_async_iter(client.list_room_members(seg)),
        lambda client, seg: client.create_or_replace_room_member(
            seg, "alice", ChatRoomMemberCreateOrReplace(role_name="room.member")
        ),
        lambda client, seg: client.create_or_replace_room_member(
            "general", seg, ChatRoomMemberCreateOrReplace(role_name="room.member")
        ),
        lambda client, seg: client.delete_room_member(seg, "alice"),
        lambda client, seg: client.delete_room_member("general", seg),
        lambda client, seg: _consume_async_iter(client.list_topics(seg)),
        lambda client, seg: client.create_or_replace_topic(seg, "topic", ChatTopicCreateOrReplace(title="Topic")),
        lambda client, seg: client.create_or_replace_topic("general", seg, ChatTopicCreateOrReplace(title="Topic")),
        lambda client, seg: client.get_topic(seg, "topic"),
        lambda client, seg: client.get_topic("general", seg),
        lambda client, seg: client.update_topic(seg, "topic", ChatTopicUpdate(title="Topic")),
        lambda client, seg: client.update_topic("general", seg, ChatTopicUpdate(title="Topic")),
        lambda client, seg: client.delete_topic(seg, "topic"),
        lambda client, seg: client.delete_topic("general", seg),
        lambda client, seg: client.get_conversation(seg),
        lambda client, seg: _consume_async_iter(client.list_messages(seg)),
        lambda client, seg: client.update_message(
            seg, "m1", ChatMessageUpdate(content=MessageContent(text="Updated"))
        ),
        lambda client, seg: client.update_message(
            "c.general.default", seg, ChatMessageUpdate(content=MessageContent(text="Updated"))
        ),

        lambda client, seg: client.delete_message(seg, "m1"),
        lambda client, seg: client.delete_message("c.general.default", seg),
        lambda client, seg: client.create_or_replace_user(
            seg, HumanChatUserCreateOrReplace(nickname="Alice", role_name="user.normal")
        ),
        lambda client, seg: client.get_user(seg),
        lambda client, seg: client.delete_user(seg),
        lambda client, seg: _consume_async_iter(client.list_rooms_for_user(seg)),
    ],
)
async def test_async_operations_reject_dot_path_segments_before_sending(dot_segment, invoke):
    async with WebPubSubChatServiceClient(ENDPOINT, HUB, AzureKeyCredential(ACCESS_KEY)) as client:
        with patch.object(client._client._pipeline._transport, "send", new_callable=AsyncMock) as send:
            with pytest.raises(ValueError, match="must not be '\\.' or '\\.\\.'"):
                await invoke(client, dot_segment)
            send.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "valid_segment",
    ["...", "alice.smith", "c.room.default", "room.reader", ".leading", "trailing.", "part%2ename", "%2e%2e%2e"],
)
async def test_async_operations_allow_valid_segments_containing_dots(valid_segment):
    def capture(_pipeline_request):
        raise RequestCaptured()

    async with WebPubSubChatServiceClient(ENDPOINT, HUB, AzureKeyCredential(ACCESS_KEY)) as client:
        with pytest.raises(RequestCaptured):
            await client.get_user(valid_segment, raw_request_hook=capture)


@pytest.mark.asyncio
async def test_async_custom_per_call_policies_and_send_request_path_validation():
    called = []

    class CustomPolicy(SansIOHTTPPolicy):
        def on_request(self, request):
            called.append(request.http_request.url)

    async with WebPubSubChatServiceClient(
        ENDPOINT, HUB, AzureKeyCredential(ACCESS_KEY), per_call_policies=[CustomPolicy()]
    ) as client:
        with patch.object(client._client._pipeline._transport, "send", new_callable=AsyncMock) as send:
            with pytest.raises(ValueError, match="must not be '\\.' or '\\.\\.'"):
                await client.send_request(HttpRequest("GET", "/chat/api/hubs/chat/users/%2e%2e"))
            send.assert_not_awaited()

        def capture(_pipeline_request):
            raise RequestCaptured()

        with pytest.raises(RequestCaptured):
            await client.get_user("alice", raw_request_hook=capture)
        assert len(called) == 1

