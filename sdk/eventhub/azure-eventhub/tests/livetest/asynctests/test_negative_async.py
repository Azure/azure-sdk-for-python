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
    EventDataBatch,
)
from azure.eventhub.exceptions import (
    EventHubError,
    ConnectError,
    AuthenticationError,
    EventDataSendError
)
from azure.eventhub.aio import EventHubConsumerClient, EventHubProducerClient


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_with_invalid_hostname_async(invalid_hostname, connstr_receivers):
    if sys.platform.startswith('darwin'):
        pytest.skip("Skipping on OSX - it keeps reporting 'Unable to set external certificates' "
                    "and blocking other tests")
    _, receivers = connstr_receivers
    client = EventHubProducerClient.from_connection_string(invalid_hostname)
    async with client:
        with pytest.raises(ConnectError):
            batch = EventDataBatch()
            batch.add(EventData("test data"))
            await client.send_batch(batch)

    # test setting callback
    async def on_error(events, pid, err):
        assert len(events) == 1
        assert not pid
        on_error.err = err

    on_error.err = None
    client = EventHubProducerClient.from_connection_string(invalid_hostname, on_error=on_error)
    async with client:
        batch = EventDataBatch()
        batch.add(EventData("test data"))
        await client.send_batch(batch)
    assert isinstance(on_error.err, ConnectError)

    on_error.err = None
    client = EventHubProducerClient.from_connection_string(invalid_hostname, on_error=on_error)
    async with client:
        await client.send_event(EventData("test data"))
    assert isinstance(on_error.err, ConnectError)


@pytest.mark.parametrize("invalid_place",
                         ["hostname", "key_name", "access_key", "event_hub", "partition"])
@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_receive_with_invalid_param_async(live_eventhub, invalid_place):
    eventhub_config = live_eventhub.copy()
    if invalid_place != "partition":
        eventhub_config[invalid_place] = "invalid " + invalid_place
    conn_str = live_eventhub["connection_str"].format(
        eventhub_config['hostname'],
        eventhub_config['key_name'],
        eventhub_config['access_key'],
        eventhub_config['event_hub'])

    client = EventHubConsumerClient.from_connection_string(conn_str, consumer_group='$default', retry_total=0)

    async def on_event(partition_context, event):
        pass

    async with client:
        if invalid_place == "partition":
            task = asyncio.ensure_future(client.receive(on_event, partition_id=invalid_place,
                                         starting_position="-1"))
        else:
            task = asyncio.ensure_future(client.receive(on_event, partition_id="0",
                                                        starting_position="-1"))
        await asyncio.sleep(10)
        assert len(client._event_processors) == 1
    await task


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_with_invalid_key_async(invalid_key):
    client = EventHubProducerClient.from_connection_string(invalid_key)
    async with client:
        with pytest.raises(ConnectError):
            batch = EventDataBatch()
            batch.add(EventData("test data"))
            await client.send_batch(batch)


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_with_invalid_policy_async(invalid_policy):
    client = EventHubProducerClient.from_connection_string(invalid_policy)
    async with client:
        with pytest.raises(ConnectError):
            batch = EventDataBatch()
            batch.add(EventData("test data"))
            await client.send_batch(batch)


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_non_existing_entity_sender_async(connection_str):
    client = EventHubProducerClient.from_connection_string(connection_str, eventhub_name="nemo")
    async with client:
        with pytest.raises(ConnectError):
            batch = EventDataBatch()
            batch.add(EventData("test data"))
            await client.send_batch(batch)


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_to_invalid_partitions_async(connection_str):
    partitions = ["XYZ", "-1", "1000", "-"]
    for p in partitions:
        client = EventHubProducerClient.from_connection_string(connection_str)
        try:
            with pytest.raises(ConnectError):
                batch = await client.create_batch(partition_id=p)
                batch.add(EventData("test data"))
                await client.send_batch(batch)
        finally:
            await client.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_too_large_message_async(connection_str):
    if sys.platform.startswith('darwin'):
        pytest.skip("Skipping on OSX - open issue regarding message size")
    client = EventHubProducerClient.from_connection_string(connection_str)
    try:
        data = EventData(b"A" * 1100000)
        with pytest.raises(ValueError):
            batch = await client.create_batch()
            batch.add(data)
    finally:
        await client.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_null_body_async(connection_str):
    client = EventHubProducerClient.from_connection_string(connection_str)
    try:
        with pytest.raises(ValueError):
            data = EventData(None)
            batch = await client.create_batch()
            batch.add(data)
            await client.send_batch(batch)
    finally:
        await client.close()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_create_batch_with_invalid_hostname_async(invalid_hostname):
    if sys.platform.startswith('darwin'):
        pytest.skip("Skipping on OSX - it keeps reporting 'Unable to set external certificates' "
                    "and blocking other tests")
    client = EventHubProducerClient.from_connection_string(invalid_hostname)
    async with client:
        with pytest.raises(ConnectError):
            await client.create_batch(max_size_in_bytes=300)


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_create_batch_with_too_large_size_async(connection_str):
    client = EventHubProducerClient.from_connection_string(connection_str)
    async with client:
        with pytest.raises(ValueError):
            await client.create_batch(max_size_in_bytes=5 * 1024 * 1024)
