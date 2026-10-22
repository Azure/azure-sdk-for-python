# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
# cspell:ignore kwonlyargs
import ast
import inspect
import json
from typing import get_args
from unittest.mock import AsyncMock, Mock, patch

import pytest
from azure.core import MatchConditions
from azure.core.credentials import AzureKeyCredential

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient
from azure.messaging.webpubsubchatservice.aio import WebPubSubChatServiceClient as AsyncClient
from azure.messaging.webpubsubchatservice import models, types

REQUEST_PROJECTIONS = [
    (models.ChatTopicCreateOrReplace, models.ChatTopic, {"create", "update"}),
    (models.ChatTopicUpdate, models.ChatTopic, {"update"}),
    (models.ChatMessageUpdate, models.ChatMessage, {"update"}),
    (models.ChatRoleCreateOrReplace, models.ChatRole, {"create", "update"}),
    (models.ChatRoomCreateOrReplace, models.ChatRoom, {"create", "update"}),
    (models.ChatRoomMemberCreateOrReplace, models.ChatRoomMember, {"create", "update"}),
    (models.ChatUserCreateOrReplace, models.ChatUser, {"create", "update"}),
    (models.HumanChatUserCreateOrReplace, models.HumanChatUser, {"create", "update"}),
]

CASES = [
    (
        "create_or_replace_topic",
        ("room", "topic"),
        models.ChatTopicCreateOrReplace(title="Title"),
        models.ChatTopic,
        {"title": "Title"},
    ),
    (
        "create_or_replace_topic",
        ("room", "topic"),
        types.ChatTopicCreateOrReplace(title="Title"),
        models.ChatTopic,
        {"title": "Title"},
    ),
    (
        "create_or_replace_topic",
        ("room", "topic"),
        models.ChatTopicCreateOrReplace(title="Title", state=models.ChatTopicState.ARCHIVED),
        models.ChatTopic,
        {"title": "Title", "state": "Archived"},
    ),
    (
        "create_or_replace_topic",
        ("room", "topic"),
        types.ChatTopicCreateOrReplace(title="Title", state=models.ChatTopicState.ARCHIVED),
        models.ChatTopic,
        {"title": "Title", "state": "Archived"},
    ),
    (
        "update_topic",
        ("room", "topic"),
        models.ChatTopicUpdate(state=models.ChatTopicState.ARCHIVED),
        models.ChatTopic,
        {"state": "Archived"},
    ),
    (
        "update_topic",
        ("room", "topic"),
        models.ChatTopicUpdate(title="New title"),
        models.ChatTopic,
        {"title": "New title"},
    ),
    (
        "update_message",
        ("conversation", "message"),
        models.ChatMessageUpdate(created_by="Updated creator"),
        models.ChatMessage,
        {"createdBy": "Updated creator"},
    ),
    (
        "update_topic",
        ("room", "topic"),
        types.ChatTopicUpdate(title="New title"),
        models.ChatTopic,
        {"title": "New title"},
    ),
    (
        "update_topic",
        ("room", "topic"),
        types.ChatTopicUpdate(state=models.ChatTopicState.ARCHIVED),
        models.ChatTopic,
        {"state": "Archived"},
    ),
    (
        "update_message",
        ("conversation", "message"),
        types.ChatMessageUpdate(createdBy="Updated creator"),
        models.ChatMessage,
        {"createdBy": "Updated creator"},
    ),
    (
        "update_message",
        ("conversation", "message"),
        types.ChatMessageUpdate(content={"text": "Updated"}),
        models.ChatMessage,
        {"content": {"text": "Updated"}},
    ),
    (
        "update_message",
        ("conversation", "message"),
        models.ChatMessageUpdate(content=models.MessageContent(text="Updated")),
        models.ChatMessage,
        {"content": {"text": "Updated"}},
    ),
    (
        "update_message",
        ("conversation", "message"),
        models.ChatMessageUpdate(content=models.MessageContent(binary=b"\x00\xff")),
        models.ChatMessage,
        {"content": {"binary": "AP8="}},
    ),
    (
        "create_or_replace_role",
        ("user.role",),
        models.ChatRoleCreateOrReplace(permissions=[models.ChatPermission.USER_CREATE_ROOM]),
        models.ChatRole,
        {"permissions": ["user.create_room"]},
    ),
    (
        "create_or_replace_room",
        ("room",),
        models.ChatRoomCreateOrReplace(title="Room"),
        models.ChatRoom,
        {"title": "Room"},
    ),
    (
        "create_or_replace_room_member",
        ("room", "user"),
        models.ChatRoomMemberCreateOrReplace(role_name="room.member"),
        models.ChatRoomMember,
        {"roleName": "room.member"},
    ),
    (
        "create_or_replace_user",
        ("user",),
        models.HumanChatUserCreateOrReplace(nickname="User", role_name="user.member"),
        models.HumanChatUser,
        {"kind": "Human", "nickname": "User", "roleName": "user.member"},
    ),
]


