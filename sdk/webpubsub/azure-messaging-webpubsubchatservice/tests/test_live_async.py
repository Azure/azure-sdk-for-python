# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import pytest
from devtools_testutils import recorded_by_proxy

from azure.messaging.webpubsubservice.chat import RoomPermissions, UserPermissions
from azure.messaging.webpubsubservice.chat.models import ChatRole, ChatRoom, ChatRoomMember, HumanChatUser

from testcase import WebPubSubChatPreparer, WebPubSubChatTest


async def _collect(paged):
    return [item async for item in paged]


class TestWebPubSubChatLiveAsync(WebPubSubChatTest):
    @WebPubSubChatPreparer()
    @recorded_by_proxy
    @pytest.mark.asyncio
    async def test_async_resource_lifecycle(self, wps_chat_connection_string):
        client = self.create_async_client(wps_chat_connection_string)
        user_role = "user.python_async_e2e"
        room_role = "room.python_async_e2e"
        user_id = "python-async-e2e-user"
        room_id = "python-async-e2e-room"
        try:
            await client.create_or_replace_role(user_role, ChatRole(permissions=[UserPermissions.CREATE_ROOM]))
            await client.create_or_replace_role(room_role, ChatRole(permissions=[RoomPermissions.PUBLISH_MESSAGE]))
            assert (await client.get_role(user_role)).name == user_role
            assert any(role.name == user_role for role in await _collect(client.list_roles(maxpagesize=1)))

            user = await client.create_or_replace_user(
                user_id,
                HumanChatUser(nickname="Async Python User", role_name=user_role),
            )
            assert user.id == user_id
            room = await client.create_or_replace_room(room_id, ChatRoom(title="Async Room"))
            member = await client.create_or_replace_room_member(
                room_id,
                user_id,
                ChatRoomMember(role_name=room_role),
            )
            assert member.user_id == user_id
            assert any(item.user_id == user_id for item in await _collect(client.list_room_members(room_id)))

            conversation = await client.get_conversation(room.default_conversation)
            assert conversation.parent_room == room_id
            assert await _collect(client.list_messages(room.default_conversation)) == []

            access = await client.get_client_access_token(user_id=user_id)
            assert access["baseUrl"].startswith("wss://")
            await client.delete_room_member(room_id, user_id)
        finally:
            await self.cleanup_async(client.delete_room, room_id)
            await self.cleanup_async(client.delete_user, user_id)
            await self.cleanup_async(client.delete_role, user_role)
            await self.cleanup_async(client.delete_role, room_role)
            await client.close()
