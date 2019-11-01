#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show receiving events from an Event Hub partition.
"""
import os
from azure.eventhub import EventPosition, EventHubConsumerClient

CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
EVENT_HUB = os.environ['EVENT_HUB_NAME']

RECEIVE_TIMEOUT = 5  # timeout in seconds for a receiving operation. 0 or None means no timeout
RETRY_TOTAL = 3  # max number of retries for receive operations within the receive timeout. Actual number of retries clould be less if RECEIVE_TIMEOUT is too small

EVENT_POSITION = EventPosition("-1")
PARTITION = "0"

total = 0


def do_operation(event):
    pass
    # do some operations on the event
    # print(event)


def on_partition_initialize(partition_context):
    print("Partition: {} has been intialized".format(partition_context.partition_id))


def on_partition_close(partition_context, reason):
    print("Partition: {} has been closed, reason for closing: {}".format(partition_context.partition_id,
                                                                         reason))


def on_error(partition_context, error):
    print("Partition: {} met an exception during receiving: {}".format(partition_context.partition_id,
                                                                       error))


def on_event(partition_context, events):
    global total

    print("received events: {} from partition: {}".format(len(events), partition_context.partition_id))
    total += len(events)
    for event in events:
        do_operation(event)


if __name__ == '__main__':
    consumer_client = EventHubConsumerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        event_hub_path=EVENT_HUB,
        receive_timeout=RECEIVE_TIMEOUT,  # the wait time for single receiving iteration
        retry_total=RETRY_TOTAL  # num of retry times if receiving from EventHub has an error.
    )

    try:
        with consumer_client:
            consumer_client.receive(on_event=on_event, consumer_group='$Default',
                                    on_partition_initialize=on_partition_initialize,
                                    on_partition_close=on_partition_close,
                                    on_error=on_error)
            # Receive with owner level:
            # consumer_client.receive(on_event=on_event, consumer_group='$Default', owner_level=1)
    except KeyboardInterrupt:
        print('Stop receiving.')
        consumer_client.close()
