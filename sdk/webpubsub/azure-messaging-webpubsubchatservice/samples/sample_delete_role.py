# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Delete a sample-specific role. Do not target a role used by your application."""

import os

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient
from _shared import run_sample


def sample(client: WebPubSubChatServiceClient) -> None:
    client.delete_role(os.environ["WPS_CHAT_ROLE_NAME"])


if __name__ == "__main__":
    run_sample(sample, ("WPS_CHAT_ROLE_NAME",))