def _required_constructor_fields(model):
    definition = ast.parse(inspect.getsource(model)).body[0]
    constructor = next(
        node for node in definition.body if isinstance(node, ast.FunctionDef) and node.name == "__init__"
    )
    return {
        parameter.arg
        for parameter, default in zip(constructor.args.kwonlyargs, constructor.args.kw_defaults)
        if default is None
    }


@pytest.mark.parametrize("request_model,resource_model,lifecycle", REQUEST_PROJECTIONS)
def test_request_fields_follow_resource_lifecycle_visibility(request_model, resource_model, lifecycle):
    resource_fields = resource_model({})._attr_to_rest_field
    request_fields = request_model({})._attr_to_rest_field
    writable_fields = {name for name, field in resource_fields.items() if lifecycle.intersection(field._visibility)}
    assert set(request_fields) == writable_fields
    for name, field in request_fields.items():
        assert field._rest_name == resource_fields[name]._rest_name
        assert lifecycle.intersection(field._visibility)

    required = _required_constructor_fields(resource_model)
    if lifecycle == {"update"}:
        required = set()
    else:
        required = {name for name in required & writable_fields if "create" in resource_fields[name]._visibility}
    assert _required_constructor_fields(request_model) == required
    dictionary_projection = getattr(types, request_model.__name__)
    # Discriminated dictionary requests are unions of their concrete subtypes.
    for dictionary_type in get_args(dictionary_projection) or (dictionary_projection,):
        concrete_request = getattr(models, dictionary_type.__name__)
        concrete_fields = concrete_request({})._attr_to_rest_field
        assert set(dictionary_type.__annotations__) == {field._rest_name for field in concrete_fields.values()}
        required_dictionary_fields = _required_constructor_fields(concrete_request) | {
            name for name, field in concrete_fields.items() if field._is_discriminator
        }
        assert dictionary_type.__required_keys__ == {
            concrete_fields[name]._rest_name for name in required_dictionary_fields
        }


def _response(body):
    payload = {
        **body,
        "id": "returned-id",
        "etag": '"new"',
        "createdAt": "2026-08-01T00:00:00Z",
        "createdBy": "user",
        "conversationId": "conversation",
        "defaultConversation": "conversation",
    }
    response = Mock(status_code=200, headers={"content-type": "application/json"}, reason="OK")
    response.json.return_value = payload
    response.text.return_value = json.dumps(payload)
    return Mock(http_response=response)


def _assert_request(run, method, body):
    request = run.call_args.args[0]
    assert json.loads(request.content) == body
    assert request.method == ("PATCH" if method.startswith("update_") else "PUT")
    assert request.headers["If-Match"] == '"old"'
    if method.startswith("update_"):
        assert request.headers["Content-Type"] == "application/merge-patch+json"


@pytest.mark.parametrize("method,args,resource,response_model,body", CASES)
def test_lifecycle_request_and_resource_response(method, args, resource, response_model, body):
    with WebPubSubChatServiceClient(
        "https://example.webpubsub.azure.com", "chat", AzureKeyCredential("test-key")
    ) as client:
        with patch.object(client._client._pipeline, "run", return_value=_response(body)) as run:
            result = getattr(client, method)(
                *args, resource, etag='"old"', match_condition=MatchConditions.IfNotModified
            )
    assert isinstance(result, response_model)
    assert result.etag == '"new"'
    _assert_request(run, method, body)


@pytest.mark.asyncio
@pytest.mark.parametrize("method,args,resource,response_model,body", CASES)
async def test_async_lifecycle_request_and_resource_response(method, args, resource, response_model, body):
    async with AsyncClient("https://example.webpubsub.azure.com", "chat", AzureKeyCredential("test-key")) as client:
        with patch.object(client._client._pipeline, "run", new_callable=AsyncMock, return_value=_response(body)) as run:
            result = await getattr(client, method)(
                *args, resource, etag='"old"', match_condition=MatchConditions.IfNotModified
            )
    assert isinstance(result, response_model)
    assert result.etag == '"new"'
    _assert_request(run, method, body)
