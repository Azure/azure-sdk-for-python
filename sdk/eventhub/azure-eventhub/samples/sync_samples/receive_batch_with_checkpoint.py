#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show receiving events from an Event Hub with checkpoint store doing checkpoint by batch.
In the `receive_batch` method of `EventHubConsumerClient`:
If no partition id is specified, the checkpoint_store are used for load-balance and checkpoint.
If partition id is specified, the checkpoint_store can only be used for checkpoint without load balancing.
"""

import os
import logging
from azure.eventhub import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblob import BlobCheckpointStore

CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']
STORAGE_CONNECTION_STR = os.environ["AZURE_STORAGE_CONN_STR"]
BLOB_CONTAINER_NAME = "your-blob-container-name"  # Please make sure the blob container resource exists.

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def on_event_batch(partition_context, event_batch):
    log.info("Partition {}, Received count: {}".format(partition_context.partition_id, len(event_batch)))
    # put your code here
    partition_context.update_checkpoint()


def receive_batch():
    checkpoint_store = BlobCheckpointStore.from_connection_string(STORAGE_CONNECTION_STR, BLOB_CONTAINER_NAME)
    client = EventHubConsumerClient.from_connection_string(
        CONNECTION_STR,
        consumer_group="$Default",
        eventhub_name=EVENTHUB_NAME,
        checkpoint_store=checkpoint_store,
    )
    with client:
        client.receive_batch(
            on_event_batch=on_event_batch,
            max_batch_size=100,
            starting_position="-1",  # "-1" is from the beginning of the partition.
        )


if __name__ == '__main__':
    receive_batch()
