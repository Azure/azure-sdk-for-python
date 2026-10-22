# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Create or replace a sample-specific room."""

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient
from azure.messaging.webpubsubchatservice.models import ChatRoomCreateOrReplace


def sample(client: WebPubSubChatServiceClient) -> None:
    room = client.create_or_replace_room("sample-room", ChatRoomCreateOrReplace(title="Sample room"))
    print(room.id, room.title, room.default_conversation)
