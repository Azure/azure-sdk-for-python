#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show receiving events from an Event Hub partition with EventHubConsumerClient tracking
the last enqueued event properties of specific partition.
"""
import os
import time
from azure.eventhub import EventPosition, EventHubConsumerClient

CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
EVENT_HUB = os.environ['EVENT_HUB_NAME']

EVENT_POSITION = EventPosition("-1")
PARTITION = "0"


def on_event(partition_context, event):
    print("Received event from partition {}".format(partition_context.partition_id))
    
    # Put your code here to do some operations on the event.
    # Avoid time-consuming operations.
    print(event)

    print("Last enqueued event properties from partition: {} is: {}".format(
        partition_context.partition_id,
        event.last_enqueued_event_properties)
    )


if __name__ == '__main__':
    consumer_client = EventHubConsumerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        eventhub_name=EVENT_HUB,
    )

    try:
        with consumer_client:
            consumer_client.receive(
                on_event=on_event,
                consumer_group='$Default',
                partition_id='0',
                track_last_enqueued_event_properties=True
            )
    except KeyboardInterrupt:
        print('Stop receiving.')
