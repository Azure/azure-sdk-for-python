# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import pytest
from devtools_testutils.aio import recorded_by_proxy_async

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


async def _collect(paged):
    return [item async for item in paged]


class TestWebPubSubChatLiveAsync(WebPubSubChatTest):
    @WebPubSubChatPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_async_role_lifecycle_and_paging(self, wps_chat_endpoint):
        client = self.create_async_client(wps_chat_endpoint)
        role_names = ["user.python_async_e2e_role_1", "user.python_async_e2e_role_2"]
        try:
            for role_name in role_names:
                role = await client.create_or_replace_role(
                    role_name,
                    ChatRole(permissions=[ChatPermission.USER_CREATE_ROOM]),
                )
                assert role.name == role_name
                assert (await client.get_role(role_name)).permissions == [
                    ChatPermission.USER_CREATE_ROOM
                ]

            listed = await _collect(client.list_roles(maxpagesize=1))
            assert {role.name for role in listed}.issuperset(role_names)

            page_iterator = client.list_roles(maxpagesize=1).by_page()
            first_page = await _collect(await anext(page_iterator))
            assert len(first_page) == 1
            assert page_iterator.continuation_token

            resumed_page_iterator = client.list_roles(maxpagesize=1).by_page(
                page_iterator.continuation_token
            )
            second_page = await _collect(await anext(resumed_page_iterator))
            assert len(second_page) == 1
            assert second_page[0].name != first_page[0].name
        finally:
            for role_name in role_names:
                await self.cleanup_async(client.delete_role, role_name)
            await client.close()

    @WebPubSubChatAccessPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_async_list_roles_using_connection_string(
        self,
        wps_chat_endpoint,
        wps_chat_connection_string,
        wps_chat_disable_local_auth,
    ):
        if wps_chat_disable_local_auth.lower() == "true":
            pytest.skip("Local authentication is disabled")

        client = self.create_async_key_client(wps_chat_connection_string)
        try:
            roles = await _collect(client.list_roles())
            assert all(role.name for role in roles)
        finally:
            await client.close()

    @WebPubSubChatPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_async_create_role_only_when_missing(self, wps_chat_endpoint):
        client = self.create_async_client(wps_chat_endpoint)
        role_name = "user.python_async_create_only_role"
        try:
            created = await client.create_or_replace_role(
                role_name,
                ChatRole(permissions=[ChatPermission.USER_CREATE_ROOM]),
                match_condition=MatchConditions.IfMissing,
            )
            assert created.name == role_name

            with pytest.raises(HttpResponseError) as error:
                await client.create_or_replace_role(
                    role_name,
                    ChatRole(permissions=[ChatPermission.USER_FETCH_ALL_ROOMS]),
                    match_condition=MatchConditions.IfMissing,
                )
            assert error.value.status_code == 412
        finally:
            await self.cleanup_async(client.delete_role, role_name)
            await client.close()

    @WebPubSubChatPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_async_rejects_stale_role_etag(self, wps_chat_endpoint):
        client = self.create_async_client(wps_chat_endpoint)
        role_name = "user.python_async_etag_role"
        try:
            created = await client.create_or_replace_role(
                role_name,
                ChatRole(permissions=[ChatPermission.USER_CREATE_ROOM]),
            )
            replaced = await client.create_or_replace_role(
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
                await client.create_or_replace_role(
                    role_name,
                    ChatRole(permissions=[ChatPermission.USER_CREATE_ROOM]),
                    etag=created.etag,
                    match_condition=MatchConditions.IfNotModified,
                )
            assert error.value.status_code == 412
        finally:
            await self.cleanup_async(client.delete_role, role_name)
            await client.close()

    @WebPubSubChatPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_async_room_conversation_and_empty_pages(self, wps_chat_endpoint):
        client = self.create_async_client(wps_chat_endpoint)
        room_id = "python-async-e2e-empty-room"
        try:
            room = await client.create_or_replace_room(
                room_id, ChatRoom(title="Async Python E2E Room")
            )
            assert room.id == room_id
            fetched_room = await client.get_room(room_id)
            assert fetched_room.id == room_id
            assert fetched_room.title == "Async Python E2E Room"

            conversation = await client.get_conversation(room.default_conversation)
            assert conversation.id == room.default_conversation
            assert conversation.parent_room == room_id
            assert await _collect(client.list_messages(room.default_conversation)) == []
            assert await _collect(client.list_room_members(room_id)) == []
        finally:
            await self.cleanup_async(client.delete_room, room_id)
            await client.close()

    @WebPubSubChatPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_async_user_and_room_member_lifecycle(self, wps_chat_endpoint):
        client = self.create_async_client(wps_chat_endpoint)
        user_role = "user.python_async_e2e_member"
        room_role = "room.python_async_e2e_member"
        user_id = "python-async-e2e-user"
        room_id = "python-async-e2e-member-room"
        try:
            await client.create_or_replace_role(
                user_role, ChatRole(permissions=[ChatPermission.USER_CREATE_ROOM])
            )
            await client.create_or_replace_role(
                room_role, ChatRole(permissions=[ChatPermission.ROOM_PUBLISH_MESSAGE])
            )

            user = await client.create_or_replace_user(
                user_id,
                HumanChatUser(nickname="Async Python User", role_name=user_role),
            )
            assert user.id == user_id
            assert user.kind == "Human"
            fetched_user = await client.get_user(user_id)
            assert fetched_user.id == user_id
            assert fetched_user.nickname == "Async Python User"
            await client.create_or_replace_room(
                room_id, ChatRoom(title="Async Member Room")
            )
            member = await client.create_or_replace_room_member(
                room_id,
                user_id,
                ChatRoomMember(role_name=room_role),
            )
            assert member.user_id == user_id
            assert member.role_name == room_role
            assert any(
                item.user_id == user_id and item.role_name == room_role
                for item in await _collect(client.list_room_members(room_id))
            )
            await client.delete_room_member(room_id, user_id)
        finally:
            await self.cleanup_async(client.delete_room, room_id)
            await self.cleanup_async(client.delete_user, user_id)
            await self.cleanup_async(client.delete_role, user_role)
            await self.cleanup_async(client.delete_role, room_role)
            await client.close()

    @WebPubSubChatPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_async_message_lifecycle(self, wps_chat_endpoint):
        client = self.create_async_client(wps_chat_endpoint)
        user_role = "user.python_async_message"
        room_role = "room.python_async_message"
        user_id = "python-async-message-user"
        room_id = "python-async-message-room"
        message_text = "Python async E2E original message"
        updated_text = "Python async E2E updated message"
        binary_content = bytes([0, 1, 2, 254, 255])
        try:
            await client.create_or_replace_role(
                user_role, ChatRole(permissions=[ChatPermission.USER_CREATE_ROOM])
            )
            await client.create_or_replace_role(
                room_role,
                ChatRole(
                    permissions=[
                        ChatPermission.ROOM_PUBLISH_MESSAGE,
                        ChatPermission.ROOM_HISTORY,
                    ]
                ),
            )
            await client.create_or_replace_user(
                user_id,
                HumanChatUser(nickname="Async Message User", role_name=user_role),
            )
            room = await client.create_or_replace_room(
                room_id, ChatRoom(title="Async Message Room")
            )
            await client.create_or_replace_room_member(
                room_id, user_id, ChatRoomMember(role_name=room_role)
            )

            await self.seed_chat_message_async(client, user_id, room.default_conversation, message_text)
            messages = await _collect(client.list_messages(room.default_conversation))
            message = next(
                item
                for item in messages
                if item.created_by == user_id and item.content.text == message_text
            )
            updated = await client.update_message(
                room.default_conversation,
                message.id,
                ChatMessage(
                    created_by=user_id, content=MessageContent(text=updated_text)
                ),
            )
            assert updated.content.text == updated_text
            binary_updated = await client.update_message(
                room.default_conversation,
                message.id,
                ChatMessage(
                    created_by=user_id,
                    content=MessageContent(binary=binary_content),
                ),
            )
            assert binary_updated.content.binary == binary_content
            await client.delete_message(room.default_conversation, message.id)
            assert all(
                item.id != message.id
                for item in await _collect(
                    client.list_messages(room.default_conversation)
                )
            )
        finally:
            await self.cleanup_async(client.delete_room, room_id)
            await self.cleanup_async(client.delete_user, user_id)
            await self.cleanup_async(client.delete_role, user_role)
            await self.cleanup_async(client.delete_role, room_role)
            await client.close()

    @WebPubSubChatAccessPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_async_client_access_token(
        self,
        wps_chat_endpoint,
        wps_chat_connection_string,
        wps_chat_disable_local_auth,
    ):
        if wps_chat_disable_local_auth.lower() == "true":
            pytest.skip("Local authentication is disabled")

        token_client = self.create_async_client(wps_chat_endpoint)
        key_client = self.create_async_key_client(wps_chat_connection_string)
        try:
            token_access = await token_client.get_client_access_token(
                user_id="python-async-e2e-token-access-user"
            )
            await self.assert_client_access_async(token_access, wps_chat_endpoint)

            key_access = await key_client.get_client_access_token(
                user_id="python-async-e2e-key-access-user"
            )
            await self.assert_client_access_async(key_access, wps_chat_endpoint)
        finally:
            await token_client.close()
            await key_client.close()
