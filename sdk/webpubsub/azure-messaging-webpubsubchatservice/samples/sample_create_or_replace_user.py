# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Create or replace a sample-specific human user with an existing user role."""

import os

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient
from azure.messaging.webpubsubchatservice.models import HumanChatUserCreateOrReplace
from _shared import run_sample


def sample(client: WebPubSubChatServiceClient) -> None:
    user = client.create_or_replace_user(
        os.environ["WPS_CHAT_USER_ID"],
        HumanChatUserCreateOrReplace(nickname="Sample user", role_name=os.environ["WPS_CHAT_USER_ROLE_NAME"]),
    )
    print(user.id, user.kind)


if __name__ == "__main__":
    run_sample(sample, ("WPS_CHAT_USER_ID", "WPS_CHAT_USER_ROLE_NAME"))
