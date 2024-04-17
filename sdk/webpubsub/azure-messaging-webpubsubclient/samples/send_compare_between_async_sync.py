# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import os
import time
import asyncio
from azure.messaging.webpubsubservice import WebPubSubServiceClient
from azure.messaging.webpubsubservice.aio import WebPubSubServiceClient as WebPubSubServiceClientAsync
from azure.messaging.webpubsubclient.aio import WebPubSubClient as AsyncClient
from azure.messaging.webpubsubclient.aio import WebPubSubClientCredential as WebPubSubClientCredentialAsync
from azure.messaging.webpubsubclient import WebPubSubClient as Client
from azure.messaging.webpubsubclient import WebPubSubClientCredential
from azure.messaging.webpubsubclient.models import WebPubSubDataType
from dotenv import load_dotenv

load_dotenv()

MESSAGE_COUNT = 100
TIME_COST = 0.0
TIME_COST_ASYNC = 0.0


def client_access_url_provider():
    service_client = WebPubSubServiceClient.from_connection_string( # type: ignore
        connection_string=os.getenv("WEBPUBSUB_CONNECTION_STRING", ""), hub="hub"
    )
    return service_client.get_client_access_token(
        roles=["webpubsub.joinLeaveGroup", "webpubsub.sendToGroup"]
    )["url"]

async def client_access_url_provider_async():
    service_client_async = WebPubSubServiceClientAsync.from_connection_string( # type: ignore
        connection_string=os.getenv("WEBPUBSUB_CONNECTION_STRING", ""), hub="hub"
    )
    return (await service_client_async.get_client_access_token(
        roles=["webpubsub.joinLeaveGroup", "webpubsub.sendToGroup"]
    ))["url"]


def send() -> None:
    global TIME_COST
    client = Client(
        credential=WebPubSubClientCredential(
            client_access_url_provider=client_access_url_provider
        ),
    )

    with client:
        group_name = "test"
        client.join_group(group_name)
        start = time.time()
        for i in range(MESSAGE_COUNT):
            client.send_to_group(group_name, {"hello": "json"}, WebPubSubDataType.JSON)
            print(f"send message {i} with Sync API ")
        TIME_COST = time.time() - start


async def send_item_async(client_async, idx):
    print(f"send message {idx} with Async API")
    await client_async.send_to_group("test", {"hello": "json"}, WebPubSubDataType.JSON)


async def send_async() -> None:
    global TIME_COST_ASYNC
    client_async = AsyncClient(
        credential=WebPubSubClientCredentialAsync(
            client_access_url_provider=client_access_url_provider_async
        ),
    )
    async with client_async:
        group_name = "send_compare_between_async_sync"
        await client_async.join_group(group_name)
        start = time.time()
        await asyncio.gather(
            *[send_item_async(client_async, i) for i in range(MESSAGE_COUNT)]
        )
        TIME_COST_ASYNC = time.time() - start


if __name__ == "__main__":
    send()
    asyncio.get_event_loop().run_until_complete(send_async())
    print(
        f"it takes {TIME_COST} seconds to send {MESSAGE_COUNT} messages with Sync API"
    )
    print(
        f"it takes {TIME_COST_ASYNC} seconds to send {MESSAGE_COUNT} messages with Async API"
    )
