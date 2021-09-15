import io
import logging
import os

from azure.messaging.webpubsubservice import WebPubSubServiceClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger()

# Set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:
# AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, WEBPUBSUB_ENDPOINT
try:
    endpoint = os.environ.get("WEBPUBSUB_ENDPOINT")
except KeyError:
    LOG.error("Missing environment variable 'WEBPUBSUB_ENDPOINT' - please set if before running the example")
    exit()

# Build a client from the connection string. And for this example, we have enabled debug
# tracing. For production code, this should be turned off.
client = WebPubSubServiceClient(credential=DefaultAzureCredential(), endpoint=endpoint)

# Send a json message to everybody on the given hub...
try:
    # Raise an exception if the service rejected the call
    client.web_pub_sub.send_to_all('Hub', message={'Hello': 'all!'})
    print('Successfully sent a JSON message')
except HttpResponseError as e:
    print('Failed to send JSON message: {}'.format(e.response.json()))

# Send a text message to everybody on the given hub...
try:
    # Raise an exception if the service rejected the call
    client.web_pub_sub.send_to_all('Hub', message='hello, text!', content_type='text/plain')
    print('Successfully sent a text message')
except HttpResponseError as e:
    print('Failed to send text message: {}'.format(e.response.json()))


# Send a json message from a stream to everybody on the given hub...
try:
    # Raise an exception if the service rejected the call
    client.web_pub_sub.send_to_all('Hub', message=io.BytesIO(b'{ "hello": "world" }'), content_type='application/json')
    print('Successfully sent a JSON message')
except HttpResponseError as e:
    print('Failed to send JSON message: {}'.format(e.response.json()))

