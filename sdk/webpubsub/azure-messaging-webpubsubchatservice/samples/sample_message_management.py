# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import os

from azure.messaging.webpubsubchatservice import WebPubSubChatServiceClient
from azure.messaging.webpubsubchatservice.models import ChatMessageUpdate, MessageContent


def main():
    if not os.environ.get("WPS_CHAT_CONNECTION_STRING"):
        print("Set WPS_CHAT_CONNECTION_STRING to run this example.")
        return

    with WebPubSubChatServiceClient.from_connection_string(
        os.environ["WPS_CHAT_CONNECTION_STRING"],
        os.environ.get("WPS_CHAT_HUB", "test_hub"),
    ) as client:
        conversation_id = "<conversation-id>"
        message_id = "<message-id>"
        client.update_message(
            conversation_id,
            message_id,
            ChatMessageUpdate(
                content=MessageContent(text="Updated message"),
            ),
        )
        client.delete_message(conversation_id, message_id)


if __name__ == "__main__":
    main()
