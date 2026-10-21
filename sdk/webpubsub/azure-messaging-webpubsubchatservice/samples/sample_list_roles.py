# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Iterate roles, allowing the SDK to fetch subsequent pages."""

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient
from _shared import run_sample


def sample(client: WebPubSubChatServiceClient) -> None:
    for role in client.list_roles():
        print(role.name, role.permissions)


if __name__ == "__main__":
    run_sample(sample)
