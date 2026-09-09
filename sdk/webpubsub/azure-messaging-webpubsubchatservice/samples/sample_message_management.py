# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import os

from azure.messaging.webpubsubservice.chat import WebPubSubChatServiceClient
from azure.messaging.webpubsubservice.chat.models import ChatMessage, MessageContent


def main():
    required = (
        "WPS_CHAT_CONNECTION_STRING",
        "WPS_CHAT_CONVERSATION_ID",
        "WPS_CHAT_MESSAGE_ID",
        "WPS_CHAT_USER_ID",
    )
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        print(f"Set {', '.join(missing)} to run this sample.")
        return

    with WebPubSubChatServiceClient.from_connection_string(
        os.environ["WPS_CHAT_CONNECTION_STRING"],
        os.environ.get("WPS_CHAT_HUB", "test_hub"),
    ) as client:
        conversation_id = os.environ["WPS_CHAT_CONVERSATION_ID"]
        message_id = os.environ["WPS_CHAT_MESSAGE_ID"]
        client.update_message(
            conversation_id,
            message_id,
            ChatMessage(
                created_by=os.environ["WPS_CHAT_USER_ID"],
                content=MessageContent(text="Updated message"),
            ),
        )
        client.delete_message(conversation_id, message_id)


if __name__ == "__main__":
    main()
