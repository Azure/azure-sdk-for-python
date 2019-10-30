#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show receiving events from an Event Hub partition.
"""
import os
import time
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


def event_handler(partition_context, events):
    global total
    if events:
        print("received events: {} from partition: {}".format(len(events), partition_context.partition_id))
        total += len(events)
        for event in events:
            do_operation(event)
    else:
        print("No event received from partition: {}".format(partition_context.partition_id))


def receive_for_a_while(client, duration):
    client.receive(event_handler=event_handler, consumer_group='$Default')
    # Receive with owner level:
    # consumer_client.receive(event_handler=event_handler, consumer_group='$Default', owner_level=1)
    time.sleep(duration)
    client.close()


def receive_forever(client):
    client.receive(event_handler=event_handler, consumer_group='$Default')
    # Receive with owner level:
    # consumer_client.receive(event_handler=event_handler, consumer_group='$Default', owner_level=1)
    try:
        while True:
            time.sleep(0.05)
            pass
    except KeyboardInterrupt:
        print('Stop receiving.')
        client.close()


if __name__ == '__main__':
    consumer_client = EventHubConsumerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        event_hub_path=EVENT_HUB,
        receive_timeout=RECEIVE_TIMEOUT,  # the wait time for single receiving iteration
        retry_total=RETRY_TOTAL  # num of retry times if receiving from EventHub has an error.
    )

    with consumer_client:
        receiving_time = 5
        receive_for_a_while(consumer_client, receiving_time)
        # receive_forever(consumer_client)

        print("Received {} messages in {} seconds".format(total, receiving_time))
