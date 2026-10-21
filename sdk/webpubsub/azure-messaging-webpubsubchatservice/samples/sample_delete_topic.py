# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Soft delete a topic only if the supplied ETag still matches."""

import os

from azure.core import MatchConditions
from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient
from _shared import run_sample


def sample(client: WebPubSubChatServiceClient) -> None:
    client.delete_topic(
        os.environ["WPS_CHAT_ROOM_ID"],
        os.environ["WPS_CHAT_TOPIC_ID"],
        etag=os.environ["WPS_CHAT_TOPIC_ETAG"],
        match_condition=MatchConditions.IfNotModified,
    )


if __name__ == "__main__":
    run_sample(sample, ("WPS_CHAT_ROOM_ID", "WPS_CHAT_TOPIC_ID", "WPS_CHAT_TOPIC_ETAG"))
