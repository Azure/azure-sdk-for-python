# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Update the content of a sample-specific persisted message."""

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient
from azure.messaging.webpubsubchatservice.models import ChatMessageUpdate, MessageContent


def sample(client: WebPubSubChatServiceClient) -> None:
    message = client.update_message(
        "c.sample-room.sample-topic",
        "123456789",
        ChatMessageUpdate(content=MessageContent(text="Updated sample message")),
    )
    print(message.id, message.content)
