from azure.eventgrid import CloudEvent
from azure.storage.queue import QueueServiceClient, BinaryBase64DecodePolicy
import os
import json
from base64 import b64decode

# all types of CloudEvents below produce same DeserializedEvent
connection_str = os.environ['STORAGE_QUEUE_CONN_STR']
queue_name = os.environ['STORAGE_QUEUE_NAME']

with QueueServiceClient.from_connection_string(connection_str) as qsc:
    payload =  qsc.get_queue_client(
        queue=queue_name,
        message_decode_policy=BinaryBase64DecodePolicy()
        ).peek_messages()

    ## deserialize payload into a lost of typed Events
    events = [CloudEvent(**json.loads(msg.content)) for msg in payload]

    for event in events:
        print(type(event)) ## CloudEvent
