# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Iterate the members of an existing room."""

import os

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient
from _shared import run_sample


def sample(client: WebPubSubChatServiceClient) -> None:
    for member in client.list_room_members(os.environ["WPS_CHAT_ROOM_ID"]):
        print(member.user_id, member.role_name)


if __name__ == "__main__":
    run_sample(sample, ("WPS_CHAT_ROOM_ID",))
