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
from azure.eventgrid import EventGridConsumer

consumer = EventGridConsumer()

# returns List[DeserializedEvent]
deserialized_events = consumer.decode_eventgrid_event(service_bus_received_message)

# CloudEvent schema
for event in deserialized_events:

    # both allow access to raw properties as strings
    time_string = event.time
    time_string = event["time"]

    # model returns CloudEvent object
    cloud_event = event.model

    # all model properties are strongly typed
    datetime_object = event.model.time
    storage_blobcreated_object = event.model.data