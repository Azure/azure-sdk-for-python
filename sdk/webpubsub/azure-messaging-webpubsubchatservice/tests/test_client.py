# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import time
from unittest.mock import Mock, patch
from urllib.parse import urlparse

import jwt
import pytest
from azure.core.credentials import AccessToken, AzureKeyCredential

from azure.messaging.webpubsubservice.chat import (
    BuiltInChatRoles,
    WebPubSubChatServiceClient,
)
from azure.messaging.webpubsubservice.chat.models import ChatPermission

ACCESS_KEY = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ABCDEFGH"
ENDPOINT = "https://example.webpubsub.azure.com"
HUB = "chat"
CHAT_ROLES = ["webpubsub.getGroupState", "webpubsub.setGroupState"]


class RequestCaptured(Exception):
    pass


class FakeTokenCredential:
    def get_token(self, *scopes, **kwargs):
        return AccessToken("entra-token", int(time.time()) + 3600)


def _capture_list_roles_request(client):
    captured = {}

    def capture(pipeline_request):
        captured["request"] = pipeline_request.http_request
        raise RequestCaptured()

    with pytest.raises(RequestCaptured):
        list(client.list_roles(raw_request_hook=capture))
    return captured["request"]


@pytest.mark.parametrize(
    "endpoint,hub,credential",
    [
        (None, HUB, AzureKeyCredential(ACCESS_KEY)),
        ("", HUB, AzureKeyCredential(ACCESS_KEY)),
        (ENDPOINT, None, AzureKeyCredential(ACCESS_KEY)),
        (ENDPOINT, "", AzureKeyCredential(ACCESS_KEY)),
        (ENDPOINT, HUB, None),
    ],
)
def test_constructor_validation(endpoint, hub, credential):
    with pytest.raises(ValueError):
        WebPubSubChatServiceClient(endpoint=endpoint, hub=hub, credential=credential)


@pytest.mark.parametrize("connection_string", [None, ""])
def test_connection_string_validation(connection_string):
    with pytest.raises(ValueError):
        WebPubSubChatServiceClient.from_connection_string(connection_string, HUB)


def test_malformed_connection_string_does_not_expose_input():
    connection_string = (
        f"Endpoint={ENDPOINT};AccessKey={ACCESS_KEY};malformed-secret-segment"
    )

    with pytest.raises(ValueError) as error:
        WebPubSubChatServiceClient.from_connection_string(connection_string, HUB)

    assert str(error.value) == "Malformed connection string - expected 'key=value'"
    assert ACCESS_KEY not in str(error.value)
    assert "malformed-secret-segment" not in str(error.value)


def test_connection_string_parses_endpoint_access_key_and_port():
    client = WebPubSubChatServiceClient.from_connection_string(
        f"Endpoint={ENDPOINT};AccessKey={ACCESS_KEY};Port=8443;Version=1.0;",
        HUB,
    )
    try:
        assert client._config.endpoint == f"{ENDPOINT}:8443"
        assert client._config.credential.key == ACCESS_KEY
    finally:
        client.close()


def test_key_credential_request_uses_full_uri_audience_and_sixty_second_token():
    client = WebPubSubChatServiceClient(ENDPOINT, HUB, AzureKeyCredential(ACCESS_KEY))
    try:
        request = _capture_list_roles_request(client)
        token = request.headers["Authorization"].removeprefix("Bearer ")
        claims = jwt.decode(
            token, ACCESS_KEY, algorithms=["HS256"], audience=request.url
        )

        assert claims["aud"] == request.url
        assert "api-version=2026-02-01-preview" in request.url
        assert 0 < claims["exp"] - int(time.time()) <= 60
    finally:
        client.close()


def test_updating_key_credential_changes_subsequent_request_tokens():
    credential = AzureKeyCredential(ACCESS_KEY)
    client = WebPubSubChatServiceClient(ENDPOINT, HUB, credential)
    try:
        first_request = _capture_list_roles_request(client)
        first_token = first_request.headers["Authorization"].removeprefix("Bearer ")

        updated_key = "updated-key-updated-key-updated-key-updated-key"
        credential.update(updated_key)
        second_request = _capture_list_roles_request(client)
        second_token = second_request.headers["Authorization"].removeprefix("Bearer ")

        assert first_token != second_token
        jwt.decode(
            first_token, ACCESS_KEY, algorithms=["HS256"], audience=first_request.url
        )
        jwt.decode(
            second_token, updated_key, algorithms=["HS256"], audience=second_request.url
        )
    finally:
        client.close()


