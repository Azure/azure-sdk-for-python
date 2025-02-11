#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show receiving events from an Event Hub for a period of time asynchronously.
"""

import asyncio
import os
import time
from azure.eventhub.aio import EventHubConsumerClient
from azure.identity.aio import DefaultAzureCredential

FULLY_QUALIFIED_NAMESPACE = os.environ["EVENT_HUB_HOSTNAME"]
EVENTHUB_NAME = os.environ["EVENT_HUB_NAME"]
RECEIVE_DURATION = 15


async def on_event(partition_context, event):
    # Put your code here.
    print("Received event from partition: {}.".format(partition_context.partition_id))
    await partition_context.update_checkpoint(event)


async def on_partition_initialize(partition_context):
    # Put your code here.
    print("Partition: {} has been initialized.".format(partition_context.partition_id))


async def on_partition_close(partition_context, reason):
    # Put your code here.
    print("Partition: {} has been closed, reason for closing: {}.".format(partition_context.partition_id, reason))


async def on_error(partition_context, error):
    # Put your code here. partition_context can be None in the on_error callback.
    if partition_context:
        print(
            "An exception: {} occurred during receiving from Partition: {}.".format(
                partition_context.partition_id, error
            )
        )
    else:
        print("An exception: {} occurred during the load balance process.".format(error))


async def main():
    client = EventHubConsumerClient(
        fully_qualified_namespace=FULLY_QUALIFIED_NAMESPACE,
        eventhub_name=EVENTHUB_NAME,
        credential=DefaultAzureCredential(),
        consumer_group="$default",
    )

    print("Consumer will keep receiving for {} seconds, start time is {}.".format(RECEIVE_DURATION, time.time()))

    async with client:
        task = asyncio.ensure_future(
            client.receive(
                on_event=on_event,
                on_error=on_error,
                on_partition_close=on_partition_close,
                on_partition_initialize=on_partition_initialize,
                starting_position="-1",  # "-1" is from the beginning of the partition.
            )
        )
        await asyncio.sleep(RECEIVE_DURATION)
    await task

    print("Consumer has stopped receiving, end time is {}.".format(time.time()))


if __name__ == "__main__":
    asyncio.run(main())
