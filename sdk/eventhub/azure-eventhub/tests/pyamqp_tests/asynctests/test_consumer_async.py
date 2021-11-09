# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import asyncio
import pytest

from azure.eventhub.aio import EventHubConsumerClient, EventHubProducerClient
from azure.eventhub import EventData


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_from_single_partition(live_eventhub):
    producer_client = EventHubProducerClient.from_connection_string(live_eventhub["connection_str"])
    consumer_client = EventHubConsumerClient.from_connection_string(live_eventhub["connection_str"], consumer_group=live_eventhub["consumer_group"])

    to_send_count = 10
    received_count = [0]

    async def on_event(partition_context, event):
        received_count[0] += 1

    batch = await producer_client.create_batch(partition_id="0")
    for _ in range(to_send_count):
        batch.add(EventData(b'data'))

    await producer_client.send_batch(batch)

    future = asyncio.create_task(
        consumer_client.receive(
            on_event=on_event,
            partition_id="0",
            starting_position="-1"
        )
    )
    await asyncio.sleep(15)
    await consumer_client.close()
    await future
    assert to_send_count == received_count[0]
