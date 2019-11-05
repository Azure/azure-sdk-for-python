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

total = 0


def do_operation(event):
    # do some operations on the event, avoid time-consuming ops
    pass


def on_events(partition_context, events):
    # put your code here
    global total
    print("received events: {} from partition {}".format(len(events), partition_context.partition_id))
    total += len(events)
    for event in events:
        do_operation(event)

    print("Last enqueued event properties from partition: {} is: {}".
          format(partition_context.partition_id,
                 events[-1].last_enqueued_event_properties))


if __name__ == '__main__':
    consumer_client = EventHubConsumerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        event_hub_path=EVENT_HUB,
    )

    try:
        with consumer_client:
            consumer_client.receive(on_events=on_events, consumer_group='$Default',
                                    partition_id='0', track_last_enqueued_event_properties=True)

    except KeyboardInterrupt:
        print('Stop receiving.')
