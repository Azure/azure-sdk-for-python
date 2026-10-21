# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Read a room's default conversation or a topic's conversation."""

import os

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient
from _shared import run_sample


def sample(client: WebPubSubChatServiceClient) -> None:
    conversation = client.get_conversation(os.environ["WPS_CHAT_CONVERSATION_ID"])
    print(conversation.id, conversation.parent_room)


if __name__ == "__main__":
    run_sample(sample, ("WPS_CHAT_CONVERSATION_ID",))
