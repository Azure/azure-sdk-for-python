# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: consume_cloud_events_from_eventhub.py
DESCRIPTION:
    These samples demonstrate receiving events from a Storage Queue.
USAGE:
    python consume_cloud_events_from_eventhub.py
    Set the environment variables with your own values before running the sample:
    1) STORAGE_QUEUE_CONN_STR: The connection string to the storage account
    3) STORAGE_QUEUE_NAME: The name of the storage queue.
"""
import os
from azure.storage.queue import QueueServiceClient
from azure.eventgrid import EventGridConsumer, CloudEvent
from base64 import b64decode

connection_str = os.environ["STORAGE_QUEUE_CONN_STR"]
queue_name = os.environ["STORAGE_QUEUE_NAME"]
queue_service = QueueServiceClient.from_connection_string(conn_str=connection_str)

queue_client = queue_service.get_queue_client(queue_name)
consumer = EventGridConsumer()

msgs = queue_client.receive_messages()
for msg in msgs:
    # receive single dict message
    if 'specversion' in msg:
        deserialized_event = consumer.decode_cloud_event(b64decode(msg.content))
        dict_event = deserialized_event.to_json()
        print("event.type: {}\n".format(dict_event["type"]))
        print("event.to_json(): {}\n".format(dict_event))
        print("model: {}\n".format(deserialized_event.model))
        print("model.data: {}\n".format(deserialized_event.model.data))
    else:
        deserialized_event = consumer.decode_eventgrid_event(b64decode(msg.content))
        dict_event = deserialized_event.to_json()
        print("event.to_json(): {}\n".format(dict_event))
        print("model: {}\n".format(deserialized_event.model))
        print("model.data: {}\n".format(deserialized_event.model.data))
