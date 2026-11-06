# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Create or replace a sample-specific topic in an existing room."""

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient
from azure.messaging.webpubsubchatservice.models import ChatTopicCreateOrReplace


def sample(client: WebPubSubChatServiceClient) -> None:
    topic = client.create_or_replace_topic(
        "sample-room",
        "sample-topic",
        ChatTopicCreateOrReplace(title="Sample topic"),
    )
    print(topic.id, topic.conversation_id, topic.etag)
