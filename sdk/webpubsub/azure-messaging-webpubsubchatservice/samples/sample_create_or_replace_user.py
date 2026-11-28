# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Create or replace a sample-specific human user with an existing user role."""

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient
from azure.messaging.webpubsubchatservice.models import HumanChatUserCreateOrReplace


def sample(client: WebPubSubChatServiceClient) -> None:
    user = client.create_or_replace_user(
        "sample-user",
        HumanChatUserCreateOrReplace(nickname="Sample user", role_name="user.member"),
    )
    print(user.id, user.kind)
