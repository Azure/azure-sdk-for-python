#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show receiving events from an Event Hub with partition manager.
In the `receive` method of `EventHubConsumerClient`:
If no partition id is specified, the partition_manager are used for load-balance and checkpoint.
If partition id is specified, the partition_manager can only be used for checkpoint.
"""
import os
from azure.storage.blob import ContainerClient
from azure.eventhub import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblob import BlobCheckpointStore


CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
STORAGE_CONNECTION_STR = os.environ["AZURE_STORAGE_CONN_STR"]


def on_event(partition_context, event):
    print("Received event from partition: {}".format(partition_context.partition_id))

    # Put your code here to do some operations on the event.
    # Avoid time-consuming operations.
    print(event)

    partition_context.update_checkpoint(event)


if __name__ == '__main__':
    container_client = ContainerClient.from_connection_string(STORAGE_CONNECTION_STR, "eventprocessor")
    partition_manager = BlobPartitionManager(container_client)
    consumer_client = EventHubConsumerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        partition_manager=partition_manager,  # For load balancing and checkpoint. Leave None for no load balancing
    )

    try:
        with consumer_client:
            """
            Without specified partition_id, the receive will try to receive events from all partitions and if provided with
            partition manager, the client will load-balance partition assignment with other EventHubConsumerClient instances
            which also try to receive events from all partitions and use the same storage resource.
            """
            consumer_client.receive(on_event=on_event, consumer_group='$Default')
            # With specified partition_id, load-balance will be disabled
            # client.receive(on_event=on_event, consumer_group='$Default', partition_id='0')
    except KeyboardInterrupt:
        print('Stop receiving.')
