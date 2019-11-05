#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show receiving events from an Event Hub partition.
"""
import os
import time
from azure.eventhub import EventHubClient, EventPosition, EventHubSharedKeyCredential

HOSTNAME = os.environ['EVENT_HUB_HOSTNAME']  # <mynamespace>.servicebus.windows.net
EVENT_HUB = os.environ['EVENT_HUB_NAME']

USER = os.environ['EVENT_HUB_SAS_POLICY']
KEY = os.environ['EVENT_HUB_SAS_KEY']

EVENT_POSITION = EventPosition("-1")
PARTITION = "0"


total = 0
last_sn = -1
last_offset = "-1"
client = EventHubClient(host=HOSTNAME, event_hub_path=EVENT_HUB, credential=EventHubSharedKeyCredential(USER, KEY),
                        network_tracing=False)

consumer = client.create_consumer(consumer_group="$default", partition_id=PARTITION,
                                  event_position=EVENT_POSITION, prefetch=5000,
                                  track_last_enqueued_event_properties=True)
with consumer:
    start_time = time.time()
    batch = consumer.receive(timeout=5)
    for event_data in batch:
        last_offset = event_data.offset
        last_sn = event_data.sequence_number
        print("Received: {}, {}".format(last_offset, last_sn))
        print(event_data.body_as_str())
        total += 1
    batch = consumer.receive(timeout=5)
    print("Consumer last enqueued event properties: {}.".format(consumer.last_enqueued_event_properties))
    print("Received {} messages in {} seconds".format(total, time.time() - start_time))
