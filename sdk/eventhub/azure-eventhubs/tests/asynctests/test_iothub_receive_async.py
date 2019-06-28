#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os
import asyncio
import pytest
import time

from azure.eventhub.aio import EventHubClient
from azure.eventhub import EventData, EventPosition, EventHubError


async def pump(receiver, sleep=None):
    messages = 0
    if sleep:
        await asyncio.sleep(sleep)
    async with receiver:
        batch = await receiver.receive(timeout=1)
        messages += len(batch)
    return messages


async def get_partitions(iot_connection_str):
    client = EventHubClient.from_connection_string(iot_connection_str, network_tracing=False)
    receiver = client.create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition("-1"), prefetch=1000, operation='/messages/events')
    async with receiver:
        partitions = await client.get_properties()
        return partitions["partition_ids"]


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_iothub_receive_multiple_async(iot_connection_str):
    pytest.skip("This will get AuthenticationError. We're investigating...")
    partitions = await get_partitions(iot_connection_str)
    client = EventHubClient.from_connection_string(iot_connection_str, network_tracing=False)
    receivers = []
    for p in partitions:
        receivers.append(client.create_consumer(consumer_group="$default", partition_id=p, event_position=EventPosition("-1"), prefetch=10, operation='/messages/events'))
    outputs = await asyncio.gather(*[pump(r) for r in receivers])

    assert isinstance(outputs[0], int) and outputs[0] <= 10
    assert isinstance(outputs[1], int) and outputs[1] <= 10
