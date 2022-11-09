# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import threading
import logging
import websocket
import time
import sys

from azure.messaging.webpubsubservice import WebPubSubServiceClient
from azure.core.exceptions import HttpResponseError

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger()
websocket.enableTrace(True)
WEBSOCKET_N = 1

try:
    connection_string = os.environ['WEBPUBSUB_CONNECTION_STRING']
except KeyError:
    LOG.error("Missing environment variable 'WEBPUBSUB_CONNECTION_STRING' - please set if before running the example")
    exit()

# Build a client from the connection string. And for this example, we have enabled debug
# tracing. For production code, this should be turned off.
service = WebPubSubServiceClient.from_connection_string(connection_string, hub='hub', logging_enable=True)
recv_messages = []

def on_message(wsapp, message): recv_messages.append(message)
def on_open(wsapp): print("connected")

# Build multiple websockets
for i in range(WEBSOCKET_N):
    token = service.get_client_access_token(groups=["InitGroup"], user_id="user%d" % i)    
    client = websocket.WebSocketApp(token["url"], on_open=on_open, on_message=on_message)
    wst = threading.Thread(target=client.run_forever, daemon=True)
    wst.start()

try:
    # test naive send_to_all
    service.send_to_all(message='Message_For_All', content_type='text/plain') # WEBSOCKET_N messages

    # test if generating token with the initial group is working
    service.send_to_group(group="InitGroup", message='Message_For_InitGroup', content_type='text/plain') # WEBSOCKET_N messages

    # test if parameter "filter" in send is working
    service.send_to_all("Message_Not_For_user0", filter="userId ne 'user0'", content_type='text/plain') # (WEBSOCKET_N - 1) messages

    # other tests
    service.send_to_user("user1", message='Message_For_user0', content_type='text/plain') # 1 messages

except HttpResponseError as e:
    print('Failed to send JSON message: {}'.format(e.response.json()))

time.sleep(1)

print("Recevied Message =", recv_messages)
assert service.group_exists("InitGroup") == True
assert recv_messages.count("Message_For_All") == WEBSOCKET_N
assert recv_messages.count("Message_For_InitGroup") == WEBSOCKET_N
assert recv_messages.count("Message_Not_For_user0") == WEBSOCKET_N - 1
assert recv_messages.count("Message_For_user0") == 1