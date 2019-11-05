#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show running concurrent consumers.
"""

import os
import time
import asyncio

from azure.eventhub.aio import EventHubClient
from azure.eventhub import EventPosition, EventHubSharedKeyCredential

HOSTNAME = os.environ['EVENT_HUB_HOSTNAME']  # <mynamespace>.servicebus.windows.net
EVENT_HUB = os.environ['EVENT_HUB_NAME']
USER = os.environ['EVENT_HUB_SAS_POLICY']
KEY = os.environ['EVENT_HUB_SAS_KEY']

EVENT_POSITION = EventPosition("-1")


async def pump(client, partition):
    consumer = client.create_consumer(consumer_group="$default", partition_id=partition, event_position=EVENT_POSITION,
                                      prefetch=5, track_last_enqueued_event_properties=True)
    async with consumer:
        total = 0
        start_time = time.time()
        for event_data in await consumer.receive(timeout=10):
            last_offset = event_data.offset
            last_sn = event_data.sequence_number
            print("Received: {}, {}".format(last_offset, last_sn))
            total += 1
        end_time = time.time()
        run_time = end_time - start_time
        print("Consumer last enqueued event properties: {}.".format(consumer.last_enqueued_event_properties))
        print("Received {} messages in {} seconds".format(total, run_time))


loop = asyncio.get_event_loop()
client = EventHubClient(host=HOSTNAME, event_hub_path=EVENT_HUB, credential=EventHubSharedKeyCredential(USER, KEY),
                        network_tracing=False)
tasks = [asyncio.ensure_future(pump(client, "0"))]
loop.run_until_complete(asyncio.wait(tasks))
