# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Create or replace a sample-specific room."""

import os

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient
from azure.messaging.webpubsubchatservice.models import ChatRoomCreateOrReplace
from _shared import run_sample


def sample(client: WebPubSubChatServiceClient) -> None:
    room = client.create_or_replace_room(os.environ["WPS_CHAT_ROOM_ID"], ChatRoomCreateOrReplace(title="Sample room"))
    print(room.id, room.title, room.default_conversation)


if __name__ == "__main__":
    run_sample(sample, ("WPS_CHAT_ROOM_ID",))
