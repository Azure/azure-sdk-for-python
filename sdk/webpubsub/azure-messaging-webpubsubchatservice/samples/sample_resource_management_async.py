# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import asyncio
import os
import uuid

from azure.core.exceptions import HttpResponseError
from azure.messaging.webpubsubservice.chat import RoomPermissions, UserPermissions
from azure.messaging.webpubsubservice.chat.aio import WebPubSubChatServiceClient
from azure.messaging.webpubsubservice.chat.models import ChatRole, ChatRoom, ChatRoomMember, HumanChatUser


async def main():
    connection_string = os.environ.get("WPS_CHAT_CONNECTION_STRING")
    if not connection_string:
        print("Set WPS_CHAT_CONNECTION_STRING to run this sample.")
        return

    suffix = uuid.uuid4().hex[:8]
    user_role = f"user.async_sample_{suffix}"
    room_role = f"room.async_sample_{suffix}"
    user_id = f"async-sample-user-{suffix}"
    room_id = f"async-sample-room-{suffix}"
    client = WebPubSubChatServiceClient.from_connection_string(
        connection_string,
        os.environ.get("WPS_CHAT_HUB", "test_hub"),
    )
    try:
        await client.create_or_replace_role(user_role, ChatRole(permissions=[UserPermissions.CREATE_ROOM]))
        await client.create_or_replace_role(room_role, ChatRole(permissions=[RoomPermissions.PUBLISH_MESSAGE]))
        await client.create_or_replace_user(
            user_id,
            HumanChatUser(nickname="Async Sample User", role_name=user_role),
        )
        await client.create_or_replace_room(room_id, ChatRoom(title="Async Sample Room"))
        await client.create_or_replace_room_member(
            room_id,
            user_id,
            ChatRoomMember(role_name=room_role),
        )
        async for member in client.list_room_members(room_id):
            print(member.user_id, member.role_name)
    finally:
        for action, args in (
            (client.delete_room, (room_id,)),
            (client.delete_user, (user_id,)),
            (client.delete_role, (user_role,)),
            (client.delete_role, (room_role,)),
        ):
            try:
                await action(*args)
            except HttpResponseError:
                pass
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