def test_reverse_proxy_preserves_path_query_and_original_key_audience():
    proxy_endpoint = "https://proxy.contoso.com"
    client = WebPubSubChatServiceClient(
        ENDPOINT,
        HUB,
        AzureKeyCredential(ACCESS_KEY),
        reverse_proxy_endpoint=proxy_endpoint,
    )
    try:
        request = _capture_list_roles_request(client)
        token = request.headers["Authorization"].removeprefix("Bearer ")
        original_url = request.url.replace(proxy_endpoint, ENDPOINT, 1)
        claims = jwt.decode(
            token, ACCESS_KEY, algorithms=["HS256"], audience=original_url
        )

        assert urlparse(request.url).netloc == "proxy.contoso.com"
        assert urlparse(request.url).path == urlparse(original_url).path
        assert urlparse(request.url).query == urlparse(original_url).query
        assert claims["aud"] == original_url
    finally:
        client.close()


def test_reverse_proxy_with_entra_credential_keeps_bearer_token():
    client = WebPubSubChatServiceClient(
        ENDPOINT,
        HUB,
        FakeTokenCredential(),
        reverse_proxy_endpoint="https://proxy.contoso.com",
    )
    try:
        request = _capture_list_roles_request(client)
        assert urlparse(request.url).netloc == "proxy.contoso.com"
        assert request.headers["Authorization"] == "Bearer entra-token"
    finally:
        client.close()


def test_token_credential_client_access_token_uses_generated_operation():
    client = WebPubSubChatServiceClient(ENDPOINT, HUB, FakeTokenCredential())
    try:
        with patch.object(
            client, "_generate_client_token", return_value=Mock(token="token")
        ) as generate:
            result = client.get_client_access_token(user_id="alice")

        base_url = f"wss://example.webpubsub.azure.com/client/hubs/{HUB}"
        assert result == {
            "baseUrl": base_url,
            "token": "token",
            "url": f"{base_url}?access_token=token",
        }
        generate.assert_called_once_with(
            user_id="alice", role=CHAT_ROLES, minutes_to_expire=60
        )
    finally:
        client.close()


def test_key_client_access_token_is_generated_locally():
    client = WebPubSubChatServiceClient(ENDPOINT, HUB, AzureKeyCredential(ACCESS_KEY))
    try:
        with patch.object(client, "_generate_client_token") as generate:
            result = client.get_client_access_token(user_id="alice")

        generate.assert_not_called()
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
        client.close()


@pytest.mark.parametrize("minutes_to_expire", [0, -1])
def test_key_client_access_token_rejects_invalid_expiration(minutes_to_expire):
    client = WebPubSubChatServiceClient(ENDPOINT, HUB, AzureKeyCredential(ACCESS_KEY))
    try:
        with pytest.raises(ValueError, match="minutes_to_expire must be at least 1"):
            client.get_client_access_token(minutes_to_expire=minutes_to_expire)
    finally:
        client.close()


def test_builtin_roles_and_generated_permissions():
    assert BuiltInChatRoles.USER_NORMAL == "user.normal"
    assert BuiltInChatRoles.ROOM_MEMBER == "room.member"
    assert BuiltInChatRoles.ROOM_OPERATOR == "room.operator"
    assert ChatPermission.USER_CREATE_ROOM == "user.create_room"
    assert ChatPermission.USER_FETCH_ALL_ROOMS == "user.fetch_all_rooms"
    assert ChatPermission.ROOM_INVITE == "room.invite"
    assert ChatPermission.ROOM_REMOVE_USER == "room.remove_user"
    assert ChatPermission.ROOM_HISTORY == "room.history"
    assert ChatPermission.ROOM_PUBLISH_MESSAGE == "room.publish_message"
