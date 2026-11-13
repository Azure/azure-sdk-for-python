# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import datetime
import inspect
import json
from unittest.mock import AsyncMock, Mock, patch
from urllib.parse import parse_qs, urlencode, urlparse

import pytest
from azure.core import MatchConditions
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceModifiedError

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient
from azure.messaging.webpubsubchatservice.aio import WebPubSubChatServiceClient as AsyncClient
from azure.messaging.webpubsubchatservice.models import (
    ChatMessage,
    ChatRole,
    ChatRoom,
    ChatRoomMember,
    ChatTopic,
    ChatTopicCreateOrReplace,
    ChatTopicState,
    ChatTopicUpdate,
    ChatUserRoom,
    HumanChatUser,
)

ENDPOINT = "https://example.webpubsub.azure.com"
TOPIC = {
    "id": "topic",
    "title": "Announcements",
    "createdAt": "2026-08-01T00:00:00Z",
    "createdBy": "user",
    "state": "Normal",
    "conversationId": "c.room.topic",
    "etag": '"first"',
}
COLLECTIONS = [
    (
        "list_messages",
        ("conversation",),
        "conversations/conversation/messages",
        ChatMessage,
        {"createdBy": "user", "content": {}, "createdAt": "2026-08-01T00:00:00Z", "etag": '"message"'},
        "id",
    ),
    ("list_roles", (), "roles", ChatRole, {"permissions": [], "etag": '"role"'}, "name"),
    (
        "list_room_members",
        ("room",),
        "rooms/room/members",
        ChatRoomMember,
        {"roleName": "room.member", "etag": '"member"'},
        "userId",
    ),
    ("list_rooms", (), "rooms", ChatRoom, {"title": "Room", "defaultConversation": "c.room.default"}, "id"),
    ("list_users", (), "users", HumanChatUser, {"kind": "Human", "nickname": "User", "roleName": "user.member"}, "id"),
    ("list_topics", ("room",), "rooms/room/topics", ChatTopic, TOPIC, "id"),
    ("list_rooms_for_user", ("user",), "users/user/rooms", ChatUserRoom, {"title": "Room"}, "id"),
]


def _response(payload, status=200):
    response = Mock(status_code=status, headers={"content-type": "application/json"}, reason="Test response")
    response.json.return_value = payload
    response.text.return_value = json.dumps(payload)
    return Mock(http_response=response)


def _paging_responses(path, fields, identity):
    cursor = "first" if path.endswith("/messages") else "next+/=token"
    query = urlencode({"api-version": "2026-08-01-preview", "continuationToken": cursor})
    next_link = f"{ENDPOINT}/api/hubs/chat/chat/{path}?{query}"
    return [
        _response({"value": [{**fields, identity: "first"}], "nextLink": next_link}),
        _response({"value": [{**fields, identity: "second"}]}),
    ]


def _assert_page_requests(run, path):
    first, second = [call.args[0] for call in run.call_args_list]
    assert first.method == second.method == "GET"
    assert urlparse(first.url).path == f"/api/hubs/chat/chat/{path}"
    assert parse_qs(urlparse(first.url).query)["maxpagesize"] == ["1"]
    assert "continuationToken" not in parse_qs(urlparse(first.url).query)
    assert parse_qs(urlparse(first.url).query)["api-version"] == ["2026-08-01-preview"]
    assert urlparse(second.url).path == f"/api/hubs/chat/chat/{path}"
    cursor = "first" if path.endswith("/messages") else "next+/=token"
    assert parse_qs(urlparse(second.url).query)["continuationToken"] == [cursor]
    assert parse_qs(urlparse(second.url).query)["api-version"] == ["2026-08-01-preview"]


