# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
from devtools_testutils import recorded_by_proxy
import pytest

from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError
from azure.messaging.webpubsubchatservice.models import (
    ChatPermission,
    ChatRole,
    ChatRoom,
    ChatRoomMember,
    ChatTopic,
    ChatTopicState,
    HumanChatUser,
)
from testcase import WebPubSubChatPreparer, WebPubSubChatTest


def _assert_resumable_pages(paged):
    pages = paged.by_page()
    first = list(next(pages))
    assert len(first) == 1
    assert pages.continuation_token
    resumed = paged.by_page(pages.continuation_token)
    second = list(next(resumed))
    assert len(second) == 1
    assert first[0].id != second[0].id


class TestWebPubSubChatTopicsLive(WebPubSubChatTest):
    @WebPubSubChatPreparer()
    @recorded_by_proxy
    def test_topic_lifecycle_and_paging(self, wps_chat_endpoint):
        client = self.create_client(wps_chat_endpoint)
        # Existing operations are not yet routed under the new version on DevINT.
        setup = self.create_client(wps_chat_endpoint, api_version="2026-02-01-preview")
        room_id = "python-e2e-topics"
        try:
            room = setup.create_or_replace_room(room_id, ChatRoom(title="Topic E2E"))
            assert all(topic.conversation_id == room.default_conversation for topic in client.list_topics(room_id))
            for topic_id in ("first", "second"):
                topic = client.create_or_replace_topic(room_id, topic_id, ChatTopic({"title": topic_id}))
                assert topic.id == topic_id
                assert topic.title == topic_id
                assert topic.state == ChatTopicState.NORMAL
                assert topic.created_at
                assert topic.created_by
                assert topic.etag
                conversation = setup.get_conversation(topic.conversation_id)
                assert conversation.id == topic.conversation_id
                assert conversation.parent_room == room_id
                assert list(setup.list_messages(topic.conversation_id)) == []

            assert {topic.id for topic in client.list_topics(room_id, max_page_size=1)}.issuperset({"first", "second"})
            _assert_resumable_pages(client.list_topics(room_id, max_page_size=1))
            fetched = client.get_topic(room_id, "first")
            archived = client.update_topic(
                room_id,
                "first",
                ChatTopic(title="Archived topic", state=ChatTopicState.ARCHIVED),
                etag=fetched.etag,
                match_condition=MatchConditions.IfNotModified,
            )
            assert archived.title == "Archived topic"
            assert archived.state == ChatTopicState.ARCHIVED
            assert archived.conversation_id == fetched.conversation_id
            assert archived.etag != fetched.etag
            assert client.get_topic(room_id, "first").state == ChatTopicState.ARCHIVED
            with pytest.raises(HttpResponseError) as error:
                client.update_topic(
                    room_id,
                    "first",
                    ChatTopic(title="Stale update", state=ChatTopicState.NORMAL),
                    etag=fetched.etag,
                    match_condition=MatchConditions.IfNotModified,
                )
            assert error.value.status_code == 412
            client.delete_topic(room_id, "first", etag=archived.etag, match_condition=MatchConditions.IfNotModified)
        finally:
            self.cleanup(setup.delete_room, room_id)
            setup.close()
            client.close()

    @WebPubSubChatPreparer()
    @recorded_by_proxy
    def test_room_user_and_user_room_collections(self, wps_chat_endpoint):
        client = self.create_client(wps_chat_endpoint)
        setup = self.create_client(wps_chat_endpoint, api_version="2026-02-01-preview")
        room_ids = ["python-e2e-collection-1", "python-e2e-collection-2"]
        user_ids = ["python-e2e-collection-user-1", "python-e2e-collection-user-2"]
        user_role = "user.python_e2e_collections"
        room_role = "room.python_e2e_collections"
        try:
            setup.create_or_replace_role(user_role, ChatRole(permissions=[ChatPermission.USER_CREATE_ROOM]))
            setup.create_or_replace_role(room_role, ChatRole(permissions=[ChatPermission.ROOM_PUBLISH_MESSAGE]))
            for user_id in user_ids:
                setup.create_or_replace_user(user_id, HumanChatUser(nickname=user_id, role_name=user_role))
            assert list(client.list_rooms_for_user(user_ids[0])) == []
            for room_id in room_ids:
                setup.create_or_replace_room(room_id, ChatRoom(title=room_id))
                setup.create_or_replace_room_member(room_id, user_ids[0], ChatRoomMember(role_name=room_role))
            assert {room.id for room in client.list_rooms(max_page_size=1)}.issuperset(room_ids)
            users = list(client.list_users(max_page_size=1))
            assert {user.id for user in users}.issuperset(user_ids)
            assert all(isinstance(user, HumanChatUser) for user in users if user.id in user_ids)
            assert {room.id for room in client.list_rooms_for_user(user_ids[0])} == set(room_ids)
            _assert_resumable_pages(client.list_rooms(max_page_size=1))
            _assert_resumable_pages(client.list_users(max_page_size=1))
            _assert_resumable_pages(client.list_rooms_for_user(user_ids[0], params={"maxpagesize": 1}))
            setup.delete_room_member(room_ids[0], user_ids[0])
            assert {room.id for room in client.list_rooms_for_user(user_ids[0])} == {room_ids[1]}
        finally:
            for room_id in room_ids:
                self.cleanup(setup.delete_room, room_id)
            for user_id in user_ids:
                self.cleanup(setup.delete_user, user_id)
            self.cleanup(setup.delete_role, user_role)
            self.cleanup(setup.delete_role, room_role)
            setup.close()
            client.close()
