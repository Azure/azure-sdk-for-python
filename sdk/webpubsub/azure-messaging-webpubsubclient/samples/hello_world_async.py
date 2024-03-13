# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import os
import asyncio
from azure.messaging.webpubsubclient.aio import WebPubSubClient
from azure.messaging.webpubsubclient import WebPubSubClientCredential
from azure.messaging.webpubsubservice import WebPubSubServiceClient
from azure.messaging.webpubsubclient.models import (
    OnConnectedArgs,
    OnGroupDataMessageArgs,
    OnDisconnectedArgs,
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
    service_client = WebPubSubServiceClient.from_connection_string(
        connection_string=os.getenv("WEBPUBSUB_CONNECTION_STRING", ""), hub="hub"
    )
    client = WebPubSubClient(
        credential=WebPubSubClientCredential(
            client_access_url_provider=lambda: service_client.get_client_access_token(
                roles=["webpubsub.joinLeaveGroup", "webpubsub.sendToGroup"]
            )["url"]
        ),
    )

    async with client:
        await client.subscribe("connected", on_connected)
        await client.subscribe("disconnected", on_disconnected)
        await client.subscribe("group-message", on_group_message)
        group_name = "test"
        await client.join_group(group_name)
        await client.send_to_group(
            group_name, "hello text", "text", no_echo=False, ack=False
        )
        await client.send_to_group(group_name, {"hello": "json"}, "json")
        await client.send_to_group(group_name, "hello json", "json")
        content = memoryview("hello binary".encode())
        await client.send_to_group(group_name, content, "binary")

    # If you can't run client in context, please open/close client manually like:
    # await client.open()
    # ...
    # await client.close()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
    # asyncio.run(main())
