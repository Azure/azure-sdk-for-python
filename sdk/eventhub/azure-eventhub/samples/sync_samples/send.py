#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Examples to show sending events with different options to an Event Hub partition.
"""

# pylint: disable=C0111

import time
import os
from azure.eventhub import EventHubProducerClient, EventData


CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']


def send_event_data_batch(producer):
    # Without specifying partition_id or partition_key
    # the events will be distributed to available partitions via round-robin.
    event_data_batch = producer.create_batch()
    event_data_batch.add(EventData('Single message'))
    producer.send_batch(event_data_batch)


def send_event_data_batch_with_limited_size(producer):
    # Without specifying partition_id or partition_key
    # the events will be distributed to available partitions via round-robin.
    event_data_batch_with_limited_size = producer.create_batch(max_size_in_bytes=1000)

    while True:
        try:
            event_data_batch_with_limited_size.add(EventData('Message inside EventBatchData'))
        except ValueError:
            # EventDataBatch object reaches max_size.
            # New EventDataBatch object can be created here to send more data.
            break

    producer.send_batch(event_data_batch_with_limited_size)


def send_event_data_batch_with_partition_key(producer):
    # Specifying partition_key.
    event_data_batch_with_partition_key = producer.create_batch(partition_key='pkey')
    event_data_batch_with_partition_key.add(EventData('Message will be sent to a partition determined by the partition key'))

    producer.send_batch(event_data_batch_with_partition_key)


def send_event_data_batch_with_partition_id(producer):
    # Specifying partition_id.
    event_data_batch_with_partition_id = producer.create_batch(partition_id='0')
    event_data_batch_with_partition_id.add(EventData('Message will be sent to target-id partition'))

    producer.send_batch(event_data_batch_with_partition_id)


def send_event_data_batch_with_properties(producer):
    event_data_batch = producer.create_batch()
    event_data = EventData('Message with properties')
    event_data.properties = {'prop_key': 'prop_value'}
    event_data_batch.add(event_data)
    producer.send_batch(event_data_batch)


producer = EventHubProducerClient.from_connection_string(
    conn_str=CONNECTION_STR,
    eventhub_name=EVENTHUB_NAME
)

start_time = time.time()
with producer:
    send_event_data_batch(producer)
    send_event_data_batch_with_limited_size(producer)
    send_event_data_batch_with_partition_key(producer)
    send_event_data_batch_with_partition_id(producer)
    send_event_data_batch_with_properties(producer)

print("Send messages in {} seconds.".format(time.time() - start_time))
