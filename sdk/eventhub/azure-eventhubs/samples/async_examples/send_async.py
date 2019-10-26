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

from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub import EventData

EVENT_HUB_CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
EVENT_HUB = os.environ['EVENT_HUB_NAME']


async def run(producer):
    async with producer:
        for i in range(5):
            print("Sending message: {}".format(i))
            data = EventData(str(i))
            await producer.send(data)


loop = asyncio.get_event_loop()
producer = EventHubProducerClient.from_connection_string(conn_str=EVENT_HUB_CONNECTION_STR, event_hub_path=EVENT_HUB)
tasks = asyncio.gather(
    run(producer))
start_time = time.time()
loop.run_until_complete(tasks)
print("Runtime: {} seconds".format(time.time() - start_time))
