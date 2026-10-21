# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Iterate the topics in an existing room."""

import os

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient
from _shared import run_sample


def sample(client: WebPubSubChatServiceClient) -> None:
    for topic in client.list_topics(os.environ["WPS_CHAT_ROOM_ID"], max_page_size=10):
        print(topic.id, topic.title, topic.conversation_id)


if __name__ == "__main__":
    run_sample(sample, ("WPS_CHAT_ROOM_ID",))
