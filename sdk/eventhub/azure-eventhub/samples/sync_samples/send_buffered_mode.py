#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Examples to show sending events in buffered mode to an Event Hub.
"""

import time
import os
from typing import TYPE_CHECKING, Optional
from azure.eventhub import EventHubProducerClient, EventData

if TYPE_CHECKING:
    from azure.eventhub import EventDataBatch

CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']


def on_success(events, pid: Optional[str]) -> None:
    # sending succeeded
    print(events, pid)


def on_error(events, pid: Optional[str], error: Exception) -> None:
    # sending failed
    print(events, pid, error)


producer = EventHubProducerClient.from_connection_string(
    conn_str=CONNECTION_STR,
    eventhub_name=EVENTHUB_NAME,
    buffered_mode=True,
    on_success=on_success,
    on_error=on_error
)

start_time = time.time()

# exiting the context manager will automatically call flush
with producer:
    # single events will be batched automatically
    for i in range(10):
        # the method returning indicates the event has been enqueued to the buffer
        producer.send_event(EventData(f'Single data {i}'))

    batch: EventDataBatch = producer.create_batch()
    for i in range(10):
        batch.add(EventData(f'Single data in batch {i}'))
    # alternatively, you can enqueue an EventDataBatch object to the buffer
    producer.send_batch(batch)

    # calling flush sends out the events in the buffer immediately
    producer.flush()

print(f"Send messages in {time.time() - start_time} seconds.")
