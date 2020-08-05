import os
import json
from azure.storage.queue import QueueServiceClient
from azure.eventgrid import EventGridConsumer, CloudEvent, EventGridEvent
from base64 import b64decode

connection_str = os.environ["STORAGE_QUEUE_CONN_STR"]
queue_service = QueueServiceClient.from_connection_string(conn_str=connection_str)

queue_client = queue_service.get_queue_client("egstoragequeue")
#queue_client.encode_message = False
consumer = EventGridConsumer()

msgs = queue_client.receive_messages()
i = 0
for msg in msgs:
    # receive single dict message
    deserialized_event = consumer.deserialize_event(b64decode(msg.content))
    if deserialized_event.model.__class__ == CloudEvent:
        dict_event = deserialized_event.to_json()
        print("event.type: {}\n".format(dict_event["type"]))
        print("event.to_json(): {}\n".format(dict_event))
        print("model: {}\n".format(deserialized_event.model))
        print("model.data: {}\n".format(deserialized_event.model.data))
    else:
        dict_event = deserialized_event.to_json()
        print("event.eventType: {}\n".format(dict_event["eventType"]))
        print("event.to_json(): {}\n".format(dict_event))
        print("model: {}\n".format(deserialized_event.model))
        print("model.data: {}\n".format(deserialized_event.model.data))

    i+=1

print("number of messages: {}".format(i))
