# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Iterate persisted messages from an existing conversation."""

import os

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient
from _shared import run_sample


def sample(client: WebPubSubChatServiceClient) -> None:
    for message in client.list_messages(os.environ["WPS_CHAT_CONVERSATION_ID"]):
        print(message.id, message.created_by, message.content)


if __name__ == "__main__":
    run_sample(sample, ("WPS_CHAT_CONVERSATION_ID",))
