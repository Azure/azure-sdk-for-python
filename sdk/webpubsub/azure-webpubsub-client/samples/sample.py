import os
import time
from azure.webpubsub.client import WebPubSubClient, WebPubSubClientCredential
from azure.messaging.webpubsubservice import WebPubSubServiceClient
from azure.webpubsub.client import OnConnectedArgs
from dotenv import load_dotenv

load_dotenv()


def on_connected(connected: OnConnectedArgs):
    print("===================")
    print(connected)


service_client = WebPubSubServiceClient.from_connection_string(
    connection_string=os.getenv("WEBPUBSUB_CONNECTION_STRING"), hub="Hub"
)

url = service_client.get_client_access_token(
    roles=["webpubsub.joinLeaveGroup", "webpubsub.sendToGroup"]
)["url"]
print(url)

client = WebPubSubClient(client_access_url=url)
client.on("connected", on_connected)
client.start()
# client.join_group("test")
# client.leave_group("test3")
client.stop()
