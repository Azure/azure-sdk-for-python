#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show receiving events from an Event Hub partition and processing
the event in on_event_data callback.

"""
import os
import logging

from azure.eventhub import EventHubClient, EventPosition, EventHubSharedKeyCredential

import examples
logger = examples.get_logger(logging.INFO)

HOSTNAME = os.environ.get('EVENT_HUB_HOSTNAME')  # <mynamespace>.servicebus.windows.net
EVENT_HUB = os.environ.get('EVENT_HUB_NAME')

USER = os.environ.get('EVENT_HUB_SAS_POLICY')
KEY = os.environ.get('EVENT_HUB_SAS_KEY')

EVENT_POSITION = EventPosition("-1")
PARTITION = "0"


total = 0
last_sn = -1
last_offset = "-1"
client = EventHubClient(host=HOSTNAME, event_hub_path=EVENT_HUB, credential=EventHubSharedKeyCredential(USER, KEY), network_tracing=False)

try:
    consumer = client.create_consumer(consumer_group="$default", partition_id=PARTITION, event_position=EVENT_POSITION, prefetch=100)
    with consumer:
        batched_events = consumer.receive(max_batch_size=10)
        for event_data in batched_events:
            last_offset = event_data.offset
            last_sn = event_data.sequence_number
            total += 1
            print("Partition {}, Received {}, sn={} offset={}".format(
                PARTITION,
                total,
                last_sn,
                last_offset))

except KeyboardInterrupt:
    pass
