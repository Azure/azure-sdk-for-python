#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show receiving events from an IoT Hub partition.
"""
import os
import logging

from azure.eventhub import EventHubClient, EventPosition


logger = logging.getLogger('azure.eventhub')

iot_connection_str = os.environ['IOTHUB_CONNECTION_STR']

client = EventHubClient.from_connection_string(iot_connection_str, network_tracing=False)
consumer = client.create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition("-1"), operation='/messages/events')
with consumer:
    received = consumer.receive(timeout=5)
    print(received)

    eh_info = client.get_properties()
    print(eh_info)
