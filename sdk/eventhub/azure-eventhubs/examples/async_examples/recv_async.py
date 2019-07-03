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
import logging
import asyncio

from azure.eventhub.aio import EventHubClient
from azure.eventhub import EventPosition, EventHubSharedKeyCredential

import examples
logger = examples.get_logger(logging.INFO)


HOSTNAME = os.environ.get('EVENT_HUB_HOSTNAME')  # <mynamespace>.servicebus.windows.net
EVENT_HUB = os.environ.get('EVENT_HUB_NAME')

USER = os.environ.get('EVENT_HUB_SAS_POLICY')
KEY = os.environ.get('EVENT_HUB_SAS_KEY')

EVENT_POSITION = EventPosition("-1")


async def pump(client, partition):
    consumer = client.create_consumer(consumer_group="$default", partition_id=partition, event_position=EVENT_POSITION, prefetch=5)
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
        print("Received {} messages in {} seconds".format(total, run_time))

try:
    if not HOSTNAME:
        raise ValueError("No EventHubs URL supplied.")

    loop = asyncio.get_event_loop()
    client = EventHubClient(host=HOSTNAME, event_hub_path=EVENT_HUB, credential=EventHubSharedKeyCredential(USER, KEY),
                            network_tracing=False)
    tasks = [
        asyncio.ensure_future(pump(client, "0")),
        asyncio.ensure_future(pump(client, "1"))]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

except KeyboardInterrupt:
    pass
