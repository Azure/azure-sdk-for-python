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
import time
from azure.storage.blob import ContainerClient
from azure.eventhub import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblob import BlobPartitionManager


RECEIVE_TIMEOUT = 5  # timeout in seconds for a receiving operation. 0 or None means no timeout
RETRY_TOTAL = 3  # max number of retries for receive operations within the receive timeout. Actual number of retries clould be less if RECEIVE_TIMEOUT is too small
CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
STORAGE_CONNECTION_STR = os.environ["AZURE_STORAGE_CONN_STR"]


def do_operation(event):
    # do some operations on the event, avoid time-consuming ops
    pass


def on_event(partition_context, events):
    # put your code here
    print("received events: {} from partition: {}".format(len(events), partition_context.partition_id))
    for event in events:
        do_operation(event)

    partition_context.update_checkpoint(events[-1])


if __name__ == '__main__':
    container_client = ContainerClient.from_connection_string(STORAGE_CONNECTION_STR, "eventprocessor")
    partition_manager = BlobPartitionManager(container_client)
    consumer_client = EventHubConsumerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        partition_manager=partition_manager,  # For load balancing and checkpoint. Leave None for no load balancing
        receive_timeout=RECEIVE_TIMEOUT,  # the wait time for single receiving iteration
        retry_total=RETRY_TOTAL  # num of retry times if receiving from EventHub has an error.
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
        consumer_client.close()
