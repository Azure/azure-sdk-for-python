# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Add an existing user to a room, or replace their room role."""

import os

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient
from azure.messaging.webpubsubchatservice.models import ChatRoomMemberCreateOrReplace
from _shared import run_sample


def sample(client: WebPubSubChatServiceClient) -> None:
    member = client.create_or_replace_room_member(
        os.environ["WPS_CHAT_ROOM_ID"],
        os.environ["WPS_CHAT_USER_ID"],
        ChatRoomMemberCreateOrReplace(role_name=os.environ["WPS_CHAT_ROOM_ROLE_NAME"]),
    )
    print(member.user_id, member.role_name)


if __name__ == "__main__":
    run_sample(sample, ("WPS_CHAT_ROOM_ID", "WPS_CHAT_USER_ID", "WPS_CHAT_ROOM_ROLE_NAME"))
