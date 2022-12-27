import os
import time
import json
from azure.webpubsub.client import WebPubSubClient, WebPubSubClientCredential
from azure.messaging.webpubsubservice import WebPubSubServiceClient
from azure.webpubsub.client import OnConnectedArgs, SendToGroupOptions, WebPubSubClientOptions
from dotenv import load_dotenv
import websocket

load_dotenv()


def on_connected(connected: OnConnectedArgs):
    print("===================")
    print(connected)


# def on_close()

service_client = WebPubSubServiceClient.from_connection_string(
    connection_string="Endpoint=http://localhost:8080;AccessKey=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ABCDEFGH;Version=1.0;", hub="Hub"
)

url = service_client.get_client_access_token(roles=["webpubsub.joinLeaveGroup", "webpubsub.sendToGroup"])["url"]
print(url)

# client = WebPubSubClient(client_access_url=url, options=WebPubSubClientOptions(auto_reconnect=False))
# client.on("connected", on_connected)
# client.start()
# client.join_group("test")
# client.leave_group("test3")
# client.stop()
# while True:
#     client.send_to_group(
#         group_name="test",
#         content="xxx",
#         data_type="text",
#         options=SendToGroupOptions(no_echo=False, fire_and_forget=True),
#     )
#     time.sleep(10)
# client.send_to_group(
#     group_name="test",
#     content="xxx",
#     data_type="text",
#     options=SendToGroupOptions(no_echo=False, fire_and_forget=True),
# )
# client._ws.send(json.dumps(message).encode())

ws = websocket.create_connection(url)
join_group = {"type": "joinGroup", "group": "test", "ackId": 99}
ws.send(json.dumps(join_group))
result = ws.recv()
print(result)
send_to_group = {"type": "sendToGroup", "group": "test", "data": "xxx", "ackId": 100}
ws.send(json.dumps(send_to_group))
result = ws.recv()
print(result)