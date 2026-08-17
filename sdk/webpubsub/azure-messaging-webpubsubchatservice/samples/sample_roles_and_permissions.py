# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
from azure.messaging.webpubsubservice.chat import ChatRoles, RoomPermissions, UserPermissions


print(ChatRoles.USER_NORMAL)
print(ChatRoles.ROOM_MEMBER)
print(ChatRoles.ROOM_OPERATOR)
print(UserPermissions.CREATE_ROOM)
print(UserPermissions.FETCH_ALL_ROOMS)
print(RoomPermissions.INVITE_USER)
print(RoomPermissions.REMOVE_USER)
print(RoomPermissions.READ_HISTORY)
print(RoomPermissions.PUBLISH_MESSAGE)
