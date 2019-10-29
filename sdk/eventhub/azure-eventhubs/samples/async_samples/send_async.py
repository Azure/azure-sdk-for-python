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
        ed = EventData("msg")
        await producer.send(ed)  # The event will be distributed to available partitions via round-robin.

        ed = EventData("msg sent to partition_id 0")
        await producer.send(ed, partition_id='0')  # Specifying partition_id

        ed = EventData("msg sent with partition_key")
        await producer.send(ed, partition_key="p_key")  # Specifying partition_key

        # Send a list of events
        event_list = []
        for i in range(1500):
            event_list.append(EventData('Hello World'))
        await producer.send(event_list)


loop = asyncio.get_event_loop()
producer = EventHubProducerClient.from_connection_string(conn_str=EVENT_HUB_CONNECTION_STR, event_hub_path=EVENT_HUB)
tasks = asyncio.gather(
    run(producer))
start_time = time.time()
loop.run_until_complete(tasks)
print("Send messages in {} seconds".format(time.time() - start_time))
