#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import asyncio
import pytest
import sys

from azure.eventhub import (
    EventData,
    EventPosition,
    EventHubError,
    ConnectError,
    AuthenticationError,
    EventDataSendError,
)
from azure.eventhub.aio.client_async import EventHubClient


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_with_invalid_hostname_async(invalid_hostname, connstr_receivers):
    _, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(invalid_hostname)
    sender = client._create_producer()
    with pytest.raises(AuthenticationError):
        await sender.send(EventData("test data"))
    await sender.close()
    await client.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_with_invalid_hostname_async(invalid_hostname):
    client = EventHubClient.from_connection_string(invalid_hostname)
    receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition("-1"))
    with pytest.raises(AuthenticationError):
        await receiver.receive(timeout=3)
    await receiver.close()
    await client.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_with_invalid_key_async(invalid_key, connstr_receivers):
    _, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(invalid_key)
    sender = client._create_producer()
    with pytest.raises(AuthenticationError):
        await sender.send(EventData("test data"))
    await sender.close()
    await client.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_with_invalid_key_async(invalid_key):
    client = EventHubClient.from_connection_string(invalid_key)
    receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition("-1"))
    with pytest.raises(AuthenticationError):
        await receiver.receive(timeout=3)
    await receiver.close()
    await client.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_with_invalid_policy_async(invalid_policy, connstr_receivers):
    _, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(invalid_policy)
    sender = client._create_producer()
    with pytest.raises(AuthenticationError):
        await sender.send(EventData("test data"))
    await sender.close()
    await client.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_with_invalid_policy_async(invalid_policy):
    client = EventHubClient.from_connection_string(invalid_policy)
    receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition("-1"))
    with pytest.raises(AuthenticationError):
        await receiver.receive(timeout=3)
    await receiver.close()
    await client.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_partition_key_with_partition_async(connection_str):
    pytest.skip("No longer raise value error. EventData will be sent to partition_id")
    client = EventHubClient.from_connection_string(connection_str)
    sender = client._create_producer(partition_id="1")
    try:
        data = EventData(b"Data")
        with pytest.raises(ValueError):
            await sender.send(EventData("test data"))
    finally:
        await sender.close()
        await client.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_non_existing_entity_sender_async(connection_str):
    client = EventHubClient.from_connection_string(connection_str, event_hub_path="nemo")
    sender = client._create_producer(partition_id="1")
    with pytest.raises(AuthenticationError):
        await sender.send(EventData("test data"))
    await sender.close()
    await client.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_non_existing_entity_receiver_async(connection_str):
    client = EventHubClient.from_connection_string(connection_str, event_hub_path="nemo")
    receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition("-1"))
    with pytest.raises(AuthenticationError):
        await receiver.receive(timeout=5)
    await receiver.close()
    await client.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_from_invalid_partitions_async(connection_str):
    partitions = ["XYZ", "-1", "1000", "-"]
    for p in partitions:
        client = EventHubClient.from_connection_string(connection_str)
        receiver = client._create_consumer(consumer_group="$default", partition_id=p, event_position=EventPosition("-1"))
        with pytest.raises(ConnectError):
            await receiver.receive(timeout=5)
        await receiver.close()
        await client.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_to_invalid_partitions_async(connection_str):
    partitions = ["XYZ", "-1", "1000", "-"]
    for p in partitions:
        client = EventHubClient.from_connection_string(connection_str)
        sender = client._create_producer(partition_id=p)
        with pytest.raises(ConnectError):
            await sender.send(EventData("test data"))
        await sender.close()
        await client.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_too_large_message_async(connection_str):
    if sys.platform.startswith('darwin'):
        pytest.skip("Skipping on OSX - open issue regarding message size")
    client = EventHubClient.from_connection_string(connection_str)
    sender = client._create_producer()
    try:
        data = EventData(b"A" * 1100000)
        with pytest.raises(EventDataSendError):
            await sender.send(data)
    finally:
        await sender.close()
        await client.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_null_body_async(connection_str):
    client = EventHubClient.from_connection_string(connection_str)
    sender = client._create_producer()
    try:
        with pytest.raises(ValueError):
            data = EventData(None)
            await sender.send(data)
    finally:
        await sender.close()
        await client.close()


async def pump(receiver):
    async with receiver:
        messages = 0
        count = 0
        batch = await receiver.receive(timeout=10)
        while batch and count <= 5:
            count += 1
            messages += len(batch)
            batch = await receiver.receive(timeout=10)
        return messages


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_max_receivers_async(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str)
    receivers = []
    for i in range(6):
        receivers.append(client._create_consumer(consumer_group="$default", partition_id="0", prefetch=1000, event_position=EventPosition('@latest')))

    outputs = await asyncio.gather(
        pump(receivers[0]),
        pump(receivers[1]),
        pump(receivers[2]),
        pump(receivers[3]),
        pump(receivers[4]),
        pump(receivers[5]),
        return_exceptions=True)
    print(outputs)
    failed = [o for o in outputs if isinstance(o, EventHubError)]
    assert len(failed) == 1
    print(failed[0].message)
    await client.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_create_batch_with_invalid_hostname_async(invalid_hostname):
    client = EventHubClient.from_connection_string(invalid_hostname)
    sender = client._create_producer()
    try:
        with pytest.raises(AuthenticationError):
            batch_event_data = await sender.create_batch(max_size=300)
    finally:
        await sender.close()
        await client.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_create_batch_with_too_large_size_async(connection_str):
    client = EventHubClient.from_connection_string(connection_str)
    sender = client._create_producer()
    try:
        with pytest.raises(ValueError):
            batch_event_data = await sender.create_batch(max_size=5 * 1024 * 1024)
    finally:
        await sender.close()
        await client.close()
