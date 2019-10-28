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
from azure.eventhub import EventHubConsumerClient, FileBasedPartitionManager

RECEIVE_TIMEOUT = 5  # timeout in seconds for a receiving operation. 0 or None means no timeout
RETRY_TOTAL = 3  # max number of retries for receive operations within the receive timeout. Actual number of retries clould be less if RECEIVE_TIMEOUT is too small
CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]


def do_operation(event):
    pass
    # do some operations.
    # print(event)


def event_handler(partition_context, events):
    if events:
        print("received events: {} from partition: {}".format(len(events), partition_context.partition_id))
        for event in events:
            do_operation(event)

        partition_context.update_checkpoint(events[-1])
    else:
        print("empty events received", "partition:", partition_context.partition_id)


if __name__ == '__main__':
    partition_manager = FileBasedPartitionManager('consumer_pm_store')
    client = EventHubConsumerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        partition_manager=partition_manager,  # For load balancing and checkpoint. Leave None for no load balancing
        receive_timeout=RECEIVE_TIMEOUT,  # the wait time for single receiving iteration
        retry_total=RETRY_TOTAL  # num of retry times if receiving from EventHub has an error.
    )

    try:
        """
        Without specified partition_id, the receive will try to receive events from all partitions and if provided with
        partition manager, the client will load-balance partition assignment with other EventHubConsumerClient instances
        which also try to receive events from all partitions and use the same storage resource.
        """
        task = client.receive(event_handler=event_handler, consumer_group='$Default')
        # With specified partition_id, load-balance will be disabled
        # task = client.receive(event_handler=event_handler, consumer_group='$Default', partition_id='0')
        time.sleep(5)
        task.cancel()

    except KeyboardInterrupt:
        task.cancel()


