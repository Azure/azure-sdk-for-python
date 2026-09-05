# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import asyncio
import os


async def main():
    required = ("WPS_CHAT_CONNECTION_STRING", "WPS_CHAT_CONVERSATION_ID")
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        print(f"Set {', '.join(missing)} to run this sample.")
        return

    from azure.messaging.webpubsubservice.chat.aio import WebPubSubChatServiceClient

    client = WebPubSubChatServiceClient.from_connection_string(
        os.environ["WPS_CHAT_CONNECTION_STRING"],
        os.environ.get("WPS_CHAT_HUB", "test_hub"),
    )
    try:
        async for message in client.list_messages(os.environ["WPS_CHAT_CONVERSATION_ID"]):
            print(message.id, message.created_by, message.content.text)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
