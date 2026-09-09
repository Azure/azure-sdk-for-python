# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import os

from azure.messaging.webpubsubservice.chat import WebPubSubChatServiceClient


def main():
    required = ("WPS_CHAT_CONNECTION_STRING", "WPS_CHAT_CONVERSATION_ID")
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        print(f"Set {', '.join(missing)} to run this sample.")
        return

    with WebPubSubChatServiceClient.from_connection_string(
        os.environ["WPS_CHAT_CONNECTION_STRING"],
        os.environ.get("WPS_CHAT_HUB", "test_hub"),
    ) as client:
        for message in client.list_messages(os.environ["WPS_CHAT_CONVERSATION_ID"]):
            print(message.id, message.created_by, message.content.text)


if __name__ == "__main__":
    main()
