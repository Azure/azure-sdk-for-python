# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from testcase import WebPubSubChatPreparer, WebPubSubChatTest

from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError
from azure.messaging.webpubsubchatservice.models import (
    ChatPermission,
    ChatRoleCreate,
    ChatRoomCreate,
    ChatRoomMemberCreate,
    ChatTopicCreateOrReplace,
    ChatTopicUpdate,
    ChatTopicState,
    HumanChatUser,
    HumanChatUserCreate,
)


async def _collect(paged):
    return [item async for item in paged]


async def _assert_resumable_pages(paged):
    pages = paged.by_page()
    first = await _collect(await anext(pages))
    assert len(first) == 1
    assert pages.continuation_token
    resumed = paged.by_page(pages.continuation_token)
    second = await _collect(await anext(resumed))
    assert len(second) == 1
    assert first[0].id != second[0].id


class TestWebPubSubChatTopicsLiveAsync(WebPubSubChatTest):
    @WebPubSubChatPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_async_topic_lifecycle_and_paging(self, wps_chat_endpoint):
        client = self.create_async_client(wps_chat_endpoint)
        room_id = "python-async-e2e-topics"
        try:
            room = await client.create_or_replace_room(room_id, ChatRoomCreate(title="Async Topic E2E"))
            assert all(
                topic.conversation_id == room.default_conversation
                for topic in await _collect(client.list_topics(room_id))
            )
            for topic_id in ("first", "second"):
                topic = await client.create_or_replace_topic(
                    room_id, topic_id, ChatTopicCreateOrReplace(title=topic_id)
                )
                assert topic.id == topic_id
                assert topic.title == topic_id
                assert topic.state == ChatTopicState.NORMAL
                assert topic.created_at
                assert topic.created_by
                assert topic.etag
                conversation = await client.get_conversation(topic.conversation_id)
                assert conversation.id == topic.conversation_id
                assert conversation.parent_room == room_id
                assert await _collect(client.list_messages(topic.conversation_id)) == []

            assert {topic.id async for topic in client.list_topics(room_id, max_page_size=1)}.issuperset(
                {"first", "second"}
            )
            await _assert_resumable_pages(client.list_topics(room_id, max_page_size=1))
            fetched = await client.get_topic(room_id, "first")
            archived = await client.update_topic(
                room_id,
                "first",
                ChatTopicUpdate(title="Archived topic", state=ChatTopicState.ARCHIVED),
                etag=fetched.etag,
                match_condition=MatchConditions.IfNotModified,
            )
            assert archived.title == "Archived topic"
            assert archived.state == ChatTopicState.ARCHIVED
            assert archived.conversation_id == fetched.conversation_id
            assert archived.etag != fetched.etag
            assert (await client.get_topic(room_id, "first")).state == ChatTopicState.ARCHIVED
            with pytest.raises(HttpResponseError) as error:
                await client.update_topic(
                    room_id,
                    "first",
                    ChatTopicUpdate(title="Stale update", state=ChatTopicState.NORMAL),
                    etag=fetched.etag,
                    match_condition=MatchConditions.IfNotModified,
                )
            assert error.value.status_code == 412
            await client.delete_topic(
                room_id, "first", etag=archived.etag, match_condition=MatchConditions.IfNotModified
            )
        finally:
            await self.cleanup_async(client.delete_room, room_id)
            await client.close()

    @WebPubSubChatPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_async_room_user_and_user_room_collections(self, wps_chat_endpoint):
        client = self.create_async_client(wps_chat_endpoint)
        room_ids = ["python-async-e2e-collection-1", "python-async-e2e-collection-2"]
        user_ids = ["python-async-e2e-collection-user-1", "python-async-e2e-collection-user-2"]
        user_role = "user.python_async_e2e_collections"
        room_role = "room.python_async_e2e_collections"
        try:
            await client.create_or_replace_role(
                user_role, ChatRoleCreate(permissions=[ChatPermission.USER_CREATE_ROOM])
            )
            await client.create_or_replace_role(
                room_role, ChatRoleCreate(permissions=[ChatPermission.ROOM_PUBLISH_MESSAGE])
            )
            for user_id in user_ids:
                await client.create_or_replace_user(user_id, HumanChatUserCreate(nickname=user_id, role_name=user_role))
            assert await _collect(client.list_rooms_for_user(user_ids[0])) == []
            for room_id in room_ids:
                await client.create_or_replace_room(room_id, ChatRoomCreate(title=room_id))
                await client.create_or_replace_room_member(
                    room_id, user_ids[0], ChatRoomMemberCreate(role_name=room_role)
                )
            assert {room.id async for room in client.list_rooms(max_page_size=1)}.issuperset(room_ids)
            users = await _collect(client.list_users(max_page_size=1))
            assert {user.id for user in users}.issuperset(user_ids)
            assert all(isinstance(user, HumanChatUser) for user in users if user.id in user_ids)
            assert {room.id async for room in client.list_rooms_for_user(user_ids[0])} == set(room_ids)
            await _assert_resumable_pages(client.list_rooms(max_page_size=1))
            await _assert_resumable_pages(client.list_users(max_page_size=1))
            await _assert_resumable_pages(client.list_rooms_for_user(user_ids[0], max_page_size=1))
            await client.delete_room_member(room_ids[0], user_ids[0])
            assert {room.id async for room in client.list_rooms_for_user(user_ids[0])} == {room_ids[1]}
        finally:
            for room_id in room_ids:
                await self.cleanup_async(client.delete_room, room_id)
            for user_id in user_ids:
                await self.cleanup_async(client.delete_user, user_id)
            await self.cleanup_async(client.delete_role, user_role)
            await self.cleanup_async(client.delete_role, room_role)
            await client.close()
