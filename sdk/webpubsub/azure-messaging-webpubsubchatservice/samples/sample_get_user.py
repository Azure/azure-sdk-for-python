# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Read an existing user."""

import os

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient
from _shared import run_sample


def sample(client: WebPubSubChatServiceClient) -> None:
    user = client.get_user(os.environ["WPS_CHAT_USER_ID"])
    print(user.id, user.kind)


if __name__ == "__main__":
    run_sample(sample, ("WPS_CHAT_USER_ID",))
