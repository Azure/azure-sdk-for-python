# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import time
from unittest.mock import Mock
from urllib.parse import urlparse

import jwt
import pytest
from azure.core.credentials import AccessToken, AzureKeyCredential

from azure.messaging.webpubsubservice.chat import (
    ChatRoles,
    RoomPermissions,
    UserPermissions,
    WebPubSubChatServiceClient,
)


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


def test_connection_string_parses_endpoint_access_key_and_port():
    client = WebPubSubChatServiceClient.from_connection_string(
        f"Endpoint={ENDPOINT};AccessKey={ACCESS_KEY};Port=8443;Version=1.0;",
        HUB,
    )
    try:
        assert client._config.endpoint == f"{ENDPOINT}:8443"
        assert client._config.credential.key == ACCESS_KEY
        assert client._web_pub_sub_service_client._config.endpoint == f"{ENDPOINT}:8443"
    finally:
        client.close()


def test_key_credential_request_uses_full_uri_audience_and_sixty_second_token():
    client = WebPubSubChatServiceClient(ENDPOINT, HUB, AzureKeyCredential(ACCESS_KEY))
    try:
        request = _capture_list_roles_request(client)
        token = request.headers["Authorization"].removeprefix("Bearer ")
        claims = jwt.decode(token, ACCESS_KEY, algorithms=["HS256"], audience=request.url)

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
        jwt.decode(first_token, ACCESS_KEY, algorithms=["HS256"], audience=first_request.url)
        jwt.decode(second_token, updated_key, algorithms=["HS256"], audience=second_request.url)
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
        claims = jwt.decode(token, ACCESS_KEY, algorithms=["HS256"], audience=original_url)

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


def test_client_access_token_delegates_fixed_chat_requirements():
    client = WebPubSubChatServiceClient(ENDPOINT, HUB, AzureKeyCredential(ACCESS_KEY))
    expected = {"baseUrl": "wss://example", "token": "token", "url": "wss://example?access_token=token"}
    client._web_pub_sub_service_client.get_client_access_token = Mock(return_value=expected)
    try:
        result = client.get_client_access_token(user_id="alice")
        assert result is expected
        client._web_pub_sub_service_client.get_client_access_token.assert_called_once_with(
            user_id="alice",
            roles=CHAT_ROLES,
            minutes_to_expire=60,
            groups=[],
            client_protocol="Default",
        )
    finally:
        client.close()


def test_entra_client_access_delegation_propagates_reverse_proxy():
    credential = FakeTokenCredential()
    proxy_endpoint = "https://proxy.contoso.com"
    client = WebPubSubChatServiceClient(
        ENDPOINT,
        HUB,
        credential,
        reverse_proxy_endpoint=proxy_endpoint,
    )
    expected = {"baseUrl": "wss://example", "token": "token", "url": "wss://example?access_token=token"}
    client._web_pub_sub_service_client.get_client_access_token = Mock(return_value=expected)
    try:
        inner = client._web_pub_sub_service_client
        assert inner._config.credential is credential
        assert inner._config.proxy_policy._endpoint == ENDPOINT
        assert inner._config.proxy_policy._reverse_proxy_endpoint == proxy_endpoint
        assert client.get_client_access_token(user_id="alice") is expected
        inner.get_client_access_token.assert_called_once_with(
            user_id="alice",
            roles=CHAT_ROLES,
            minutes_to_expire=60,
            groups=[],
            client_protocol="Default",
        )
    finally:
        client.close()


def test_key_client_access_token_returns_wss_url_and_required_roles():
    client = WebPubSubChatServiceClient(ENDPOINT, HUB, AzureKeyCredential(ACCESS_KEY))
    try:
        result = client.get_client_access_token(user_id="alice")
        claims = jwt.decode(
            result["token"],
            ACCESS_KEY,
            algorithms=["HS256"],
            audience=result["baseUrl"].replace("wss://", "https://"),
        )

        assert result["baseUrl"].startswith("wss://")
        assert result["url"] == f'{result["baseUrl"]}?access_token={result["token"]}'
        assert claims["sub"] == "alice"
        assert claims["role"] == CHAT_ROLES
        assert "webpubsub.group" not in claims
        assert 3595 <= claims["exp"] - claims["iat"] <= 3605
    finally:
        client.close()


def test_role_and_permission_constants():
    assert ChatRoles.USER_NORMAL == "user.normal"
    assert ChatRoles.ROOM_MEMBER == "room.member"
    assert ChatRoles.ROOM_OPERATOR == "room.operator"
    assert UserPermissions.CREATE_ROOM == "user.create_room"
    assert UserPermissions.FETCH_ALL_ROOMS == "user.fetch_all_rooms"
    assert RoomPermissions.INVITE_USER == "room.invite"
    assert RoomPermissions.REMOVE_USER == "room.remove_user"
    assert RoomPermissions.READ_HISTORY == "room.history"
    assert RoomPermissions.PUBLISH_MESSAGE == "room.publish_message"
