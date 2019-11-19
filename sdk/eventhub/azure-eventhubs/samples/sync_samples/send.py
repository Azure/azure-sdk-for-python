#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show sending individual events to an Event Hub partition.
Although this works, sending events in batches will get better performance.
See 'send_event_data_batch.py' for an example of batching.
"""

# pylint: disable=C0111

import time
import os
from azure.eventhub import EventHubProducerClient, EventData

EVENT_HUB_CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
EVENT_HUB = os.environ['EVENT_HUB_NAME']

producer = EventHubProducerClient.from_connection_string(conn_str=EVENT_HUB_CONNECTION_STR, event_hub_path=EVENT_HUB)

start_time = time.time()
with producer:
    # Without specifying partition_id or partition_key
    # The events will be distributed to available partitions via round-robin.
    event_data_batch = producer.create_batch(max_size=10000)

    # Specifying partition_id
    # event_data_batch = producer.create_batch(partition_id='0')

    # Specifying partition_key
    # event_data_batch = producer.create_batch(partition_key='pkey')

    while True:
        try:
            event_data_batch.add(EventData('Message inside EventBatchData'))
        except ValueError:
            # EventDataBatch object reaches max_size.
            # New EventDataBatch object can be created here to send more data
            break

    producer.send_batch(event_data_batch)

print("Send messages in {} seconds".format(time.time() - start_time))
