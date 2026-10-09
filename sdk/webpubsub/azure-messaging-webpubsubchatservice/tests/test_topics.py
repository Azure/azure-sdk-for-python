# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import datetime
import json
from unittest.mock import AsyncMock, Mock, patch
from urllib.parse import parse_qs, urlparse

import pytest
from azure.core import MatchConditions
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceModifiedError

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient
from azure.messaging.webpubsubchatservice.aio import WebPubSubChatServiceClient as AsyncClient
from azure.messaging.webpubsubchatservice.models import (
    ChatRoom,
    ChatTopic,
    ChatTopicState,
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
    ("list_rooms", (), "rooms", ChatRoom, {"title": "Room", "defaultConversation": "c.room.default"}),
    ("list_users", (), "users", HumanChatUser, {"kind": "Human", "nickname": "User", "roleName": "user.member"}),
    ("list_topics", ("room",), "rooms/room/topics", ChatTopic, TOPIC),
    ("list_rooms_for_user", ("user",), "users/user/rooms", ChatUserRoom, {"title": "Room"}),
]


def _response(payload, status=200):
    response = Mock(status_code=status, headers={"content-type": "application/json"}, reason="Test response")
    response.json.return_value = payload
    response.text.return_value = json.dumps(payload)
    return Mock(http_response=response)


def _paging_responses(path, fields):
    next_link = f"{ENDPOINT}/api/hubs/chat/chat/{path}?api-version=2026-08-01-preview&continuationToken=next"
    return [
        _response({"value": [{**fields, "id": "first"}], "nextLink": next_link}),
        _response({"value": [{**fields, "id": "second"}]}),
    ]


def _assert_page_requests(run, path):
    first, second = [call.args[0] for call in run.call_args_list]
    assert first.method == second.method == "GET"
    assert urlparse(first.url).path == f"/api/hubs/chat/chat/{path}"
    assert parse_qs(urlparse(first.url).query)["maxpagesize"] == ["1"]
    assert parse_qs(urlparse(first.url).query)["api-version"] == ["2026-08-01-preview"]
    assert parse_qs(urlparse(second.url).query)["continuationToken"] == ["next"]
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


@pytest.mark.parametrize("operation,args,path,model,fields", COLLECTIONS)
def test_collection_paging_and_continuation(operation, args, path, model, fields):
    with WebPubSubChatServiceClient(ENDPOINT, "chat", AzureKeyCredential("test-key")) as client:
        with patch.object(client._client._pipeline, "run", side_effect=_paging_responses(path, fields)) as run:
            options = {"params": {"maxpagesize": 1}} if operation == "list_rooms_for_user" else {"max_page_size": 1}
            pages = getattr(client, operation)(*args, **options).by_page()
            first = list(next(pages))
            assert len(first) == 1
            assert isinstance(first[0], model)
            assert pages.continuation_token
            resumed = getattr(client, operation)(*args, **options).by_page(pages.continuation_token)
            second = list(next(resumed))
            assert [item.id for item in first + second] == ["first", "second"]
            assert list(resumed) == []
            _assert_page_requests(run, path)


@pytest.mark.asyncio
@pytest.mark.parametrize("operation,args,path,model,fields", COLLECTIONS)
async def test_async_collection_paging_and_continuation(operation, args, path, model, fields):
    async with AsyncClient(ENDPOINT, "chat", AzureKeyCredential("test-key")) as client:
        with patch.object(
            client._client._pipeline, "run", new_callable=AsyncMock, side_effect=_paging_responses(path, fields)
        ) as run:
            options = {"params": {"maxpagesize": 1}} if operation == "list_rooms_for_user" else {"max_page_size": 1}
            pages = getattr(client, operation)(*args, **options).by_page()
            first = [item async for item in await anext(pages)]
            assert len(first) == 1
            assert isinstance(first[0], model)
            assert pages.continuation_token
            resumed = getattr(client, operation)(*args, **options).by_page(pages.continuation_token)
            second = [item async for item in await anext(resumed)]
            assert [item.id for item in first + second] == ["first", "second"]
            assert [page async for page in resumed] == []
            _assert_page_requests(run, path)


def test_topic_serialization_lifecycle_and_etag():
    archived = {**TOPIC, "state": "Archived", "etag": '"second"'}
    with WebPubSubChatServiceClient(ENDPOINT, "chat", AzureKeyCredential("test-key")) as client:
        with patch.object(
            client._client._pipeline,
            "run",
            side_effect=[_response(TOPIC, 201), _response(TOPIC), _response(archived), _response({}, 204)],
        ) as run:
            topic = client.create_or_replace_topic(
                "room", "topic", ChatTopic({"title": TOPIC["title"], "id": TOPIC["id"], "etag": TOPIC["etag"]})
            )
            assert topic.created_at == datetime.datetime(2026, 8, 1, tzinfo=datetime.timezone.utc)
            fetched = client.get_topic("room", "topic")
            assert fetched.state == ChatTopicState.NORMAL
            updated = client.update_topic(
                "room",
                "topic",
                ChatTopic(title=topic.title, state=ChatTopicState.ARCHIVED),
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
                "room", "topic", ChatTopic({"title": TOPIC["title"], "id": TOPIC["id"], "etag": TOPIC["etag"]})
            )
            assert topic.created_at == datetime.datetime(2026, 8, 1, tzinfo=datetime.timezone.utc)
            fetched = await client.get_topic("room", "topic")
            assert fetched.state == ChatTopicState.NORMAL
            updated = await client.update_topic(
                "room",
                "topic",
                ChatTopic(title=topic.title, state=ChatTopicState.ARCHIVED),
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
                    ChatTopic(title="Title", state=ChatTopicState.ARCHIVED),
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
                    ChatTopic(title="Title", state=ChatTopicState.ARCHIVED),
                    etag='"stale"',
                    match_condition=MatchConditions.IfNotModified,
                )
            assert error.value.status_code == 412


def test_topic_unknown_state_remains_extensible():
    assert ChatTopic({**TOPIC, "state": "FutureState"}).state == "FutureState"
