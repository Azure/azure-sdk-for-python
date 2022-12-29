#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Example to show streaming sending events with different options to an Event Hub asynchronously.
"""

import time
import asyncio
import os
from typing import TYPE_CHECKING

from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub import EventData

if TYPE_CHECKING:
    from azure.eventhub import EventDataBatch

CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']


async def run() -> None:

    producer = EventHubProducerClient.from_connection_string(
        conn_str=CONNECTION_STR,
        eventhub_name=EVENTHUB_NAME
    )

    to_send_message_cnt = 500
    bytes_per_message = 256

    async with producer:
        event_data_batch: EventDataBatch = await producer.create_batch()
        for i in range(to_send_message_cnt):
            event_data = EventData('D' * bytes_per_message)
            try:
                event_data_batch.add(event_data)
            except ValueError:
                await producer.send_batch(event_data_batch)
                event_data_batch = await producer.create_batch()
                event_data_batch.add(event_data)
        if len(event_data_batch) > 0:
            await producer.send_batch(event_data_batch)


start_time = time.time()
asyncio.run(run())
print(f"Send messages in {time.time() - start_time} seconds.")
