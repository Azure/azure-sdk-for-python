# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import pytest

from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub import EventData


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_batch_event(live_eventhub):
    client = EventHubProducerClient.from_connection_string(live_eventhub["connection_str"])
    async with client:
        batch = await client.create_batch()

        # large message that should be split into multiple transfer frames
        while True:
            try:
                batch.add(EventData(b'test'))
            except ValueError:
                break
        await client.send_batch(batch)

        # small message that fits in one transfer frame
        batch = await client.create_batch()
        for _ in range(100):
            batch.add(EventData(b'test' * 60))
        await client.send_batch(batch)


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_batch_event_single_partition(live_eventhub):
    client = EventHubProducerClient.from_connection_string(live_eventhub["connection_str"])
    async with client:
        batch = await client.create_batch(partition_id="0")

        while True:
            try:
                batch.add(EventData(b'test'))
            except ValueError:
                break
        await client.send_batch(batch)

        batch = await client.create_batch()
        for _ in range(100):
            batch.add(EventData(b'test' * 60))
        await client.send_batch(batch)
