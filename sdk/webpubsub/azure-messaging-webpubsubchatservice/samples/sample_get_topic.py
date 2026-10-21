# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Read a topic and the ETag used for a conditional update or delete."""

import os

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient
from _shared import run_sample


def sample(client: WebPubSubChatServiceClient) -> None:
    topic = client.get_topic(os.environ["WPS_CHAT_ROOM_ID"], os.environ["WPS_CHAT_TOPIC_ID"])
    print(topic.id, topic.title, topic.state, topic.etag)


if __name__ == "__main__":
    run_sample(sample, ("WPS_CHAT_ROOM_ID", "WPS_CHAT_TOPIC_ID"))
