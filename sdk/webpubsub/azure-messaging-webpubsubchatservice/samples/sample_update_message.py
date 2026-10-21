# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Update the content of a sample-specific persisted message."""

import os

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient
from azure.messaging.webpubsubchatservice.models import ChatMessageUpdate, MessageContent
from _shared import run_sample


def sample(client: WebPubSubChatServiceClient) -> None:
    message = client.update_message(
        os.environ["WPS_CHAT_CONVERSATION_ID"],
        os.environ["WPS_CHAT_MESSAGE_ID"],
        ChatMessageUpdate(content=MessageContent(text="Updated sample message")),
    )
    print(message.id, message.content)


if __name__ == "__main__":
    run_sample(sample, ("WPS_CHAT_CONVERSATION_ID", "WPS_CHAT_MESSAGE_ID"))
