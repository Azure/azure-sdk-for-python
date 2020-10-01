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
from azure.eventgrid import EventGridConsumer

consumer = EventGridConsumer()

# returns List[DeserializedEvent]
deserialized_events = consumer.decode_eventgrid_event(service_bus_received_message)

# EventGridEvent schema, Storage.BlobCreated event
for event in deserialized_events:

    # both allow access to raw properties as strings
    time_string = event.event_time
    time_string = event["event_time"]

    # model returns EventGridEvent object
    event_grid_event = event.model

    # all model properties are strongly typed
    datetime_object = event.model.time
    storage_blobcreated_object = event.model.data
