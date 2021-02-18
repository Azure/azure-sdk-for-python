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
from azure.eventhub import EventHubConsumerClient

CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']


def on_event(partition_context, event):
    print("Received event from partition {}.".format(partition_context.partition_id))
    
    # Put your code here. to do some operations on the event.
    # Avoid time-consuming operations.
    print(event)

    print("Last enqueued event properties from partition: {} is: {}.".format(
        partition_context.partition_id,
        partition_context.last_enqueued_event_properties)
    )


if __name__ == '__main__':
    consumer_client = EventHubConsumerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        consumer_group='$Default',
        eventhub_name=EVENTHUB_NAME,
    )

    try:
        with consumer_client:
            consumer_client.receive(
                on_event=on_event,
                partition_id='0',
                track_last_enqueued_event_properties=True,
                starting_position="-1",  # "-1" is from the beginning of the partition.
            )
    except KeyboardInterrupt:
        print('Stopped receiving.')
