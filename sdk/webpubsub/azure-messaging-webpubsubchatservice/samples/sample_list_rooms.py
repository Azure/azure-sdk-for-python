# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Iterate rooms with a requested page size."""

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient
from _shared import run_sample


def sample(client: WebPubSubChatServiceClient) -> None:
    for room in client.list_rooms(max_page_size=10):
        print(room.id, room.title)


if __name__ == "__main__":
    run_sample(sample)
