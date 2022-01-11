# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: consume_cloud_events_from_service_bus_queue.py
DESCRIPTION:
    These samples demonstrate receiving events from Service Bus.
USAGE:
    python consume_cloud_events_from_service_bus_queue.py
    Set the environment variables with your own values before running the sample:
    1) SB_CONN_STR: The connection string to the Service Bus account
    3) SERVICE_BUS_QUEUE_NAME: The name of the servicebus account
"""

# Note: This sample would not work on pypy since azure-servicebus
# depends on uamqp which is not pypy compatible.

from azure.eventgrid import EventGridEvent
from azure.servicebus import ServiceBusClient
import os
import json

# all types of EventGridEvents below produce same DeserializedEvent
connection_str = os.environ['SERVICE_BUS_CONNECTION_STR']
queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']

with ServiceBusClient.from_connection_string(connection_str) as sb_client:
    payload =  sb_client.get_queue_receiver(queue_name).receive_messages()

    ## deserialize payload into a list of typed Events
    events = [EventGridEvent.from_json(msg) for msg in payload]

    for event in events:
        print(type(event)) ## EventGridEvent
