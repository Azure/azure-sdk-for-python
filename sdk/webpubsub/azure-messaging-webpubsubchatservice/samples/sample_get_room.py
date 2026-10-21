# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Read an existing room and its default conversation ID."""

import os

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient
from _shared import run_sample


def sample(client: WebPubSubChatServiceClient) -> None:
    room = client.get_room(os.environ["WPS_CHAT_ROOM_ID"])
    print(room.id, room.title, room.default_conversation)


if __name__ == "__main__":
    run_sample(sample, ("WPS_CHAT_ROOM_ID",))
