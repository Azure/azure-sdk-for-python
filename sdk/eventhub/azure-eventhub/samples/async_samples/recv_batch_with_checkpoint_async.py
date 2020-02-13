#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show receiving events from an Event Hub with checkpoint store doing checkpoint by batch asynchronously.
In the `receive_batch` method of `EventHubConsumerClient`:
If no partition id is specified, the checkpoint_store are used for load-balance and checkpoint.
If partition id is specified, the checkpoint_store can only be used for checkpoint.
"""

import asyncio
import os
import logging
from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblobaio import BlobCheckpointStore

CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
STORAGE_CONNECTION_STR = os.environ["AZURE_STORAGE_CONN_STR"]
BLOB_CONTAINER_NAME = "your-blob-container-name"  # Please make sure the blob container resource exists.

logging.basicConfig(
    level=logging.INFO,
    format='%(threadName)s | %(asctime)s | %(name)-12s | %(levelname)-8s %(message)s', datefmt='%m-%d %H:%M:%S',)
log = logging.getLogger(__name__)


async def batch_upload_docs(docs):
    await asyncio.sleep(3)  # http request to upload docs


async def upload_doc(doc):
    await asyncio.sleep(1)  # http request to upload a doc


# batch process and checkpoint
# by both size and time - set max_batch_size and max_wait_time
# by only size - set max_batch_size and large max_wait_time
# by only time - set max_batch_size large and max_wait_time
# immediately when events are available - set max_wait_time=0 or None
async def on_event_batch(partition_context, event_batch):
    log.info(f"<check> batch process pid:{partition_context.partition_id} last sq {event_batch[-1].sequence_number}")
    docs = [event.body_as_str for event in event_batch]
    await batch_upload_docs(docs)  # A http request to batch upload docs to Azure Search
    await partition_context.update_checkpoint()


# enable heartbeat by setting enable_callback_when_no_event=True
async def on_event_batch_with_empty(partition_context, event_batch):
    if event_batch:
        log.info(f"<check> batch process pid:{partition_context.partition_id} last sq {event_batch[-1].sequence_number}")
        docs = [event.body_as_str for event in event_batch]
        await batch_upload_docs(docs)  # A http request to batch upload docs to Azure Search
        await partition_context.update_checkpoint()
    else:
        log.info(f"<check> batch process pid:{partition_context.partition_id} last sq None")  # just heartbeating

# process individually and batch checkpoint
async def on_event_batch_process_async_batch_checkpoint(partition_context, event_batch):
    log.info(f"<check> batch process pid:{partition_context.partition_id} last sq {event_batch[-1].sequence_number}")
    tasks = tuple(upload_doc(event.body_as_str) for event in event_batch)
    await asyncio.gather(*tasks)
    await partition_context.update_checkpoint()

# process individually and checkpoint individually or by time
# use EventHubConsumerClient.receive(). Refer to ./recv_process_individual_checkpoint_by_time.py

async def receive_batch():
    checkpoint_store = BlobCheckpointStore.from_connection_string(STORAGE_CONNECTION_STR, BLOB_CONTAINER_NAME)
    client = EventHubConsumerClient.from_connection_string(
        CONNECTION_STR,
        consumer_group="$Default",
        checkpoint_store=checkpoint_store,
    )
    async with client:
        await client.receive_batch(
            on_event_batch=on_event_batch,
            max_batch_size=100,  # optional
            max_wait_time=3,  # optional
            starting_position="-1",  # optional, "-1" is from the beginning of the partition.
        )


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(receive_batch())
