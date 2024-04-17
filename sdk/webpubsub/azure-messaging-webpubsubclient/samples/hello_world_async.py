# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import os
import asyncio
from azure.messaging.webpubsubclient.aio import WebPubSubClient, WebPubSubClientCredential
from azure.messaging.webpubsubservice.aio import WebPubSubServiceClient
from azure.messaging.webpubsubclient.models import (
    OnConnectedArgs,
    OnGroupDataMessageArgs,
    OnDisconnectedArgs,
    CallbackType,
    WebPubSubDataType,
)
from dotenv import load_dotenv

load_dotenv()


async def on_connected(msg: OnConnectedArgs):
    print("======== connected ===========")
    print(f"Connection {msg.connection_id} is connected")


async def on_disconnected(msg: OnDisconnectedArgs):
    print("========== disconnected =========")
    print(f"connection is disconnected: {msg.message}")


async def on_group_message(msg: OnGroupDataMessageArgs):
    print("========== group message =========")
    if isinstance(msg.data, memoryview):
        print(f"Received message from {msg.group}: {bytes(msg.data).decode()}")
    else:
        print(f"Received message from {msg.group}: {msg.data}")


async def main():
    service_client = WebPubSubServiceClient.from_connection_string(  # type: ignore
        connection_string=os.getenv("WEBPUBSUB_CONNECTION_STRING", ""), hub="hub"
    )
    async def client_access_url_provider():
        return (await service_client.get_client_access_token(
            roles=["webpubsub.joinLeaveGroup", "webpubsub.sendToGroup"]
        ))["url"]
    client = WebPubSubClient(
        credential=WebPubSubClientCredential(client_access_url_provider=client_access_url_provider),
    )

    async with client:
        await client.subscribe(CallbackType.CONNECTED, on_connected)
        await client.subscribe(CallbackType.DISCONNECTED, on_disconnected)
        await client.subscribe(CallbackType.GROUP_MESSAGE, on_group_message)
        group_name = "hello_world_async"
        await client.join_group(group_name)
        await client.send_to_group(
            group_name, "hello text", WebPubSubDataType.TEXT, no_echo=False, ack=False
        )
        await client.send_to_group(group_name, {"hello": "json"}, WebPubSubDataType.JSON)
        await client.send_to_group(group_name, "hello text", WebPubSubDataType.TEXT)
        content = memoryview("hello binary".encode())
        await client.send_to_group(group_name, content, WebPubSubDataType.BINARY)

    # If you can't run client in context, please open/close client manually like:
    # await client.open()
    # ...
    # await client.close()


if __name__ == "__main__":
    asyncio.run(main())
