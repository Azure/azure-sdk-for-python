# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: cs6_consume_events_using_cloud_events_1.0_schema.py
DESCRIPTION:
    These samples demonstrate creating a list of CloudEvents and sending then as a list.
USAGE:
    python cs6_consume_events_using_cloud_events_1.0_schema.py
"""
import os
import json
from azure.eventgrid import EventGridConsumer

consumer = EventGridConsumer()

with open('./cs6_cloud_event_system_event.json', 'r') as f:
    cloud_event_received_message = json.loads(f.read())

# returns List[DeserializedEvent]
event = consumer.decode_cloud_event(cloud_event_received_message)

datetime_object = event.time
print(datetime_object)

storage_blobcreated_object = event.data
print(storage_blobcreated_object)
