# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Archive an existing topic only if it has not changed since it was read."""

from azure.core import MatchConditions
from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient
from azure.messaging.webpubsubchatservice.models import ChatTopicState, ChatTopicUpdate


def sample(client: WebPubSubChatServiceClient) -> None:
    current = client.get_topic("sample-room", "sample-topic")
    topic = client.update_topic(
        "sample-room",
        "sample-topic",
        ChatTopicUpdate(state=ChatTopicState.ARCHIVED),
        etag=current.etag,
        match_condition=MatchConditions.IfNotModified,
    )
    print(topic.id, topic.state, topic.etag)
