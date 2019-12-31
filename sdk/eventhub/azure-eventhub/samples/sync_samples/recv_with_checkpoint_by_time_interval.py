#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show receiving events from an Event Hub with checkpoint store doing checkpoint
by every fixed time interval.
In the `receive` method of `EventHubConsumerClient`:
If no partition id is specified, the checkpoint_store are used for load-balance and checkpoint.
If partition id is specified, the checkpoint_store can only be used for checkpoint.
"""
import os
import time
from azure.eventhub import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblob import BlobCheckpointStore


CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
STORAGE_CONNECTION_STR = os.environ["AZURE_STORAGE_CONN_STR"]

partition_last_checkpoint_time = dict()
checkpoint_time_interval = 15


def on_event(partition_context, event):
    # put your code here to do some operations on the event.
    # Avoid time-consuming operations.
    p_id = partition_context.partition_id
    print("Received event from partition: {}".format(p_id))
    now_time = time.time()
    p_id = partition_context.partition_id
    if (partition_last_checkpoint_time.get(p_id) is None) or \
            (now_time - partition_last_checkpoint_time.get(p_id)) >= checkpoint_time_interval:
        partition_context.update_checkpoint(event)
        partition_last_checkpoint_time[p_id] = now_time


if __name__ == '__main__':
    checkpoint_store = BlobCheckpointStore.from_connection_string(STORAGE_CONNECTION_STR, "eventprocessor")
    consumer_client = EventHubConsumerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        consumer_group='$Default',
        checkpoint_store=checkpoint_store,  # For load-balancing and checkpoint. Leave None for no load-balancing
    )

    try:
        with consumer_client:
            """
            Without specified partition_id, the receive will try to receive events from all partitions and if provided with
            a checkpoint store, the client will load-balance partition assignment with other EventHubConsumerClient instances
            which also try to receive events from all partitions and use the same storage resource.
            """
            consumer_client.receive(on_event=on_event)
            # With specified partition_id, load-balance will be disabled
            # client.receive(on_event=on_event, partition_id='0')
    except KeyboardInterrupt:
        print('Stop receiving.')
