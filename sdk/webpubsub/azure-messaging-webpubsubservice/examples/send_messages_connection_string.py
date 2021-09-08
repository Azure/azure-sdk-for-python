import io
import logging
import os

from azure.messaging.webpubsubservice import WebPubSubServiceClient

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger()

try:
    connection_string = os.environ['WEBPUBSUB_CONNECTION_STRING']
except KeyError:
    LOG.error("Missing environment variable 'WEBPUBSUB_CONNECTION_STRING' - please set if before running the example")
    exit()

# Build a client from the connection string. And for this example, we have enabled debug
# tracing. For production code, this should be turned off. 
client = WebPubSubServiceClient.from_connection_string(connection_string, logging_enable=True)

try:
    # Raise an exception if the service rejected the call
    client.web_pub_sub.send_to_all('Hub', message={'Hello': 'all!'})
    print('Successfully sent a JSON message')
except:
    print('Failed to send JSON message')

# Send a text message to everybody on the given hub...
try:
    # Raise an exception if the service rejected the call
    client.web_pub_sub.send_to_all('Hub', message='hello, text!', content_type='text/plain')
    print('Successfully sent a JSON message')
except:
    print('Failed to send JSON message')


# Send a json message from a stream to everybody on the given hub...
try:
    # Raise an exception if the service rejected the call
    client.web_pub_sub.send_to_all('Hub', message=io.BytesIO(b'{ "hello": "world" }'), content_type='application/json')
    print('Successfully sent a JSON message')
except:
    print('Failed to send JSON message')

