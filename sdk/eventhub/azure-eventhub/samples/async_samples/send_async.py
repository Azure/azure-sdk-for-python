#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Examples to show sending events with different options to an Event Hub asynchronously.
"""

import time
import asyncio
import os

from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub.exceptions import EventHubError
from azure.eventhub import EventData

CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']


async def send_event_data_batch(producer):
    # Without specifying partition_id or partition_key
    # the events will be distributed to available partitions via round-robin.
    event_data_batch = await producer.create_batch()
    event_data_batch.add(EventData('Single message'))
    await producer.send_batch(event_data_batch)


async def send_event_data_batch_with_limited_size(producer):
    # Without specifying partition_id or partition_key
    # the events will be distributed to available partitions via round-robin.
    event_data_batch_with_limited_size = await producer.create_batch(max_size_in_bytes=1000)

    while True:
        try:
            event_data_batch_with_limited_size.add(EventData('Message inside EventBatchData'))
        except ValueError:
            # EventDataBatch object reaches max_size.
            # New EventDataBatch object can be created here to send more data.
            break

    await producer.send_batch(event_data_batch_with_limited_size)


async def send_event_data_batch_with_partition_key(producer):
    # Specifying partition_key
    event_data_batch_with_partition_key = await producer.create_batch(partition_key='pkey')
    event_data_batch_with_partition_key.add(EventData('Message will be sent to a partition determined by the partition key'))

    await producer.send_batch(event_data_batch_with_partition_key)


async def send_event_data_batch_with_partition_id(producer):
    # Specifying partition_id.
    event_data_batch_with_partition_id = await producer.create_batch(partition_id='0')
    event_data_batch_with_partition_id.add(EventData('Message will be sent to target-id partition'))

    await producer.send_batch(event_data_batch_with_partition_id)


async def send_event_data_batch_with_properties(producer):
    event_data_batch = await producer.create_batch()
    event_data = EventData('Message with properties')
    event_data.properties = {'prop_key': 'prop_value'}
    event_data_batch.add(event_data)
    await producer.send_batch(event_data_batch)


async def send_event_data_list(producer):
    # If you know beforehand that the list of events you have will not exceed the
    # size limits, you can use the `send_batch()` api directly without creating an EventDataBatch

    # Without specifying partition_id or partition_key
    # the events will be distributed to available partitions via round-robin.

    event_data_list = [EventData('Event Data {}'.format(i)) for i in range(10)]
    try:
        await producer.send_batch(event_data_list)
    except ValueError:  # Size exceeds limit. This shouldn't happen if you make sure before hand.
        print("Size of the event data list exceeds the size limit of a single send")
    except EventHubError as eh_err:
        print("Sending error: ", eh_err)


async def run():

    producer = EventHubProducerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        eventhub_name=EVENTHUB_NAME
    )
    async with producer:
        await send_event_data_batch(producer)
        await send_event_data_batch_with_limited_size(producer)
        await send_event_data_batch_with_partition_key(producer)
        await send_event_data_batch_with_partition_id(producer)
        await send_event_data_batch_with_properties(producer)
        await send_event_data_list(producer)


start_time = time.time()
asyncio.run(run())
print("Send messages in {} seconds.".format(time.time() - start_time))
