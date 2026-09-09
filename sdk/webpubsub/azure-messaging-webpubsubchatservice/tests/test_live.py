# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import pytest
from devtools_testutils import recorded_by_proxy

from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError
from azure.messaging.webpubsubservice.chat.models import (
    ChatMessage,
    ChatPermission,
    ChatRole,
    ChatRoom,
    ChatRoomMember,
    HumanChatUser,
    MessageContent,
)

from testcase import (
    WebPubSubChatAccessPreparer,
    WebPubSubChatPreparer,
    WebPubSubChatTest,
)


class TestWebPubSubChatLive(WebPubSubChatTest):
    @WebPubSubChatPreparer()
    @recorded_by_proxy
    def test_role_lifecycle_and_paging(self, wps_chat_endpoint):
        client = self.create_client(wps_chat_endpoint)
        role_names = ["user.python_e2e_role_1", "user.python_e2e_role_2"]
        try:
            for role_name in role_names:
                role = client.create_or_replace_role(
                    role_name,
                    ChatRole(permissions=[ChatPermission.USER_CREATE_ROOM]),
                )
                assert role.name == role_name
                assert client.get_role(role_name).permissions == [
                    ChatPermission.USER_CREATE_ROOM
                ]

            listed = list(client.list_roles(maxpagesize=1))
            assert {role.name for role in listed}.issuperset(role_names)

            page_iterator = client.list_roles(maxpagesize=1).by_page()
            first_page = list(next(page_iterator))
            assert len(first_page) == 1
            assert page_iterator.continuation_token

            resumed_page_iterator = client.list_roles(maxpagesize=1).by_page(
                page_iterator.continuation_token
            )
            second_page = list(next(resumed_page_iterator))
            assert len(second_page) == 1
            assert second_page[0].name != first_page[0].name
        finally:
            for role_name in role_names:
                self.cleanup(client.delete_role, role_name)
            client.close()

    @WebPubSubChatAccessPreparer()
    @recorded_by_proxy
    def test_list_roles_using_connection_string(
        self,
        wps_chat_endpoint,
        wps_chat_connection_string,
        wps_chat_disable_local_auth,
    ):
        if wps_chat_disable_local_auth.lower() == "true":
            pytest.skip("Local authentication is disabled")

        client = self.create_key_client(wps_chat_connection_string)
        try:
            roles = list(client.list_roles())
            assert all(role.name for role in roles)
        finally:
            client.close()

    @WebPubSubChatPreparer()
    @recorded_by_proxy
    def test_create_role_only_when_missing(self, wps_chat_endpoint):
        client = self.create_client(wps_chat_endpoint)
        role_name = "user.python_create_only_role"
        try:
            created = client.create_or_replace_role(
                role_name,
                ChatRole(permissions=[ChatPermission.USER_CREATE_ROOM]),
                match_condition=MatchConditions.IfMissing,
            )
            assert created.name == role_name

            with pytest.raises(HttpResponseError) as error:
                client.create_or_replace_role(
                    role_name,
                    ChatRole(permissions=[ChatPermission.USER_FETCH_ALL_ROOMS]),
                    match_condition=MatchConditions.IfMissing,
                )
            assert error.value.status_code == 412
        finally:
            self.cleanup(client.delete_role, role_name)
            client.close()

    @WebPubSubChatPreparer()
    @recorded_by_proxy
    def test_rejects_stale_role_etag(self, wps_chat_endpoint):
        client = self.create_client(wps_chat_endpoint)
        role_name = "user.python_etag_role"
        try:
            created = client.create_or_replace_role(
                role_name,
                ChatRole(permissions=[ChatPermission.USER_CREATE_ROOM]),
            )
            replaced = client.create_or_replace_role(
                role_name,
                ChatRole(
                    permissions=[
                        ChatPermission.USER_CREATE_ROOM,
                        ChatPermission.USER_FETCH_ALL_ROOMS,
                    ]
                ),
                etag=created.etag,
                match_condition=MatchConditions.IfNotModified,
            )
            assert replaced.etag != created.etag

            with pytest.raises(HttpResponseError) as error:
                client.create_or_replace_role(
                    role_name,
                    ChatRole(permissions=[ChatPermission.USER_CREATE_ROOM]),
                    etag=created.etag,
                    match_condition=MatchConditions.IfNotModified,
                )
            assert error.value.status_code == 412
        finally:
            self.cleanup(client.delete_role, role_name)
            client.close()

    @WebPubSubChatPreparer()
    @recorded_by_proxy
    def test_room_conversation_and_empty_pages(self, wps_chat_endpoint):
        client = self.create_client(wps_chat_endpoint)
        room_id = "python-e2e-empty-room"
        try:
            room = client.create_or_replace_room(
                room_id, ChatRoom(title="Python E2E Room")
            )
            assert room.id == room_id
            fetched_room = client.get_room(room_id)
            assert fetched_room.id == room_id
            assert fetched_room.title == "Python E2E Room"

            conversation = client.get_conversation(room.default_conversation)
            assert conversation.id == room.default_conversation
            assert conversation.parent_room == room_id
            assert list(client.list_messages(room.default_conversation)) == []
            assert list(client.list_room_members(room_id)) == []
        finally:
            self.cleanup(client.delete_room, room_id)
            client.close()

    @WebPubSubChatPreparer()
    @recorded_by_proxy
    def test_user_and_room_member_lifecycle(self, wps_chat_endpoint):
        client = self.create_client(wps_chat_endpoint)
        user_role = "user.python_e2e_member"
        room_role = "room.python_e2e_member"
        user_id = "python-e2e-user"
        room_id = "python-e2e-member-room"
        try:
            client.create_or_replace_role(
                user_role, ChatRole(permissions=[ChatPermission.USER_CREATE_ROOM])
            )
            client.create_or_replace_role(
                room_role, ChatRole(permissions=[ChatPermission.ROOM_PUBLISH_MESSAGE])
            )
            user = client.create_or_replace_user(
                user_id,
                HumanChatUser(nickname="Python User", role_name=user_role),
            )
            assert user.id == user_id
            assert user.kind == "Human"
            fetched_user = client.get_user(user_id)
            assert fetched_user.id == user_id
            assert fetched_user.nickname == "Python User"

            client.create_or_replace_room(room_id, ChatRoom(title="Member Room"))
            member = client.create_or_replace_room_member(
                room_id,
                user_id,
                ChatRoomMember(role_name=room_role),
            )
            assert member.user_id == user_id
            assert member.role_name == room_role
            assert any(
                item.user_id == user_id and item.role_name == room_role
                for item in client.list_room_members(room_id)
            )
            client.delete_room_member(room_id, user_id)
        finally:
            self.cleanup(client.delete_room, room_id)
            self.cleanup(client.delete_user, user_id)
            self.cleanup(client.delete_role, user_role)
            self.cleanup(client.delete_role, room_role)
            client.close()

    @WebPubSubChatPreparer()
    @recorded_by_proxy
    def test_message_lifecycle(self, wps_chat_endpoint):
        client = self.create_client(wps_chat_endpoint)
        user_role = "user.python_e2e_message"
        room_role = "room.python_e2e_message"
        user_id = "python-e2e-message-user"
        room_id = "python-e2e-message-room"
        message_text = "Python E2E original message"
        updated_text = "Python E2E updated message"
        binary_content = bytes([0, 1, 2, 254, 255])
        try:
            client.create_or_replace_role(
                user_role, ChatRole(permissions=[ChatPermission.USER_CREATE_ROOM])
            )
            client.create_or_replace_role(
                room_role,
                ChatRole(
                    permissions=[
                        ChatPermission.ROOM_PUBLISH_MESSAGE,
                        ChatPermission.ROOM_HISTORY,
                    ]
                ),
            )
            client.create_or_replace_user(
                user_id,
                HumanChatUser(nickname="Python Message User", role_name=user_role),
            )
            room = client.create_or_replace_room(
                room_id, ChatRoom(title="Python Message Room")
            )
            client.create_or_replace_room_member(
                room_id, user_id, ChatRoomMember(role_name=room_role)
            )

            self.seed_chat_message(
                client, user_id, room.default_conversation, message_text
            )
            message = next(
                item
                for item in client.list_messages(room.default_conversation)
                if item.created_by == user_id and item.content.text == message_text
            )
            updated = client.update_message(
                room.default_conversation,
                message.id,
                ChatMessage(
                    created_by=user_id, content=MessageContent(text=updated_text)
                ),
            )
            assert updated.content.text == updated_text
            binary_updated = client.update_message(
                room.default_conversation,
                message.id,
                ChatMessage(
                    created_by=user_id,
                    content=MessageContent(binary=binary_content),
                ),
            )
            assert binary_updated.content.binary == binary_content
            client.delete_message(room.default_conversation, message.id)
            assert all(
                item.id != message.id
                for item in client.list_messages(room.default_conversation)
            )
        finally:
            self.cleanup(client.delete_room, room_id)
            self.cleanup(client.delete_user, user_id)
            self.cleanup(client.delete_role, user_role)
            self.cleanup(client.delete_role, room_role)
            client.close()

    @WebPubSubChatAccessPreparer()
    @recorded_by_proxy
    def test_client_access_token(
        self,
        wps_chat_endpoint,
        wps_chat_connection_string,
        wps_chat_disable_local_auth,
    ):
        token_client = self.create_client(wps_chat_endpoint)
        key_client = None
        try:
            token_access = token_client.get_client_access_token(
                user_id="python-e2e-token-access-user"
            )
            self.assert_client_access(token_access, wps_chat_endpoint)

            if wps_chat_disable_local_auth.lower() != "true":
                key_client = self.create_key_client(wps_chat_connection_string)
                key_access = key_client.get_client_access_token(
                    user_id="python-e2e-key-access-user"
                )
                self.assert_client_access(key_access, wps_chat_endpoint)
        finally:
            token_client.close()
            if key_client:
                key_client.close()
