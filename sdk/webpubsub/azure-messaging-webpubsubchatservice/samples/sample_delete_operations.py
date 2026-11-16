# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Independent destructive examples. Replace identifiers with isolated sample resources."""

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient


def delete_role(client: WebPubSubChatServiceClient) -> None:
    client.delete_role("room.sample")


def delete_room(client: WebPubSubChatServiceClient) -> None:
    client.delete_room("sample-room")


def delete_room_member(client: WebPubSubChatServiceClient) -> None:
    client.delete_room_member("sample-room", "sample-user")


def delete_user(client: WebPubSubChatServiceClient) -> None:
    client.delete_user("sample-user")


def delete_topic(client: WebPubSubChatServiceClient) -> None:
    client.delete_topic("sample-room", "sample-topic")


def delete_message(client: WebPubSubChatServiceClient) -> None:
    client.delete_message("c.sample-room.sample-topic", "123456789")
