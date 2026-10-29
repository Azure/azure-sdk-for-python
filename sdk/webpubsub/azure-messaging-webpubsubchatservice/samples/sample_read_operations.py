# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Independent read examples. Supply an authenticated client and existing identifiers."""

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient


def get_role(client: WebPubSubChatServiceClient) -> None:
    role = client.get_role("room.sample")
    print(role.name, role.permissions)


def get_room(client: WebPubSubChatServiceClient) -> None:
    room = client.get_room("sample-room")
    print(room.id, room.title)


def get_user(client: WebPubSubChatServiceClient) -> None:
    user = client.get_user("sample-user")
    print(user.id, user.kind)


def get_topic(client: WebPubSubChatServiceClient) -> None:
    topic = client.get_topic("sample-room", "sample-topic")
    print(topic.id, topic.title, topic.state)


def get_conversation(client: WebPubSubChatServiceClient) -> None:
    conversation = client.get_conversation("c.sample-room.sample-topic")
    print(conversation.id, conversation.room_id)


def list_roles(client: WebPubSubChatServiceClient) -> None:
    for role in client.list_roles(max_page_size=10):
        print(role.name)


def list_rooms(client: WebPubSubChatServiceClient) -> None:
    for room in client.list_rooms(max_page_size=10):
        print(room.id, room.title)


def list_room_members(client: WebPubSubChatServiceClient) -> None:
    for member in client.list_room_members("sample-room", max_page_size=10):
        print(member.user_id, member.role_name)


def list_users(client: WebPubSubChatServiceClient) -> None:
    for user in client.list_users(max_page_size=10):
        print(user.id, user.kind)


def list_topics(client: WebPubSubChatServiceClient) -> None:
    for topic in client.list_topics("sample-room", max_page_size=10):
        print(topic.id, topic.title)


def list_rooms_for_user(client: WebPubSubChatServiceClient) -> None:
    for room in client.list_rooms_for_user("sample-user", max_page_size=10):
        print(room.id, room.title)


def list_messages(client: WebPubSubChatServiceClient) -> None:
    for message in client.list_messages("c.sample-room.sample-topic", max_page_size=10):
        print(message.id, message.created_by, message.content)
