# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import os
from azure.messaging.webpubsubclient import WebPubSubClient, WebPubSubClientCredential
from azure.messaging.webpubsubservice import WebPubSubServiceClient
from azure.messaging.webpubsubclient.models import (
    OnConnectedArgs,
    OnGroupDataMessageArgs,
    OnDisconnectedArgs,
    CallbackType,
    WebPubSubDataType,
)
from dotenv import load_dotenv

load_dotenv()


def on_connected(msg: OnConnectedArgs):
    print("======== connected ===========")
    print(f"Connection {msg.connection_id} is connected")


def on_disconnected(msg: OnDisconnectedArgs):
    print("========== disconnected =========")
    print(f"connection is disconnected: {msg.message}")


def on_group_message(msg: OnGroupDataMessageArgs):
    print("========== group message =========")
    if isinstance(msg.data, memoryview):
        print(f"Received message from {msg.group}: {bytes(msg.data).decode()}")
    else:
        print(f"Received message from {msg.group}: {msg.data}")


def main():
    service_client = WebPubSubServiceClient.from_connection_string( # type: ignore
        connection_string=os.getenv("WEBPUBSUB_CONNECTION_STRING", ""), hub="hub"
    )
    client = WebPubSubClient(
        credential=WebPubSubClientCredential(
            client_access_url_provider=lambda: service_client.get_client_access_token(
                roles=["webpubsub.joinLeaveGroup", "webpubsub.sendToGroup"]
            )["url"]
        ),
    )

    with client:
        client.subscribe(CallbackType.CONNECTED, on_connected)
        client.subscribe(CallbackType.DISCONNECTED, on_disconnected)
        client.subscribe(CallbackType.GROUP_MESSAGE, on_group_message)
        group_name = "hello_world"
        client.join_group(group_name)
        client.send_to_group(group_name, "hello text", WebPubSubDataType.TEXT, no_echo=False, ack=False)
        client.send_to_group(group_name, {"hello": "json"}, WebPubSubDataType.JSON)
        client.send_to_group(group_name, "hello text", WebPubSubDataType.TEXT)
        content = memoryview("hello binary".encode())
        client.send_to_group(group_name, content, WebPubSubDataType.BINARY)

    # If you can't run client in context, please open/close client manually like:
    # client.open()
    # ...
    # client.close()


if __name__ == "__main__":
    main()
