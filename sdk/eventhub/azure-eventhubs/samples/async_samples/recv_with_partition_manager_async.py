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
from azure.storage.blob.aio import ContainerClient
from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblobaio import BlobPartitionManager

CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
STORAGE_CONNECTION_STR = os.environ["AZURE_STORAGE_CONN_STR"]


async def do_operation(event):
    pass
    # do some sync or async operations. If the operation is i/o intensive, async will have better performance
    # print(event)


async def on_event(partition_context, event):
    # put your code here
    print("Received event from partition: {}".format(partition_context.partition_id))
    await partition_context.update_checkpoint(event)


async def receive(client):
    try:
        """
        Without specifying partition_id, the receive will try to receive events from all partitions and if provided with
        partition manager, the client will load-balance partition assignment with other EventHubConsumerClient instances
        which also try to receive events from all partitions and use the same storage resource.
        """
        await client.receive(on_event=on_event, consumer_group="$Default")
        # With specified partition_id, load-balance will be disabled
        # await client.receive(on_event=on_event, consumer_group="$default", partition_id = '0'))
    except KeyboardInterrupt:
        await client.close()


async def main():
    container_client = ContainerClient.from_connection_string(STORAGE_CONNECTION_STR, "eventprocessor")
    partition_manager = BlobPartitionManager(container_client)
    client = EventHubConsumerClient.from_connection_string(
        CONNECTION_STR,
        partition_manager=partition_manager,  # For load balancing and checkpoint. Leave None for no load balancing
    )
    async with client:
        await receive(client)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
