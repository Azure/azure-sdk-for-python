#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show sending individual events asynchronously to an Event Hub.
"""

# pylint: disable=C0111

import time
import asyncio
import os

from azure.eventhub.aio import EventHubClient
from azure.eventhub import EventData, EventHubSharedKeyCredential

HOSTNAME = os.environ['EVENT_HUB_HOSTNAME']  # <mynamespace>.servicebus.windows.net
EVENT_HUB = os.environ['EVENT_HUB_NAME']

USER = os.environ['EVENT_HUB_SAS_POLICY']
KEY = os.environ['EVENT_HUB_SAS_KEY']


async def run(client):
    producer = client.create_producer()
    await send(producer, 4)


async def send(producer, count):
    async with producer:
        for i in range(count):
            print("Sending message: {}".format(i))
            data = EventData(str(i))
            await producer.send(data)

loop = asyncio.get_event_loop()
client = EventHubClient(host=HOSTNAME, event_hub_path=EVENT_HUB, credential=EventHubSharedKeyCredential(USER, KEY),
                        network_tracing=False)
tasks = asyncio.gather(
    run(client),
    run(client))
start_time = time.time()
loop.run_until_complete(tasks)
print("Runtime: {} seconds".format(time.time() - start_time))
