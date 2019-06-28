#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show iterator consumer.
"""

import os
import time
import logging
import asyncio

from azure.eventhub.aio import EventHubClient
from azure.eventhub import EventPosition, EventHubSharedKeyCredential, EventData

import examples
logger = examples.get_logger(logging.INFO)


HOSTNAME = os.environ.get('EVENT_HUB_HOSTNAME')  # <mynamespace>.servicebus.windows.net
EVENT_HUB = os.environ.get('EVENT_HUB_NAME')

USER = os.environ.get('EVENT_HUB_SAS_POLICY')
KEY = os.environ.get('EVENT_HUB_SAS_KEY')

EVENT_POSITION = EventPosition("-1")


async def iter_consumer(consumer):
    async with consumer:
        async for item in consumer:
            print(item)


async def main():
    if not HOSTNAME:
        raise ValueError("No EventHubs URL supplied.")
    client = EventHubClient(host=HOSTNAME, event_hub_path=EVENT_HUB, credential=EventHubSharedKeyCredential(USER, KEY),
                            network_tracing=False)
    consumer = client.create_consumer(consumer_group="$default", partition_id="0", event_position=EVENT_POSITION)
    await iter_consumer(consumer)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

