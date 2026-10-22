# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Three equivalent ways to add an existing user to a room with an existing room role.

Each function accepts an authenticated client. Adapt the example identifiers
before calling one of the functions; all three create or replace the same membership.
"""

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient, models, types


def model_based(client: WebPubSubChatServiceClient) -> None:
    member = client.create_or_replace_room_member(
        "sample-room",
        "sample-user",
        models.ChatRoomMemberCreateOrReplace(role_name="room.member"),
    )
    print(member.user_id, member.role_name)


def typed_dictionary(client: WebPubSubChatServiceClient) -> None:
    resource: types.ChatRoomMemberCreateOrReplace = {"roleName": "room.member"}
    member = client.create_or_replace_room_member("sample-room", "sample-user", resource)
    print(member.user_id, member.role_name)


def plain_dictionary(client: WebPubSubChatServiceClient) -> None:
    member = client.create_or_replace_room_member("sample-room", "sample-user", {"roleName": "room.member"})
    print(member.user_id, member.role_name)
