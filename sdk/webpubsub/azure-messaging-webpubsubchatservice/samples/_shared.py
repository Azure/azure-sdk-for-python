# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Configuration and client lifetime for the operation samples."""

import os
from typing import Callable

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient


def run_sample(sample: Callable[[WebPubSubChatServiceClient], None], required: tuple[str, ...] = ()) -> None:
    missing = [name for name in ("WPS_CHAT_CONNECTION_STRING", *required) if not os.environ.get(name)]
    if missing:
        print(f"Set {', '.join(missing)} to run this sample.")
        return

    with WebPubSubChatServiceClient.from_connection_string(
        os.environ["WPS_CHAT_CONNECTION_STRING"],
        os.environ.get("WPS_CHAT_HUB", "test_hub"),
    ) as client:
        sample(client)
