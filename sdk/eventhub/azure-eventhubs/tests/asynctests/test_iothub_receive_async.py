#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import asyncio
import pytest

from azure.eventhub.aio import EventHubClient
from azure.eventhub import EventPosition


async def pump(receiver, sleep=None):
    messages = 0
    if sleep:
        await asyncio.sleep(sleep)
    async with receiver:
        batch = await receiver.receive(timeout=10)
        messages += len(batch)
    return messages


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_iothub_receive_multiple_async(iot_connection_str):
    client = EventHubClient.from_connection_string(iot_connection_str, network_tracing=False)
    partitions = await client.get_partition_ids()
    receivers = []
    for p in partitions:
        receivers.append(client.create_consumer(consumer_group="$default", partition_id=p, event_position=EventPosition("-1"), prefetch=10, operation='/messages/events'))
    outputs = await asyncio.gather(*[pump(r) for r in receivers])

    assert isinstance(outputs[0], int) and outputs[0] <= 10
    assert isinstance(outputs[1], int) and outputs[1] <= 10


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_iothub_get_properties_async(iot_connection_str, device_id):
    client = EventHubClient.from_connection_string(iot_connection_str, network_tracing=False)
    properties = await client.get_properties()
    assert properties["partition_ids"] == ["0", "1", "2", "3"]


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_iothub_get_partition_ids_async(iot_connection_str, device_id):
    client = EventHubClient.from_connection_string(iot_connection_str, network_tracing=False)
    partitions = await client.get_partition_ids()
    assert partitions == ["0", "1", "2", "3"]


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_iothub_get_partition_properties_async(iot_connection_str, device_id):
    client = EventHubClient.from_connection_string(iot_connection_str, network_tracing=False)
    partition_properties = await client.get_partition_properties("0")
    assert partition_properties["id"] == "0"


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_iothub_receive_after_mgmt_ops_async(iot_connection_str, device_id):
    client = EventHubClient.from_connection_string(iot_connection_str, network_tracing=False)
    partitions = await client.get_partition_ids()
    assert partitions == ["0", "1", "2", "3"]
    receiver = client.create_consumer(consumer_group="$default", partition_id=partitions[0], event_position=EventPosition("-1"), operation='/messages/events')
    async with receiver:
        received = await receiver.receive(timeout=10)
        assert len(received) == 0


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_iothub_mgmt_ops_after_receive_async(iot_connection_str, device_id):
    client = EventHubClient.from_connection_string(iot_connection_str, network_tracing=False)
    receiver = client.create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition("-1"), operation='/messages/events')
    async with receiver:
        received = await receiver.receive(timeout=10)
        assert len(received) == 0

    partitions = await client.get_partition_ids()
    assert partitions == ["0", "1", "2", "3"]

