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

from azure.eventhub import EventData, EventHubClient


logger = logging.getLogger('azure.eventhub')

iot_device_id = os.environ['IOTHUB_DEVICE']
iot_connection_str = os.environ['IOTHUB_CONNECTION_STR']

client = EventHubClient.from_connection_string(iot_connection_str, network_tracing=False)
try:
    producer = client.create_producer(operation='/messages/devicebound')
    with producer:
        producer.send(EventData(b"A single event", to_device=iot_device_id))

except KeyboardInterrupt:
    pass