def _assert_topic_requests(run):
    create, get, update, delete = [call.args[0] for call in run.call_args_list]
    assert [request.method for request in (create, get, update, delete)] == ["PUT", "GET", "PATCH", "DELETE"]
    assert all(
        urlparse(request.url).path == "/api/hubs/chat/chat/rooms/room/topics/topic"
        for request in (create, get, update, delete)
    )
    assert json.loads(create.content) == {"title": "Announcements"}
    assert json.loads(update.content) == {"title": "Announcements", "state": "Archived"}
    assert update.headers["Content-Type"] == "application/merge-patch+json"
    assert update.headers["If-Match"] == '"first"'
    assert delete.headers["If-Match"] == '"second"'


@pytest.mark.parametrize("client_type", [WebPubSubChatServiceClient, AsyncClient])
def test_listing_api_surface(client_type):
    operations = {name for name in dir(client_type) if name.startswith("list_")}
    assert operations == {collection[0] for collection in COLLECTIONS}
    for name in operations:
        method = getattr(client_type, name)
        assert not any("continuation_token" in parameter for parameter in inspect.signature(method).parameters)
        assert ":keyword continuation_token" not in method.__doc__
        assert ":paramtype continuation_token" not in method.__doc__
    assert "Message IDs are used as pagination cursors." in " ".join(client_type.list_messages.__doc__.split())
    assert "nextLink" in client_type.list_messages.__doc__


@pytest.mark.parametrize("resume", [False, True])
@pytest.mark.parametrize("operation,args,path,model,fields,identity", COLLECTIONS)
def test_collection_paging_and_continuation(operation, args, path, model, fields, identity, resume):
    with WebPubSubChatServiceClient(ENDPOINT, "chat", AzureKeyCredential("test-key")) as client:
        with patch.object(
            client._client._pipeline, "run", side_effect=_paging_responses(path, fields, identity)
        ) as run:
            options = {"max_page_size": 1}
            pages = getattr(client, operation)(*args, **options).by_page()
            first = list(next(pages))
            assert len(first) == 1
            assert isinstance(first[0], model)
            assert pages.continuation_token
            remaining = (
                getattr(client, operation)(*args, **options).by_page(continuation_token=pages.continuation_token)
                if resume
                else pages
            )
            second = list(next(remaining))
            assert isinstance(second[0], model)
            assert [item[identity] for item in first + second] == ["first", "second"]
            assert not list(remaining)
            _assert_page_requests(run, path)


@pytest.mark.asyncio
@pytest.mark.parametrize("resume", [False, True])
@pytest.mark.parametrize("operation,args,path,model,fields,identity", COLLECTIONS)
async def test_async_collection_paging_and_continuation(operation, args, path, model, fields, identity, resume):
    async with AsyncClient(ENDPOINT, "chat", AzureKeyCredential("test-key")) as client:
        with patch.object(
            client._client._pipeline,
            "run",
            new_callable=AsyncMock,
            side_effect=_paging_responses(path, fields, identity),
        ) as run:
            options = {"max_page_size": 1}
            pages = getattr(client, operation)(*args, **options).by_page()
            first = [item async for item in await anext(pages)]
            assert len(first) == 1
            assert isinstance(first[0], model)
            assert pages.continuation_token
            remaining = (
                getattr(client, operation)(*args, **options).by_page(continuation_token=pages.continuation_token)
                if resume
                else pages
            )
            second = [item async for item in await anext(remaining)]
            assert isinstance(second[0], model)
            assert [item[identity] for item in first + second] == ["first", "second"]
            assert [page async for page in remaining] == []
            _assert_page_requests(run, path)


