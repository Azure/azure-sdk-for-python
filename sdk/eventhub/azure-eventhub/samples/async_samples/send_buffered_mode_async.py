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

from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub import EventData
from azure.identity.aio import DefaultAzureCredential

FULLY_QUALIFIED_NAMESPACE = os.environ["EVENT_HUB_HOSTNAME"]
EVENTHUB_NAME = os.environ["EVENT_HUB_NAME"]


async def on_success(events, pid):
    # sending succeeded
    print(events, pid)


async def on_error(events, pid, error):
    # sending failed
    print(events, pid, error)


async def run():

    producer = EventHubProducerClient(
        fully_qualified_namespace=FULLY_QUALIFIED_NAMESPACE,
        eventhub_name=EVENTHUB_NAME,
        credential=DefaultAzureCredential(),
        buffered_mode=True,
        on_success=on_success,
        on_error=on_error,
    )

    # exiting the context manager will automatically call flush
    async with producer:
        # single events will be batched automatically
        for i in range(10):
            # the method returning indicates the event has been enqueued to the buffer
            await producer.send_event(EventData("Single data {}".format(i)))

        batch = await producer.create_batch()
        for i in range(10):
            batch.add(EventData("Single data in batch {}".format(i)))
        # alternatively, you can enqueue an EventDataBatch object to the buffer
        await producer.send_batch(batch)

        # calling flush sends out the events in the buffer immediately
        await producer.flush()


start_time = time.time()
asyncio.run(run())
print("Send messages in {} seconds.".format(time.time() - start_time))
