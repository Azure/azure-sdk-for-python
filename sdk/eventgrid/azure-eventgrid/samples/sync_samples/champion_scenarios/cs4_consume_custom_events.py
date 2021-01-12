# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: cs4_consume_custom_events.py
DESCRIPTION:
    These samples demonstrate deserializing a custom event
USAGE:
    python cs4_consume_custom_events.py
"""
import os
import json
from azure.eventgrid import EventGridConsumer

consumer = EventGridConsumer()
path = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "./cs4_event_grid_event_custom_event.json"))

with open(path, 'r') as f:
    eg_event_received_message = json.loads(f.read())

# returns List[DeserializedEvent]
event = consumer.decode_eventgrid_event(eg_event_received_message)

# returns { "itemSku": "Contoso Item SKU #1" }
data_dict = event.data
print(data_dict)
