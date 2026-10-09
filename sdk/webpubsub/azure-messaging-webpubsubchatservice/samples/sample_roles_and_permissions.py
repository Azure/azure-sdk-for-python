# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import os
from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient


def create_role(client):
    # [START create_role]
    from azure.messaging.webpubsubchatservice.models import ChatPermission, ChatRole

    role = client.create_or_replace_role(
        os.environ.get("WPS_CHAT_ROLE_NAME", "user.python_sample"),
        ChatRole(permissions=[ChatPermission.USER_CREATE_ROOM]),
    )
    print(role.name, role.permissions)
    # [END create_role]


def main():
    connection_string = os.environ.get("WPS_CHAT_CONNECTION_STRING")
    if not connection_string:
        raise SystemExit("Set WPS_CHAT_CONNECTION_STRING to run this sample.")

    with WebPubSubChatServiceClient.from_connection_string(
        connection_string,
        os.environ.get("WPS_CHAT_HUB", "test_hub"),
    ) as client:
        create_role(client)


if __name__ == "__main__":
    main()
