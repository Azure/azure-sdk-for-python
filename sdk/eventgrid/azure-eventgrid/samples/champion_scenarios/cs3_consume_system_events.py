# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: cs3_consume_system_events.py
DESCRIPTION:
    These samples demonstrate deserializing a message from system event.
USAGE:
    python cs3_consume_system_events.py
"""
import os
import json
from azure.eventgrid import EventGridDeserializer

consumer = EventGridDeserializer()
path = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./cs3_system_event.json"))

with open(path, 'r') as f:
    eg_event_received_message = json.loads(f.read())
# returns List[DeserializedEvent]
event = consumer.deserialize_eventgrid_events(eg_event_received_message)

datetime_object = event.event_time
print(datetime_object)

storage_blobcreated_object = event.data
print(storage_blobcreated_object)