def test_topic_serialization_lifecycle_and_etag():
    archived = {**TOPIC, "state": "Archived", "etag": '"second"'}
    with WebPubSubChatServiceClient(ENDPOINT, "chat", AzureKeyCredential("test-key")) as client:
        with patch.object(
            client._client._pipeline,
            "run",
            side_effect=[_response(TOPIC, 201), _response(TOPIC), _response(archived), _response({}, 204)],
        ) as run:
            topic = client.create_or_replace_topic("room", "topic", ChatTopicCreateOrReplace(title=TOPIC["title"]))
            assert topic.created_at == datetime.datetime(2026, 8, 1, tzinfo=datetime.timezone.utc)
            fetched = client.get_topic("room", "topic")
            assert fetched.state == ChatTopicState.NORMAL
            updated = client.update_topic(
                "room",
                "topic",
                ChatTopicUpdate(title=topic.title, state=ChatTopicState.ARCHIVED),
                etag=fetched.etag,
                match_condition=MatchConditions.IfNotModified,
            )
            assert updated.state == ChatTopicState.ARCHIVED
            assert updated.conversation_id == topic.conversation_id
            assert (
                client.delete_topic("room", "topic", etag=updated.etag, match_condition=MatchConditions.IfNotModified)
                is None
            )
            _assert_topic_requests(run)


@pytest.mark.asyncio
async def test_async_topic_serialization_lifecycle_and_etag():
    archived = {**TOPIC, "state": "Archived", "etag": '"second"'}
    async with AsyncClient(ENDPOINT, "chat", AzureKeyCredential("test-key")) as client:
        with patch.object(
            client._client._pipeline,
            "run",
            new_callable=AsyncMock,
            side_effect=[_response(TOPIC, 201), _response(TOPIC), _response(archived), _response({}, 204)],
        ) as run:
            topic = await client.create_or_replace_topic(
                "room", "topic", ChatTopicCreateOrReplace(title=TOPIC["title"])
            )
            assert topic.created_at == datetime.datetime(2026, 8, 1, tzinfo=datetime.timezone.utc)
            fetched = await client.get_topic("room", "topic")
            assert fetched.state == ChatTopicState.NORMAL
            updated = await client.update_topic(
                "room",
                "topic",
                ChatTopicUpdate(title=topic.title, state=ChatTopicState.ARCHIVED),
                etag=fetched.etag,
                match_condition=MatchConditions.IfNotModified,
            )
            assert updated.state == ChatTopicState.ARCHIVED
            assert updated.conversation_id == topic.conversation_id
            assert (
                await client.delete_topic(
                    "room", "topic", etag=updated.etag, match_condition=MatchConditions.IfNotModified
                )
                is None
            )
            _assert_topic_requests(run)


def test_topic_stale_etag_surfaces_service_error():
    with WebPubSubChatServiceClient(ENDPOINT, "chat", AzureKeyCredential("test-key")) as client:
        with patch.object(
            client._client._pipeline,
            "run",
            return_value=_response({"error": {"code": "PreconditionFailed", "message": "Stale ETag"}}, 412),
        ):
            with pytest.raises(ResourceModifiedError) as error:
                client.update_topic(
                    "room",
                    "topic",
                    ChatTopicUpdate(title="Title", state=ChatTopicState.ARCHIVED),
                    etag='"stale"',
                    match_condition=MatchConditions.IfNotModified,
                )
            assert error.value.status_code == 412


@pytest.mark.asyncio
async def test_async_topic_stale_etag_surfaces_service_error():
    async with AsyncClient(ENDPOINT, "chat", AzureKeyCredential("test-key")) as client:
        with patch.object(
            client._client._pipeline,
            "run",
            new_callable=AsyncMock,
            return_value=_response({"error": {"code": "PreconditionFailed", "message": "Stale ETag"}}, 412),
        ):
            with pytest.raises(ResourceModifiedError) as error:
                await client.update_topic(
                    "room",
                    "topic",
                    ChatTopicUpdate(title="Title", state=ChatTopicState.ARCHIVED),
                    etag='"stale"',
                    match_condition=MatchConditions.IfNotModified,
                )
            assert error.value.status_code == 412


def test_topic_unknown_state_remains_extensible():
    assert ChatTopic({**TOPIC, "state": "FutureState"}).state == "FutureState"
