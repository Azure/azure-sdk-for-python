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

RECEIVE_TIMEOUT = 5  # timeout in seconds for a receiving operation. 0 or None means no timeout
RETRY_TOTAL = 3  # max number of retries for receive operations within the receive timeout. Actual number of retries clould be less if RECEIVE_TIMEOUT is too small
CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
STORAGE_CONNECTION_STR = os.environ["AZURE_STORAGE_CONN_STR"]


async def do_operation(event):
    pass
    # do some sync or async operations. If the operation is i/o intensive, async will have better performance
    # print(event)


async def event_handler(partition_context, events):
    if events:
        print("received events: {} from partition: {}".format(len(events), partition_context.partition_id))
        await asyncio.gather(*[do_operation(event) for event in events])
        await partition_context.update_checkpoint(events[-1])
    else:
        print("No event received from partition: {}".format(partition_context.partition_id))


async def receive_for_a_while(client, duration):
    """
    Without specified partition_id, the receive will try to receive events from all partitions and if provided with
    partition manager, the client will load-balance partition assignment with other EventHubConsumerClient instances
    which also try to receive events from all partitions and use the same storage resource.
    """
    task = asyncio.ensure_future(client.receive(event_handler=event_handler, consumer_group="$default"))
    # With specified partition_id, load-balance will be disabled
    # task = asyncio.ensure_future(client.receive(event_handler=event_handler, consumer_group="$default", partition_id = '0'))
    await asyncio.sleep(duration)
    task.cancel()


async def receive_forever(client):
    try:
        """
        Without specifying partition_id, the receive will try to receive events from all partitions and if provided with
        partition manager, the client will load-balance partition assignment with other EventHubConsumerClient instances
        which also try to receive events from all partitions and use the same storage resource.
        """
        await client.receive(event_handler=event_handler, consumer_group="$default")
        # With specified partition_id, load-balance will be disabled
        # await client.receive(event_handler=event_handler, consumer_group="$default", partition_id = '0'))
    except KeyboardInterrupt:
        client.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    container_client = ContainerClient.from_connection_string(STORAGE_CONNECTION_STR, "eventprocessor")
    partition_manager = BlobPartitionManager(container_client)
    client = EventHubConsumerClient.from_connection_string(
        CONNECTION_STR,
        partition_manager=partition_manager,  # For load balancing and checkpoint. Leave None for no load balancing
        receive_timeout=RECEIVE_TIMEOUT,  # the wait time for single receiving iteration
        retry_total=RETRY_TOTAL  # num of retry times if receiving from EventHub has an error.
    )
    try:
        loop.run_until_complete(receive_for_a_while(client, 60))
        # loop.run_until_complete(receive_forever(client))
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(client.close())
        loop.stop()
