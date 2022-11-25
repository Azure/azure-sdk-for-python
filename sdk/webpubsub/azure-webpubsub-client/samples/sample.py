import time
from azure.webpubsub.client import WebPubSubClient, WebPubSubClientCredential
from azure.messaging.webpussubservice import WebPubSubServiceClient

service_client = WebPubSubServiceClient.from_connection_string(
    connection_string="", hub=""
)

url = service_client.get_client_access_token(
    roles=["webpubsub.joinLeaveGroup", "webpubsub.sendToGroup"]
)["url"]
print(url)
