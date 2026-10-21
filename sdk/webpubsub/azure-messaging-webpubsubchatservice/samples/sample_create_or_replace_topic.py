# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Create or replace a sample-specific topic in an existing room."""

import os

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient
from azure.messaging.webpubsubchatservice.models import ChatTopicCreateOrReplace
from _shared import run_sample


def sample(client: WebPubSubChatServiceClient) -> None:
    topic = client.create_or_replace_topic(
        os.environ["WPS_CHAT_ROOM_ID"],
        os.environ["WPS_CHAT_TOPIC_ID"],
        ChatTopicCreateOrReplace(title="Sample topic"),
    )
    print(topic.id, topic.conversation_id, topic.etag)


if __name__ == "__main__":
    run_sample(sample, ("WPS_CHAT_ROOM_ID", "WPS_CHAT_TOPIC_ID"))
