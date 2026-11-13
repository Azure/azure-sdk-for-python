# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Create or replace a sample-specific room role. Existing permissions are replaced."""

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient
from azure.messaging.webpubsubchatservice.models import ChatPermission, ChatRoleCreateOrReplace


def sample(client: WebPubSubChatServiceClient) -> None:
    role = client.create_or_replace_role(
        "room.sample",
        ChatRoleCreateOrReplace(permissions=[ChatPermission.ROOM_HISTORY, ChatPermission.ROOM_PUBLISH_MESSAGE]),
    )
    print(role.name, role.permissions)
