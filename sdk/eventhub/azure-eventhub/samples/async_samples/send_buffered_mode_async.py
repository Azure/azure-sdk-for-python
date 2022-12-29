#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Examples to show sending events in buffered mode to an Event Hub asynchronously.
"""

import time
import asyncio
import os
from typing import TYPE_CHECKING, Optional

from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub import EventData

if TYPE_CHECKING:
    from azure.eventhub import EventDataBatch

CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']


async def on_success(events, pid: Optional[str]) -> None:
    # sending succeeded
    print(events, pid)


async def on_error(events, pid: Optional[str], error: Exception) -> None:
    # sending failed
    print(events, pid, error)


async def run() -> None:

    producer = EventHubProducerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        eventhub_name=EVENTHUB_NAME,
        buffered_mode=True,
        on_success=on_success,
        on_error=on_error
    )

    # exiting the context manager will automatically call flush
    async with producer:
        # single events will be batched automatically
        for i in range(10):
            # the method returning indicates the event has been enqueued to the buffer
            await producer.send_event(EventData(f'Single data {i}'))

        batch = await producer.create_batch()
        for i in range(10):
            batch.add(EventData(f'Single data in batch {i}'))
        # alternatively, you can enqueue an EventDataBatch object to the buffer
        await producer.send_batch(batch)

        # calling flush sends out the events in the buffer immediately
        await producer.flush()

start_time = time.time()
asyncio.run(run())
print(f"Send messages in {time.time() - start_time} seconds.")
