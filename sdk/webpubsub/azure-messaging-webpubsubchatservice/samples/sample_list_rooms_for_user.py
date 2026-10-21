# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Iterate rooms associated with an existing user."""

import os

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient
from _shared import run_sample


def sample(client: WebPubSubChatServiceClient) -> None:
    for room in client.list_rooms_for_user(os.environ["WPS_CHAT_USER_ID"]):
        print(room.id, room.title)


if __name__ == "__main__":
    run_sample(sample, ("WPS_CHAT_USER_ID",))
