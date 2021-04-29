import io
import logging
import os

from azure.messaging.webpubsubservice import WebPubSubServiceClient
from azure.messaging.webpubsubservice.rest import *

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger()

try:
    connection_string = os.environ['WEBPUBSUB_CONNECTION_STRING']
except KeyError:
    LOG.error("Missing environment variable 'WEBPUBSUB_CONNECTION_STRING' - please set if before running the example")
    exit()

# Build a client from the connection string. And for this example, we have enabled debug
# tracing. For production code, this should be turned off. 
client = WebPubSubServiceClient.from_connection_string(connection_string, tracing_enabled=True)

# Send a json message to everybody on the given hub...
request = build_send_to_all_request('myHub', json={ 'Hello': 'all!' })
print(request.headers)
response = client.send_request(request)
try:
    # Raise an exception if the service rejected the call
    response.raise_for_status()
    print('Successfully sent a JSON message')
except:
    print('Failed to send JSON message: {}'.format(response))


# Send a text message to everybody on the given hub...
request = build_send_to_all_request('ahub', content='hello, text!', content_type='text/plain')
response = client.send_request(request)
try:
    # Raise an exception if the service rejected the call
    response.raise_for_status()
    print('Successfully sent a TEXT message')
except:
    print('Failed to send TEXT message: {}'.format(response))



# Send a json message from a stream to everybody on the given hub...
request = build_send_to_all_request('ahub', content=io.BytesIO(b'{ "hello": "world" }'), content_type='application/json')
response = client.send_request(request)
try:
    # Raise an exception if the service rejected the call
    response.raise_for_status()
    print('Successfully sent a JSON message from a stream')
except:
    print('Failed to send JSON message from a stream: {}'.format(response))

