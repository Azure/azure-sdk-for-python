import os
import json
from base64 import b64decode
from azure.storage.queue import QueueServiceClient, BinaryBase64DecodePolicy
from azure.eventgrid import EventGridConsumer, CloudEvent, EventGridEvent

def get_deserialized_events(dict_events):
    events = consumer.deserialize_events(dict_events)
    for event in events:
        print(event)
        print(event.data.__class__)
        #if event.model.__class__ == CloudEvent:
        #    print("model: {}".format(event.model))

connection_str = os.environ["STORAGE_QUEUE_CONN_STR"]
queue_service = QueueServiceClient.from_connection_string(conn_str=connection_str)

queue_client = queue_service.get_queue_client("egstoragequeue")
#queue_client.message_decoding_policy = BinaryBase64DecodePolicy
consumer = EventGridConsumer()

msgs = queue_client.receive_messages()
i = 0
for msg in msgs:
    # receive single dict message
    decoded_content = b64decode(msg.content)
    dict_events = json.loads(decoded_content)
    get_deserialized_events(dict_events)
    i+=1

print("number of messages: {}".format(i))
