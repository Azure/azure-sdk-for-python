import io
import logging
import os

from azure.messaging.webpubsubservice import WebPubSubServiceClient
from azure.core.exceptions import HttpResponseError

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger()

try:
    connection_string = os.environ['WEBPUBSUB_CONNECTION_STRING']
    revers_proxy_endpoint = os.environ.get("WEBPUBSUB_REVERSE_RPOXY_ENDPOINT")
except KeyError:
    LOG.error("Missing environment variable 'WEBPUBSUB_CONNECTION_STRING' or 'WEBPUBSUB_REVERSE_RPOXY_ENDPOINT' - please set if before running the example")
    exit()

# Build a client from the connection string. And for this example, we have enabled debug
# tracing. For production code, this should be turned off. 
client = WebPubSubServiceClient.from_connection_string(connection_string, logging_enable=True, revers_proxy_endpoint=revers_proxy_endpoint)

try:
    # Raise an exception if the service rejected the call
    client.web_pub_sub.send_to_all('Hub', message={'Hello': 'connection_string_reverse_proxy!'})
    print('Successfully sent a JSON message')
except HttpResponseError as e:
    print('Failed to send JSON message: {}'.format(e.response.json()))

# Send a text message to everybody on the given hub...
try:
    # Raise an exception if the service rejected the call
    client.web_pub_sub.send_to_all('Hub', message='hello, connection_string_reverse_proxy!', content_type='text/plain')
    print('Successfully sent a JSON message')
except HttpResponseError as e:
    print('Failed to send JSON message: {}'.format(e.response.json()))


# Send a json message from a stream to everybody on the given hub...
try:
    # Raise an exception if the service rejected the call
    client.web_pub_sub.send_to_all('Hub', message=io.BytesIO(b'{ "hello": "connection_string_reverse_proxy" }'), content_type='application/json')
    print('Successfully sent a JSON message')
except HttpResponseError as e:
    print('Failed to send JSON message: {}'.format(e.response.json()))

