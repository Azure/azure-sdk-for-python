# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------


class ChatRoles:
    """Built-in Web PubSub Chat roles."""

    USER_NORMAL = "user.normal"
    ROOM_MEMBER = "room.member"
    ROOM_OPERATOR = "room.operator"


class UserPermissions:
    """Built-in Web PubSub Chat user permissions."""

    CREATE_ROOM = "user.create_room"
    FETCH_ALL_ROOMS = "user.fetch_all_rooms"


class RoomPermissions:
    """Built-in Web PubSub Chat room permissions."""

    INVITE_USER = "room.invite"
    REMOVE_USER = "room.remove_user"
    READ_HISTORY = "room.history"
    PUBLISH_MESSAGE = "room.publish_message"


__all__ = ["ChatRoles", "RoomPermissions", "UserPermissions"]
