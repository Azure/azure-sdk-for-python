#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Examples to show sending events with different options to an Event Hub asynchronously.

WARNING: EventHubProducerClient and EventDataBatch are NOT coroutine-safe!
- Do NOT share EventHubProducerClient instances between coroutines
- Do NOT share EventDataBatch instances between coroutines
- Use proper async locking mechanisms when accessing clients from multiple coroutines
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


# [START concurrent_sending_with_asyncio]
async def send_events_concurrently_with_gather():
    """
    Example of concurrent sending using asyncio.gather with separate producers.
    RECOMMENDED: Use separate EventHubProducerClient instances for each coroutine.
    """
    async def send_events_from_coroutine(coroutine_id):
        # Create a separate producer for each coroutine (recommended approach)
        coroutine_producer = EventHubProducerClient(
            fully_qualified_namespace=FULLY_QUALIFIED_NAMESPACE,
            eventhub_name=EVENTHUB_NAME,
            credential=DefaultAzureCredential(),
        )
        async with coroutine_producer:
            for i in range(5):
                batch = await coroutine_producer.create_batch()
                batch.add(EventData(f"Message {i} from coroutine {coroutine_id}"))
                await coroutine_producer.send_batch(batch)
        print(f"Coroutine {coroutine_id} completed sending")

    # Launch multiple coroutines concurrently
    await asyncio.gather(*[send_events_from_coroutine(i) for i in range(3)])


async def send_events_with_shared_producer_and_lock():
    """
    Example of using a shared producer with proper async locking.
    NOT RECOMMENDED: Better to use separate producers per coroutine.
    """
    lock = asyncio.Lock()
    shared_producer = EventHubProducerClient(
        fully_qualified_namespace=FULLY_QUALIFIED_NAMESPACE,
        eventhub_name=EVENTHUB_NAME,
        credential=DefaultAzureCredential(),
    )

    async def send_with_lock(coroutine_id):
        async with lock:
            # Only one coroutine can use the producer at a time
            batch = await shared_producer.create_batch()
            batch.add(EventData(f"Locked message from coroutine {coroutine_id}"))
            await shared_producer.send_batch(batch)
        print(f"Coroutine {coroutine_id} sent message with lock")

    async with shared_producer:
        await asyncio.gather(*[send_with_lock(i) for i in range(3)])

# [END concurrent_sending_with_asyncio]


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


async def run_concurrent_examples():
    """Run concurrent sending examples (uncomment calls in main to run)"""
    print("Running concurrent sending examples...")
    await send_events_concurrently_with_gather()
    await send_events_with_shared_producer_and_lock()


start_time = time.time()
asyncio.run(run())
print("Send messages in {} seconds.".format(time.time() - start_time))

# Example of concurrent sending (uncomment to run)
# asyncio.run(run_concurrent_examples())
