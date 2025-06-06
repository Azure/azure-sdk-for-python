#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Examples to show sending events with different options to an Event Hub asynchronously.

WARNING: EventHubProducerClient and EventDataBatch are not coroutine-safe!
Do not share these instances between coroutines without proper synchronization.
If you need to send from multiple coroutines, create separate client instances
or use proper synchronization mechanisms like asyncio.Lock.
"""

import time
import asyncio
import os

from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub.exceptions import EventHubError
from azure.eventhub import EventData
from azure.identity.aio import DefaultAzureCredential

FULLY_QUALIFIED_NAMESPACE = os.environ["EVENT_HUB_HOSTNAME"]
EVENTHUB_NAME = os.environ["EVENT_HUB_NAME"]


async def send_event_data_batch(producer):
    # Without specifying partition_id or partition_key
    # the events will be distributed to available partitions via round-robin.
    event_data_batch = await producer.create_batch()
    event_data_batch.add(EventData("Single message"))
    await producer.send_batch(event_data_batch)


async def send_event_data_batch_with_limited_size(producer):
    # Without specifying partition_id or partition_key
    # the events will be distributed to available partitions via round-robin.
    event_data_batch_with_limited_size = await producer.create_batch(max_size_in_bytes=1000)

    while True:
        try:
            event_data_batch_with_limited_size.add(EventData("Message inside EventBatchData"))
        except ValueError:
            # EventDataBatch object reaches max_size.
            # New EventDataBatch object can be created here to send more data.
            break

    await producer.send_batch(event_data_batch_with_limited_size)


async def send_event_data_batch_with_partition_key(producer):
    # Specifying partition_key
    event_data_batch_with_partition_key = await producer.create_batch(partition_key="pkey")
    event_data_batch_with_partition_key.add(
        EventData("Message will be sent to a partition determined by the partition key")
    )

    await producer.send_batch(event_data_batch_with_partition_key)


async def send_event_data_batch_with_partition_id(producer):
    # Specifying partition_id.
    event_data_batch_with_partition_id = await producer.create_batch(partition_id="0")
    event_data_batch_with_partition_id.add(EventData("Message will be sent to target-id partition"))

    await producer.send_batch(event_data_batch_with_partition_id)


async def send_event_data_batch_with_properties(producer):
    event_data_batch = await producer.create_batch()
    event_data = EventData("Message with properties")
    event_data.properties = {"prop_key": "prop_value"}
    event_data_batch.add(event_data)
    await producer.send_batch(event_data_batch)


async def send_event_data_list(producer):
    # If you know beforehand that the list of events you have will not exceed the
    # size limits, you can use the `send_batch()` api directly without creating an EventDataBatch

    # Without specifying partition_id or partition_key
    # the events will be distributed to available partitions via round-robin.

    event_data_list = [EventData("Event Data {}".format(i)) for i in range(10)]
    try:
        await producer.send_batch(event_data_list)
    except ValueError:  # Size exceeds limit. This shouldn't happen if you make sure before hand.
        print("Size of the event data list exceeds the size limit of a single send")
    except EventHubError as eh_err:
        print("Sending error: ", eh_err)


async def send_concurrent_with_separate_producers():
    """
    Example showing coroutine-safe concurrent sending using separate producers.
    WARNING: Do NOT share EventHubProducerClient instances between coroutines!
    """
    async def send_from_coroutine(task_id):
        # Create a separate producer for each coroutine - clients are NOT coroutine-safe
        producer = EventHubProducerClient(
            fully_qualified_namespace=FULLY_QUALIFIED_NAMESPACE,
            eventhub_name=EVENTHUB_NAME,
            credential=DefaultAzureCredential(),
        )
        try:
            async with producer:
                batch = await producer.create_batch()
                batch.add(EventData(f"Message from coroutine {task_id}"))
                await producer.send_batch(batch)
                print(f"Coroutine {task_id} sent message successfully")
        except Exception as e:
            print(f"Coroutine {task_id} failed: {e}")

    # Use asyncio.gather to run coroutines concurrently
    await asyncio.gather(*[send_from_coroutine(i) for i in range(3)])


async def send_concurrent_with_shared_client_and_lock():
    """
    Example showing concurrent sending with a shared client using asyncio.Lock.
    This is less efficient than separate clients but demonstrates coroutine synchronization.
    """
    send_lock = asyncio.Lock()
    
    producer = EventHubProducerClient(
        fully_qualified_namespace=FULLY_QUALIFIED_NAMESPACE,
        eventhub_name=EVENTHUB_NAME,
        credential=DefaultAzureCredential(),
    )

    async def send_with_lock(task_id):
        try:
            # Use lock to ensure coroutine-safe sending
            async with send_lock:
                batch = await producer.create_batch()
                batch.add(EventData(f"Synchronized message from coroutine {task_id}"))
                await producer.send_batch(batch)
                print(f"Coroutine {task_id} sent synchronized message successfully")
        except Exception as e:
            print(f"Coroutine {task_id} failed: {e}")

    async with producer:
        # Use asyncio.gather to run coroutines concurrently with lock synchronization
        await asyncio.gather(*[send_with_lock(i) for i in range(3)])


async def run():

    producer = EventHubProducerClient(
        fully_qualified_namespace=FULLY_QUALIFIED_NAMESPACE,
        eventhub_name=EVENTHUB_NAME,
        credential=DefaultAzureCredential(),
    )
    async with producer:
        await send_event_data_batch(producer)
        await send_event_data_batch_with_limited_size(producer)
        await send_event_data_batch_with_partition_key(producer)
        await send_event_data_batch_with_partition_id(producer)
        await send_event_data_batch_with_properties(producer)
        await send_event_data_list(producer)


async def main():
    start_time = time.time()
    await run()
    print("Send messages in {} seconds.".format(time.time() - start_time))

    # Demonstrate concurrent sending
    print("\nDemonstrating concurrent sending with separate producers...")
    await send_concurrent_with_separate_producers()

    print("\nDemonstrating concurrent sending with shared client and locks...")
    await send_concurrent_with_shared_client_and_lock()


asyncio.run(main())
