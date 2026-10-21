# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Read an existing role."""

import os

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient
from _shared import run_sample


def sample(client: WebPubSubChatServiceClient) -> None:
    role = client.get_role(os.environ["WPS_CHAT_ROLE_NAME"])
    print(role.name, role.permissions)


if __name__ == "__main__":
    run_sample(sample, ("WPS_CHAT_ROLE_NAME",))
