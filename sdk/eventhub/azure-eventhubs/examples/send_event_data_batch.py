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
from azure.eventhub import EventHubClient, EventData, EventHubSharedKeyCredential


HOSTNAME = os.environ['EVENT_HUB_HOSTNAME']  # <mynamespace>.servicebus.windows.net
EVENT_HUB = os.environ['EVENT_HUB_NAME']

USER = os.environ['EVENT_HUB_SAS_POLICY']
KEY = os.environ['EVENT_HUB_SAS_KEY']


def create_batch_data(producer):
    event_data_batch = producer.create_batch(max_size=10000)
    while True:
        try:
            event_data_batch.try_add(EventData('Message inside EventBatchData'))
        except ValueError:
            # EventDataBatch object reaches max_size.
            # New EventDataBatch object can be created here to send more data
            break
    return event_data_batch


client = EventHubClient(host=HOSTNAME, event_hub_path=EVENT_HUB, credential=EventHubSharedKeyCredential(USER, KEY),
                        network_tracing=False)
producer = client.create_producer()
start_time = time.time()
with producer:
    event_data_batch = create_batch_data(producer)
    producer.send(event_data_batch)
print("Runtime: {} seconds".format(time.time() - start_time))
