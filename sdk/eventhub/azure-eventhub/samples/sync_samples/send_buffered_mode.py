#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Examples to show sending events with different options to an Event Hub partition.
"""

import time
import os
from azure.eventhub import EventHubProducerClient, EventData

CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']


def on_success(events, pid):
    # sending succeeded
    print(events, pid)


def on_error(event, error, pid):
    # sending failed
    print(event, error, pid)


producer = EventHubProducerClient.from_connection_string(
    conn_str=CONNECTION_STR,
    eventhub_name=EVENTHUB_NAME,
    buffered_mode=True,
    on_success=on_success,
    on_error=on_error
)

start_time = time.time()
with producer:
    for i in range(10):
        producer.send_event(EventData('Single data {}'.format(i)))

    batch = producer.create_batch()
    for i in range(10):
        batch.add(EventData('Single data in batch {}'.format(i)))
    producer.send_batch(batch)

print("Send messages in {} seconds.".format(time.time() - start_time))
