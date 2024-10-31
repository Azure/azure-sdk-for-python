#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show receiving events from an Event Hub with checkpoint store doing checkpoint
by every fixed event count asynchronously.
In the `receive` method of `EventHubConsumerClient`:
If no partition id is specified, the checkpoint_store are used for load-balance and checkpoint.
If partition id is specified, the checkpoint_store can only be used for checkpoint.
"""
from typing import Dict
import asyncio
import os
from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblobaio import BlobCheckpointStore
from azure.identity.aio import DefaultAzureCredential

FULLY_QUALIFIED_NAMESPACE = os.environ["EVENT_HUB_HOSTNAME"]
EVENTHUB_NAME = os.environ["EVENT_HUB_NAME"]

storage_account_name = os.environ["AZURE_STORAGE_ACCOUNT"]
protocol = os.environ.get("PROTOCOL", "https")
suffix = os.environ.get("ACCOUNT_URL_SUFFIX", "core.windows.net")
BLOB_ACCOUNT_URL = f"{protocol}://{storage_account_name}.blob.{suffix}"
BLOB_CONTAINER_NAME = "your-blob-container-name"  # Please make sure the blob container resource exists.

partition_recv_cnt_since_last_checkpoint: Dict[str, int] = {}
checkpoint_event_cnt = 20


async def on_event(partition_context, event):
    # Put your code here.
    p_id = partition_context.partition_id
    print("Received event from partition: {}.".format(p_id))
    partition_recv_cnt_since_last_checkpoint[p_id] += 1
    if partition_recv_cnt_since_last_checkpoint[p_id] >= checkpoint_event_cnt:
        await partition_context.update_checkpoint(event)
        partition_recv_cnt_since_last_checkpoint[p_id] = 0


async def receive(client):
    """
    Without specifying partition_id, the receive will try to receive events from all partitions and if provided with
    a checkpoint store, the client will load-balance partition assignment with other EventHubConsumerClient instances
    which also try to receive events from all partitions and use the same storage resource.
    """
    await client.receive(
        on_event=on_event,
        starting_position="-1",  # "-1" is from the beginning of the partition.
    )
    # With specified partition_id, load-balance will be disabled, for example:
    # await client.receive(on_event=on_event, partition_id='0'))


async def main():
    checkpoint_store = BlobCheckpointStore(
        blob_account_url=BLOB_ACCOUNT_URL, container_name=BLOB_CONTAINER_NAME, credential=DefaultAzureCredential()
    )
    client = EventHubConsumerClient(
        fully_qualified_namespace=FULLY_QUALIFIED_NAMESPACE,
        eventhub_name=EVENTHUB_NAME,
        credential=DefaultAzureCredential(),
        consumer_group="$Default",
        checkpoint_store=checkpoint_store,
    )
    async with client:
        await receive(client)


if __name__ == "__main__":
    asyncio.run(main())
