#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show receiving events from an Event Hub partition as an epoch consumer.
"""

import os
import time
import asyncio

from azure.eventhub.aio import EventHubClient
from azure.eventhub import EventHubSharedKeyCredential, EventPosition

HOSTNAME = os.environ['EVENT_HUB_HOSTNAME']  # <mynamespace>.servicebus.windows.net
EVENT_HUB = os.environ['EVENT_HUB_NAME']

USER = os.environ['EVENT_HUB_SAS_POLICY']
KEY = os.environ['EVENT_HUB_SAS_KEY']

PARTITION = "0"


async def pump(client, owner_level):
    consumer = client.create_consumer(
        consumer_group="$default", partition_id=PARTITION, event_position=EventPosition("-1"), owner_level=owner_level
    )
    async with consumer:
        total = 0
        start_time = time.time()
        for event_data in await consumer.receive(timeout=5):
            last_offset = event_data.offset
            last_sn = event_data.sequence_number
            print("Received: {}, {}".format(last_offset, last_sn))
            total += 1
        end_time = time.time()
        run_time = end_time - start_time
        print("Received {} messages in {} seconds".format(total, run_time))

loop = asyncio.get_event_loop()
client = EventHubClient(host=HOSTNAME, event_hub_path=EVENT_HUB, credential=EventHubSharedKeyCredential(USER, KEY),
                        network_tracing=False)
loop.run_until_complete(pump(client, 20))
