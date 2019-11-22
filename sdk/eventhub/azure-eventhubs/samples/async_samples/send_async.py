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
from azure.eventhub import EventData, EventDataBatch

EVENT_HUB_CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']


async def run(producer):

    async with producer:

        # Without specifying partition_id or partition_key
        # The events will be distributed to available partitions via round-robin.
        event_data_batch = await producer.create_batch(max_size_in_bytes=10000)

        # Specifying partition_id
        # event_data_batch = producer.create_batch(partition_id='0')

        # Specifying partition_key
        # event_data_batch = producer.create_batch(partition_key='pkey')

        while True:
            try:
                event_data_batch.add(EventData('Message inside EventBatchData'))
            except ValueError:
                # EventDataBatch object reaches max_size.
                # New EventDataBatch object can be created here to send more data
                break

        await producer.send_batch(event_data_batch)


loop = asyncio.get_event_loop()
producer = EventHubProducerClient.from_connection_string(conn_str=EVENT_HUB_CONNECTION_STR, eventhub_name=EVENTHUB_NAME)
tasks = asyncio.gather(
    run(producer))
start_time = time.time()
loop.run_until_complete(tasks)
print("Send messages in {} seconds".format(time.time() - start_time))
