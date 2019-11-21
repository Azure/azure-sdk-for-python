#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show creating and sending EventBatchData within limited size.
"""

# pylint: disable=C0111

import time
import os
from azure.eventhub import EventHubProducerClient, EventData


EVENT_HUB_CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']


def create_batch_data(producer_client):
    batch_data = producer_client.create_batch(max_size=10000)
    while True:
        try:
            batch_data.try_add(EventData('Message inside EventBatchData'))
        except ValueError:
            # EventDataBatch object reaches max_size.
            # New EventDataBatch object can be created here to send more data
            break
    return batch_data


producer = EventHubProducerClient.from_connection_string(conn_str=EVENT_HUB_CONNECTION_STR, event_hub_path=EVENTHUB_NAME)

start_time = time.time()
with producer:
    event_data_batch = create_batch_data(producer)
    producer.send(event_data_batch)
print("Runtime: {} seconds".format(time.time() - start_time))
