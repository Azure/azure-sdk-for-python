#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show creating and sending EventBatchData within limited size.
"""

# pylint: disable=C0111

import time
import os
import asyncio

from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub import EventData


EVENT_HUB_CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']


async def create_batch_data(producer_client):
    batch_data = await producer_client.create_batch(max_size=10000)
    while True:
        try:
            batch_data.try_add(EventData('Message inside EventBatchData'))
        except ValueError:
            # EventDataBatch object reaches max_size.
            # New EventDataBatch object can be created here to send more data
            break
    return batch_data


async def run(producer):
    data_batch = await create_batch_data(producer)
    async with producer:
        await producer.send(data_batch)


loop = asyncio.get_event_loop()
producer = EventHubProducerClient.from_connection_string(conn_str=EVENT_HUB_CONNECTION_STR, eventhub_name=EVENTHUB_NAME)
tasks = asyncio.gather(
    run(producer))
start_time = time.time()
loop.run_until_complete(tasks)
print("Send messages in {} seconds".format(time.time() - start_time))
