# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import asyncio
import os


async def main():
    connection_string = os.environ.get("WPS_CHAT_CONNECTION_STRING")
    if not connection_string:
        print("Set WPS_CHAT_CONNECTION_STRING to run this sample.")
        return

    from azure.messaging.webpubsubservice.chat.aio import WebPubSubChatServiceClient

    client = WebPubSubChatServiceClient.from_connection_string(
        connection_string,
        os.environ.get("WPS_CHAT_HUB", "test_hub"),
    )
    try:
        access = await client.get_client_access_token(user_id="sample-user")
        print(access["url"])
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
