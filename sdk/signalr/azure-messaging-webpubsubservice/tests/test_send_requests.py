from azure.messaging.webpubsubservice import WebPubSubServiceClient
from azure.messaging.webpubsubservice.rest import *

from azure.core.credentials import AzureKeyCredential


def test_prepare_request():
    request = prepare_send_to_all("hub", "hello world", content_type="text/plain")

    assert request.headers["content-type"] == "text/plain"
    assert request.content == "hello world"


def test_send_request():
    client = WebPubSubServiceClient(
        "https://www.microsoft.com/api", AzureKeyCredential("abcd")
    )
    request = prepare_send_to_all("hub", "hello world", content_type="text/plain")
    response = client.send_request(request)
