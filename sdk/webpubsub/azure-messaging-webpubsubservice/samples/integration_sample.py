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
import os
import json
from azure.messaging.webpubsubservice import WebPubSubServiceClient


LOG = logging.getLogger()
WEBSOCKET_N = 3

try:
    connection_string = os.environ['WEBPUBSUB_CONNECTION_STRING']
except KeyError:
    LOG.error("Missing environment variable 'WEBPUBSUB_CONNECTION_STRING' - please set if before running the example")
    exit()

# Build a client from the connection string. And for this example, we have enabled debug
# tracing. For production code, this should be turned off.
service = WebPubSubServiceClient.from_connection_string(connection_string, hub='hub', logging_enable=False)
recv_messages = []
connection_ids = []

def on_message(websocket_app, message): 
    message = json.loads(message)

    if message["type"] == "message":
        recv_messages.append(message["data"])

    if message["type"] == "system" and message["event"] == "connected":
        connection_ids.append(message["connectionId"])

    print(message)

def on_open(websocket_app): print("connected")

# Build multiple websockets
for i in range(WEBSOCKET_N):
    token = service.get_client_access_token(groups=["InitGroup"], user_id="User%d" % i)    
    client = websocket.WebSocketApp(token["url"], subprotocols=['json.webpubsub.azure.v1'], on_open=on_open, on_message=on_message)
    wst = threading.Thread(target=client.run_forever, daemon=True)
    wst.start()

while len(connection_ids) != WEBSOCKET_N:
    pass

# test naive send_to_all
service.send_to_all(message='Message_For_All', content_type='text/plain') # WEBSOCKET_N messages

# test if generating token with the initial group is working
service.send_to_group(group="InitGroup", message='Message_For_InitGroup', content_type='text/plain') # WEBSOCKET_N messages

# test if parameter "filter" in send is working
service.send_to_all("Message_Not_For_User0", filter="userId ne 'User0'", content_type='text/plain') # (WEBSOCKET_N - 1) messages

# test if remove_connection_from_all_groups works
group_names = ["Group%d" % i for i in range(3)]
for group in group_names:
    service.add_connection_to_group(group, connection_ids[0])
    service.send_to_group(group, "Message_For_RemoveFromAll", content_type='text/plain')  

service.remove_connection_from_all_groups(connection_ids[0])

for group in group_names:
    service.send_to_group(group, "Message_For_RemoveFromAll", content_type='text/plain')

# other tests
service.send_to_user("User0", message='Message_For_User0', content_type='text/plain') # 1 messages

time.sleep(5)

print("Received Message =", recv_messages)
assert service.group_exists("InitGroup") == True
assert recv_messages.count("Message_For_All") == WEBSOCKET_N
assert recv_messages.count("Message_For_InitGroup") == WEBSOCKET_N
assert recv_messages.count("Message_Not_For_User0") == WEBSOCKET_N - 1
assert recv_messages.count("Message_For_User0") == 1
assert recv_messages.count("Message_For_RemoveFromAll") == 3