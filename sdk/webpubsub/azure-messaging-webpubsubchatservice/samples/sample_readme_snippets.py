# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Atomic README snippet sources; each function uses an authenticated client."""

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient


def list_roles(client: WebPubSubChatServiceClient) -> None:
    # [START list_roles]
    for role in client.list_roles():
        print(role.name)
    # [END list_roles]


def create_user(client: WebPubSubChatServiceClient) -> None:
    # [START create_user]
    from azure.messaging.webpubsubchatservice.models import HumanChatUser

    user = client.create_or_replace_user(
        "alice",
        HumanChatUser(nickname="Alice", role_name="user.room_creator"),
    )
    print(user.id, user.nickname)
    # [END create_user]


def create_room(client: WebPubSubChatServiceClient) -> None:
    # [START create_room]
    from azure.messaging.webpubsubchatservice.models import ChatRoom

    room = client.create_or_replace_room("general", ChatRoom(title="General"))
    print(room.id, room.default_conversation)
    # [END create_room]


def add_room_member(client: WebPubSubChatServiceClient) -> None:
    # [START add_room_member]
    from azure.messaging.webpubsubchatservice.models import ChatRoomMember

    member = client.create_or_replace_room_member(
        "general",
        "alice",
        ChatRoomMember(role_name="room.contributor"),
    )
    print(member.user_id, member.role_name)
    # [END add_room_member]


def list_messages(client: WebPubSubChatServiceClient) -> None:
    # [START list_messages]
    import os

    for message in client.list_messages(os.environ["WPS_CHAT_CONVERSATION_ID"]):
        print(message.id, message.created_by, message.content.text)
    # [END list_messages]


def create_topic(client: WebPubSubChatServiceClient) -> None:
    # [START create_topic]
    import os
    from azure.messaging.webpubsubchatservice.models import ChatTopic

    topic = client.create_or_replace_topic(
        os.environ["WPS_CHAT_ROOM_ID"],
        os.environ["WPS_CHAT_TOPIC_ID"],
        ChatTopic({"title": "Announcements"}),
    )
    print(topic.id, topic.etag)
    # [END create_topic]


def list_topics(client: WebPubSubChatServiceClient) -> None:
    # [START list_topics]
    import os

    for topic in client.list_topics(os.environ["WPS_CHAT_ROOM_ID"], max_page_size=10):
        print(topic.id, topic.title, topic.conversation_id)
    # [END list_topics]


def get_topic(client: WebPubSubChatServiceClient) -> None:
    # [START get_topic]
    import os

    topic = client.get_topic(os.environ["WPS_CHAT_ROOM_ID"], os.environ["WPS_CHAT_TOPIC_ID"])
    print(topic.id, topic.title, topic.state, topic.etag)
    # [END get_topic]


def archive_topic(client: WebPubSubChatServiceClient) -> None:
    # [START archive_topic]
    import os
    from azure.core import MatchConditions
    from azure.messaging.webpubsubchatservice.models import ChatTopic, ChatTopicState

    topic = client.update_topic(
        os.environ["WPS_CHAT_ROOM_ID"],
        os.environ["WPS_CHAT_TOPIC_ID"],
        ChatTopic(title="Announcements", state=ChatTopicState.ARCHIVED),
        etag=os.environ["WPS_CHAT_TOPIC_ETAG"],
        match_condition=MatchConditions.IfNotModified,
    )
    print(topic.id, topic.state, topic.etag)
    # [END archive_topic]


def delete_topic(client: WebPubSubChatServiceClient) -> None:
    # [START delete_topic]
    import os
    from azure.core import MatchConditions

    client.delete_topic(
        os.environ["WPS_CHAT_ROOM_ID"],
        os.environ["WPS_CHAT_TOPIC_ID"],
        etag=os.environ["WPS_CHAT_TOPIC_ETAG"],
        match_condition=MatchConditions.IfNotModified,
    )
    # [END delete_topic]


def list_rooms(client: WebPubSubChatServiceClient) -> None:
    # [START list_rooms]
    for room in client.list_rooms(max_page_size=10):
        print(room.id, room.title)
    # [END list_rooms]


def list_users(client: WebPubSubChatServiceClient) -> None:
    # [START list_users]
    for user in client.list_users(max_page_size=10):
        print(user.id, user.kind)
    # [END list_users]


def list_rooms_for_user(client: WebPubSubChatServiceClient) -> None:
    # [START list_rooms_for_user]
    import os

    for room in client.list_rooms_for_user(os.environ["WPS_CHAT_USER_ID"]):
        print(room.id, room.title)
    # [END list_rooms_for_user]


async def async_list_roles(endpoint: str, hub: str) -> None:
    # [START async_list_roles]
    from azure.identity.aio import DefaultAzureCredential
    from azure.messaging.webpubsubchatservice.aio import WebPubSubChatServiceClient

    credential = DefaultAzureCredential()
    client = WebPubSubChatServiceClient(endpoint, hub, credential)
    try:
        async for role in client.list_roles():
            print(role.name)
    finally:
        await client.close()
        await credential.close()
    # [END async_list_roles]
