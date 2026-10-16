# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient, models, types
from azure.messaging.webpubsubchatservice.aio import WebPubSubChatServiceClient as AsyncClient


def check_request_types(client: WebPubSubChatServiceClient) -> None:
    client.update_topic("room", "topic", models.ChatTopicUpdate(title="New title"))
    client.update_topic("room", "topic", models.ChatTopicUpdate(state=models.ChatTopicState.ARCHIVED))
    client.update_topic("room", "topic", types.ChatTopicUpdate(title="New title"))
    client.update_topic("room", "topic", types.ChatTopicUpdate(state=models.ChatTopicState.ARCHIVED))
    client.update_message("conversation", "message", models.ChatMessageUpdate(created_by="user"))
    client.update_message(
        "conversation", "message", models.ChatMessageUpdate(content=models.MessageContent(text="Updated"))
    )
    client.update_message("conversation", "message", types.ChatMessageUpdate(createdBy="user"))
    client.update_message("conversation", "message", types.ChatMessageUpdate(content={"text": "Updated"}))
    client.create_or_replace_topic("room", "topic", models.ChatTopicCreateOrReplace(title="Title"))
    models.ChatTopicUpdate(title=123)  # type: ignore[call-overload]
    models.ChatTopicUpdate(state=123)  # type: ignore[call-overload]
    models.ChatTopicUpdate(id="read-only")  # type: ignore[call-overload]
    models.ChatMessageUpdate(created_by=123)  # type: ignore[call-overload]
    models.ChatMessageUpdate(content=123)  # type: ignore[call-overload]
    models.ChatTopicCreateOrReplace()  # type: ignore[call-overload]
    models.ChatTopicCreateOrReplace(title="Title", state=models.ChatTopicState.ARCHIVED)  # type: ignore[call-overload]
    types.ChatTopicUpdate(title=123)  # type: ignore[typeddict-item]
    types.ChatTopicUpdate(id="read-only")  # type: ignore[typeddict-unknown-key]
    types.ChatMessageUpdate(content=123)  # type: ignore[typeddict-item]
    types.ChatTopicCreateOrReplace()  # type: ignore[typeddict-item]


async def check_async_request_types(client: AsyncClient) -> None:
    await client.update_topic("room", "topic", models.ChatTopicUpdate(title="New title"))
    await client.update_topic("room", "topic", models.ChatTopicUpdate(state=models.ChatTopicState.ARCHIVED))
    await client.update_topic("room", "topic", types.ChatTopicUpdate(title="New title"))
    await client.update_topic("room", "topic", types.ChatTopicUpdate(state=models.ChatTopicState.ARCHIVED))
    await client.update_message("conversation", "message", models.ChatMessageUpdate(created_by="user"))
    await client.update_message(
        "conversation", "message", models.ChatMessageUpdate(content=models.MessageContent(text="Updated"))
    )
    await client.update_message("conversation", "message", types.ChatMessageUpdate(createdBy="user"))
    await client.update_message("conversation", "message", types.ChatMessageUpdate(content={"text": "Updated"}))
