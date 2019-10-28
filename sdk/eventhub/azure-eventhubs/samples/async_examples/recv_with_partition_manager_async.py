#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show receiving events from an Event Hub with partition manager asynchronously.
In the `receive` method of `EventHubConsumerClient`:
If no partition id is specified, the partition_manager are used for load-balance and checkpoint.
If partition id is specified, the partition_manager can only be used for checkpoint.
"""

import asyncio
import os
from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub.aio import FileBasedPartitionManager

RETRY_TOTAL = 3  # max number of retries for receive operations within the receive timeout. Actual number of retries clould be less if RECEIVE_TIMEOUT is too small
CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]


async def do_operation(event):
    # do some sync or async operations. If the operation is i/o intensive, async will have better performance
    print(event)


async def event_handler(partition_context, events):
    if events:
        await asyncio.gather(*[do_operation(event) for event in events])
        await partition_context.update_checkpoint(events[-1])
    else:
        print("empty events received", "partition:", partition_context.partition_id)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    partition_manager = FileBasedPartitionManager("consumer_pm_store")
    client = EventHubConsumerClient.from_connection_string(
        CONNECTION_STR,
        partition_manager=partition_manager,  # For load balancing and checkpointing. Leave None for no load balancing
        retry_total=RETRY_TOTAL  # num of retry times if receiving from EventHub has an error.
    )
    try:
        task = asyncio.ensure_future(client.receive(event_handler=event_handler, consumer_group="$default"))
        loop.run_until_complete(asyncio.sleep(5))
        task.cancel()
    except KeyboardInterrupt:
        loop.run_until_complete(client.close())
    finally:
        loop.run_until_complete(client.close())
        loop.stop()
