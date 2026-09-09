# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import os
import uuid

from azure.core.exceptions import HttpResponseError
from azure.messaging.webpubsubservice.chat import WebPubSubChatServiceClient
from azure.messaging.webpubsubservice.chat.models import (
    ChatPermission,
    ChatRole,
    ChatRoom,
    ChatRoomMember,
    HumanChatUser,
)


def main():
    connection_string = os.environ.get("WPS_CHAT_CONNECTION_STRING")
    if not connection_string:
        print("Set WPS_CHAT_CONNECTION_STRING to run this sample.")
        return

    suffix = uuid.uuid4().hex[:8]
    user_role = f"user.sample_{suffix}"
    room_role = f"room.sample_{suffix}"
    user_id = f"sample-user-{suffix}"
    room_id = f"sample-room-{suffix}"
    with WebPubSubChatServiceClient.from_connection_string(
        connection_string,
        os.environ.get("WPS_CHAT_HUB", "test_hub"),
    ) as client:
        try:
            client.create_or_replace_role(user_role, ChatRole(permissions=[ChatPermission.USER_CREATE_ROOM]))
            client.create_or_replace_role(room_role, ChatRole(permissions=[ChatPermission.ROOM_PUBLISH_MESSAGE]))
            client.create_or_replace_user(
                user_id,
                HumanChatUser(nickname="Sample User", role_name=user_role),
            )
            client.create_or_replace_room(room_id, ChatRoom(title="Sample Room"))
            client.create_or_replace_room_member(
                room_id,
                user_id,
                ChatRoomMember(role_name=room_role),
            )
            for member in client.list_room_members(room_id):
                print(member.user_id, member.role_name)
        except HttpResponseError as error:
            print(f"Chat service request failed: {error}")
            raise
        finally:
            for action, args in (
                (client.delete_room, (room_id,)),
                (client.delete_user, (user_id,)),
                (client.delete_role, (user_role,)),
                (client.delete_role, (room_role,)),
            ):
                try:
                    action(*args)
                except HttpResponseError:
                    pass


if __name__ == "__main__":
    main()
