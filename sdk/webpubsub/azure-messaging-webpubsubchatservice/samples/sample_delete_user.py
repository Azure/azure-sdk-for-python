# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Delete a sample-specific user. Do not target an active application user."""

import os

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient
from _shared import run_sample


def sample(client: WebPubSubChatServiceClient) -> None:
    client.delete_user(os.environ["WPS_CHAT_USER_ID"])


if __name__ == "__main__":
    run_sample(sample, ("WPS_CHAT_USER_ID",))
