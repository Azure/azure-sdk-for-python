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

CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']
RECEIVE_DURATION = 15


async def on_event(partition_context, event):
    # put your code here
    print("Received event from partition: {}".format(partition_context.partition_id))


async def on_partition_initialize(partition_context):
    # put your code here
    print("Partition: {} has been initialized".format(partition_context.partition_id))


async def on_partition_close(partition_context, reason):
    # put your code here
    print("Partition: {} has been closed, reason for closing: {}".format(partition_context.partition_id,
                                                                         reason))


async def on_error(partition_context, error):
    # put your code here
    print("Partition: {} met an exception during receiving: {}".format(partition_context.partition_id,
                                                                       error))


async def main():
    client = EventHubConsumerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        consumer_group="$default",
        eventhub_name=EVENTHUB_NAME
    )

    print('Consumer will keep receiving for {} seconds, start time is {}'.format(duration, time.time()))

    task = asyncio.ensure_future(
        client.receive(
            on_event=on_event,
            on_error=on_error,
            on_partition_close=on_partition_close,
            on_partition_initialize=on_partition_initialize
        )
    )
    await asyncio.sleep(RECEIVE_DURATION)
    await client.close()
    await task

    print('Consumer has stopped receiving, end time is {}'.format(time.time()))

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
