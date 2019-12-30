#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show receiving events from Event Hub partitions with custom starting position.
"""
import os
from azure.eventhub import EventHubConsumerClient, EventHubProducerClient, EventData

CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']


def on_partition_initialize(partition_context):
    # put your code here
    print("Partition: {} has been initialized".format(partition_context.partition_id))


def on_partition_close(partition_context, reason):
    # put your code here
    print("Partition: {} has been closed, reason for closing: {}".format(partition_context.partition_id,
                                                                         reason))


def on_error(partition_context, error):
    # put your code here
    print("Partition: {} met an exception during receiving: {}".format(partition_context.partition_id,
                                                                       error))


def on_event(partition_context, event):
    # put your code here
    print("Received event: {} from partition: {}".format(event.body_as_str(), partition_context.partition_id))


def send_test_data(producer_client):
    with producer_client:
        event_data_batch_to_partition_0 = producer_client.create_batch(partition_id='0')
        event_data_batch_to_partition_0.add(EventData("First event in partition 0"))
        event_data_batch_to_partition_0.add(EventData("Second event in partition 0"))
        event_data_batch_to_partition_0.add(EventData("Third event in partition 0"))
        event_data_batch_to_partition_0.add(EventData("Forth event in partition 0"))
        producer_client.send_batch(event_data_batch_to_partition_0)

        event_data_batch_to_partition_1 = producer_client.create_batch(partition_id='1')
        event_data_batch_to_partition_1.add(EventData("First event in partition 1"))
        event_data_batch_to_partition_1.add(EventData("Second event in partition 1"))
        event_data_batch_to_partition_1.add(EventData("Third event in partition 1"))
        event_data_batch_to_partition_1.add(EventData("Forth event in partition 1"))
        producer_client.send_batch(event_data_batch_to_partition_1)


if __name__ == '__main__':

    producer_client = EventHubProducerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        eventhub_name=EVENTHUB_NAME,
    )

    send_test_data(producer_client)

    consumer_client = EventHubConsumerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        consumer_group='$Default',
        eventhub_name=EVENTHUB_NAME,
    )

    partition_0_last_enqueued_sequence_number =\
        consumer_client.get_partition_properties("0")["last_enqueued_sequence_number"]
    partition_1_last_enqueued_sequence_number =\
        consumer_client.get_partition_properties("1")["last_enqueued_sequence_number"]

    # client will receive messages from position of the third from last from partition 0
    # client will receive messages from position of the second from last from partition 1
    starting_position = {
        "0": partition_0_last_enqueued_sequence_number - 3,
        "1": partition_1_last_enqueued_sequence_number - 2
    }

    try:
        with consumer_client:
            consumer_client.receive(
                on_event=on_event,
                on_partition_initialize=on_partition_initialize,
                on_partition_close=on_partition_close,
                on_error=on_error,
                starting_position=starting_position
            )
    except KeyboardInterrupt:
        print('Stop receiving.')
