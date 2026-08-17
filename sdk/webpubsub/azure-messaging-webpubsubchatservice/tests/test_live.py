# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
from devtools_testutils import recorded_by_proxy

from azure.messaging.webpubsubservice.chat import RoomPermissions, UserPermissions
from azure.messaging.webpubsubservice.chat.models import ChatRole, ChatRoom, ChatRoomMember, HumanChatUser

from testcase import WebPubSubChatPreparer, WebPubSubChatTest


class TestWebPubSubChatLive(WebPubSubChatTest):
    @WebPubSubChatPreparer()
    @recorded_by_proxy
    def test_role_lifecycle_and_paging(self, wps_chat_connection_string):
        client = self.create_client(wps_chat_connection_string)
        role_names = ["user.python_e2e_role_1", "user.python_e2e_role_2"]
        try:
            for role_name in role_names:
                role = client.create_or_replace_role(
                    role_name,
                    ChatRole(permissions=[UserPermissions.CREATE_ROOM]),
                )
                assert role.name == role_name
                assert client.get_role(role_name).permissions == [UserPermissions.CREATE_ROOM]

            listed = list(client.list_roles(maxpagesize=1))
            assert {role.name for role in listed}.issuperset(role_names)
        finally:
            for role_name in role_names:
                self.cleanup(client.delete_role, role_name)
            client.close()

    @WebPubSubChatPreparer()
    @recorded_by_proxy
    def test_room_conversation_and_empty_pages(self, wps_chat_connection_string):
        client = self.create_client(wps_chat_connection_string)
        room_id = "python-e2e-empty-room"
        try:
            room = client.create_or_replace_room(room_id, ChatRoom(title="Python E2E Room"))
            assert room.id == room_id
            assert client.get_room(room_id).title == "Python E2E Room"

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
    def test_user_and_room_member_lifecycle(self, wps_chat_connection_string):
        client = self.create_client(wps_chat_connection_string)
        user_role = "user.python_e2e_member"
        room_role = "room.python_e2e_member"
        user_id = "python-e2e-user"
        room_id = "python-e2e-member-room"
        try:
            client.create_or_replace_role(user_role, ChatRole(permissions=[UserPermissions.CREATE_ROOM]))
            client.create_or_replace_role(room_role, ChatRole(permissions=[RoomPermissions.PUBLISH_MESSAGE]))
            user = client.create_or_replace_user(
                user_id,
                HumanChatUser(nickname="Python User", role_name=user_role),
            )
            assert user.id == user_id
            assert client.get_user(user_id).nickname == "Python User"

            client.create_or_replace_room(room_id, ChatRoom(title="Member Room"))
            member = client.create_or_replace_room_member(
                room_id,
                user_id,
                ChatRoomMember(role_name=room_role),
            )
            assert member.user_id == user_id
            assert any(item.user_id == user_id for item in client.list_room_members(room_id))
            client.delete_room_member(room_id, user_id)
        finally:
            self.cleanup(client.delete_room, room_id)
            self.cleanup(client.delete_user, user_id)
            self.cleanup(client.delete_role, user_role)
            self.cleanup(client.delete_role, room_role)
            client.close()

    @WebPubSubChatPreparer()
    @recorded_by_proxy
    def test_client_access_token(self, wps_chat_connection_string):
        client = self.create_client(wps_chat_connection_string)
        try:
            result = client.get_client_access_token(user_id="python-e2e-access-user")
            assert result["baseUrl"].startswith("wss://")
            assert "access_token=" in result["url"]
        finally:
            client.close()
