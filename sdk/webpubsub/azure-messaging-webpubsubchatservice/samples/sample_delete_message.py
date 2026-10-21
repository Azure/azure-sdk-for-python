# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Delete a sample-specific persisted message."""

import os

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient
from _shared import run_sample


def sample(client: WebPubSubChatServiceClient) -> None:
    client.delete_message(os.environ["WPS_CHAT_CONVERSATION_ID"], os.environ["WPS_CHAT_MESSAGE_ID"])


if __name__ == "__main__":
    run_sample(sample, ("WPS_CHAT_CONVERSATION_ID", "WPS_CHAT_MESSAGE_ID"))
