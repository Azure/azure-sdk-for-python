# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Add an existing user to a room, or replace their room role."""

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient
from azure.messaging.webpubsubchatservice.models import ChatRoomMemberCreateOrReplace


def sample(client: WebPubSubChatServiceClient) -> None:
    member = client.create_or_replace_room_member(
        "sample-room",
        "sample-user",
        ChatRoomMemberCreateOrReplace(role_name="room.member"),
    )
    print(member.user_id, member.role_name)
