import os
from azure.webpubsub.client import WebPubSubClient
from azure.messaging.webpubsubservice import WebPubSubServiceClient
from azure.webpubsub.client import (
    OnConnectedArgs,
    OnGroupDataMessageArgs,
    OnDisconnectedArgs,
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
    if isinstance(msg.message.data, memoryview):
        print(f"Received message from {msg.message.group}: {bytes(msg.message.data).decode()}")
    else:
        print(f"Received message from {msg.message.group}: {msg.message.data}")


service_client = WebPubSubServiceClient.from_connection_string(
    connection_string=os.getenv("WEBPUBSUB_CONNECTION_STRING"), hub="hub"
)
url = service_client.get_client_access_token(roles=["webpubsub.joinLeaveGroup", "webpubsub.sendToGroup"])["url"]
print(url)

client = WebPubSubClient(credential=url, auto_reconnect=False)
client.on("connected", on_connected)
client.on("disconnected", on_disconnected)
client.on("group-message", on_group_message)

client.start()
group_name = "test"
client.join_group(group_name)
client.send_to_group(group_name, "hello text", "text", no_echo=False, fire_and_forget=False)
client.send_to_group(group_name, {"hello": "json"}, "json")
client.send_to_group(group_name, "hello json", "json")
content = memoryview("hello binary".encode())
client.send_to_group(group_name, content, "binary")
client.stop()
