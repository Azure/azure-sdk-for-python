#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os
import asyncio
import pytest
import time

from azure import eventhub
from azure.eventhub import EventData, Offset, EventHubError, EventHubClientAsync


@pytest.mark.asyncio
async def test_receive_end_of_stream_async(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClientAsync.from_connection_string(connection_str, debug=False)
    receiver = client.add_async_receiver("$default", "0", offset=Offset('@latest'))
    await client.run_async()
    try:
        received = await receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Receiving only a single event"))
        received = await receiver.receive(timeout=5)
        assert len(received) == 1

        assert list(received[-1].body)[0] == b"Receiving only a single event"
    except:
        raise
    finally:
        await client.stop_async()


@pytest.mark.asyncio
async def test_receive_with_offset_async(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClientAsync.from_connection_string(connection_str, debug=False)
    receiver = client.add_async_receiver("$default", "0", offset=Offset('@latest'))
    await client.run_async()
    try:
        received = await receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Data"))
        time.sleep(1)
        received = await receiver.receive(timeout=3)
        assert len(received) == 1
        offset = received[0].offset

        offset_receiver = client.add_async_receiver("$default", "0", offset=offset)
        await client.run_async()
        received = await offset_receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Message after offset"))
        received = await offset_receiver.receive(timeout=5)
        assert len(received) == 1
    except:
        raise
    finally:
        await client.stop_async()


@pytest.mark.asyncio
async def test_receive_with_inclusive_offset_async(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClientAsync.from_connection_string(connection_str, debug=False)
    receiver = client.add_async_receiver("$default", "0", offset=Offset('@latest'))
    await client.run_async()
    try:
        received = await receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Data"))
        time.sleep(1)
        received = await receiver.receive(timeout=5)
        assert len(received) == 1
        offset = received[0].offset

        offset_receiver = client.add_async_receiver("$default", "0", offset=Offset(offset.value, inclusive=True))
        await client.run_async()
        received = await offset_receiver.receive(timeout=5)
        assert len(received) == 1
    except:
        raise
    finally:
        await client.stop_async()


@pytest.mark.asyncio
async def test_receive_with_datetime_async(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClientAsync.from_connection_string(connection_str, debug=False)
    receiver = client.add_async_receiver("$default", "0", offset=Offset('@latest'))
    await client.run_async()
    try:
        received = await receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Data"))
        received = await receiver.receive(timeout=5)
        assert len(received) == 1
        offset = received[0].enqueued_time

        offset_receiver = client.add_async_receiver("$default", "0", offset=Offset(offset))
        await client.run_async()
        received = await offset_receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Message after timestamp"))
        time.sleep(1)
        received = await offset_receiver.receive(timeout=5)
        assert len(received) == 1
    except:
        raise
    finally:
        await client.stop_async()


@pytest.mark.asyncio
async def test_receive_with_sequence_no_async(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClientAsync.from_connection_string(connection_str, debug=False)
    receiver = client.add_async_receiver("$default", "0", offset=Offset('@latest'))
    await client.run_async()
    try:
        received = await receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Data"))
        received = await receiver.receive(timeout=5)
        assert len(received) == 1
        offset = received[0].sequence_number

        offset_receiver = client.add_async_receiver("$default", "0", offset=Offset(offset))
        await client.run_async()
        received = await offset_receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Message next in sequence"))
        time.sleep(1)
        received = await offset_receiver.receive(timeout=5)
        assert len(received) == 1
    except:
        raise
    finally:
        await client.stop_async()


@pytest.mark.asyncio
async def test_receive_with_inclusive_sequence_no_async(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClientAsync.from_connection_string(connection_str, debug=False)
    receiver = client.add_async_receiver("$default", "0", offset=Offset('@latest'))
    await client.run_async()
    try:
        received = await receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Data"))
        received = await receiver.receive(timeout=5)
        assert len(received) == 1
        offset = received[0].sequence_number

        offset_receiver = client.add_async_receiver("$default", "0", offset=Offset(offset, inclusive=True))
        await client.run_async()
        received = await offset_receiver.receive(timeout=5)
        assert len(received) == 1
    except:
        raise
    finally:
        await client.stop_async()


@pytest.mark.asyncio
async def test_receive_batch_async(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClientAsync.from_connection_string(connection_str, debug=False)
    receiver = client.add_async_receiver("$default", "0", prefetch=500, offset=Offset('@latest'))
    await client.run_async()
    try:
        received = await receiver.receive(timeout=5)
        assert len(received) == 0
        for i in range(10):
            senders[0].send(EventData(b"Data"))
        received = await receiver.receive(max_batch_size=5, timeout=5)
        assert len(received) == 5
    except:
        raise
    finally:
        await client.stop_async()


async def pump(receiver, sleep=None):
    messages = 0
    count = 0
    if sleep:
        await asyncio.sleep(sleep)
    batch = await receiver.receive(timeout=10)
    while batch:
        count += 1
        if count >= 10:
            break
        messages += len(batch)
        batch = await receiver.receive(timeout=10)
    return messages


@pytest.mark.asyncio
async def test_epoch_receiver_async(connstr_senders):
    connection_str, senders = connstr_senders
    senders[0].send(EventData(b"Receiving only a single event"))

    client = EventHubClientAsync.from_connection_string(connection_str, debug=False)
    receivers = []
    for epoch in [10, 20]:
        receivers.append(client.add_async_epoch_receiver("$default", "0", epoch, prefetch=5))
    try:
        await client.run_async()
        outputs = await asyncio.gather(
            pump(receivers[0]),
            pump(receivers[1]),
            return_exceptions=True)
        assert isinstance(outputs[0], EventHubError)
        assert outputs[1] == 1
    except:
        raise
    finally:
        await client.stop_async()


@pytest.mark.asyncio
async def test_multiple_receiver_async(connstr_senders):
    connection_str, senders = connstr_senders
    senders[0].send(EventData(b"Receiving only a single event"))

    client = EventHubClientAsync.from_connection_string(connection_str, debug=True)
    partitions = await client.get_eventhub_info_async()
    assert partitions["partition_ids"] == ["0", "1"]
    receivers = []
    for i in range(2):
        receivers.append(client.add_async_receiver("$default", "0", prefetch=10))
    try:
        await client.run_async()
        more_partitions = await client.get_eventhub_info_async()
        assert more_partitions["partition_ids"] == ["0", "1"]
        outputs = await asyncio.gather(
            pump(receivers[0]),
            pump(receivers[1]),
            return_exceptions=True)
        assert isinstance(outputs[0], int) and outputs[0] == 1
        assert isinstance(outputs[1], int) and outputs[1] == 1
    except:
        raise
    finally:
        await client.stop_async()


@pytest.mark.asyncio
async def test_epoch_receiver_after_non_epoch_receiver_async(connstr_senders):
    connection_str, senders = connstr_senders
    senders[0].send(EventData(b"Receiving only a single event"))

    client = EventHubClientAsync.from_connection_string(connection_str, debug=False)
    receivers = []
    receivers.append(client.add_async_receiver("$default", "0", prefetch=10))
    receivers.append(client.add_async_epoch_receiver("$default", "0", 15, prefetch=10))
    try:
        await client.run_async()
        outputs = await asyncio.gather(
            pump(receivers[0]),
            pump(receivers[1], sleep=5),
            return_exceptions=True)
        assert isinstance(outputs[0], EventHubError)
        assert isinstance(outputs[1], int) and outputs[1] == 1
    except:
        raise
    finally:
        await client.stop_async()


@pytest.mark.asyncio
async def test_non_epoch_receiver_after_epoch_receiver_async(connstr_senders):
    connection_str, senders = connstr_senders
    senders[0].send(EventData(b"Receiving only a single event"))

    client = EventHubClientAsync.from_connection_string(connection_str, debug=False)
    receivers = []
    receivers.append(client.add_async_epoch_receiver("$default", "0", 15, prefetch=10))
    receivers.append(client.add_async_receiver("$default", "0", prefetch=10))
    try:
        await client.run_async()
        outputs = await asyncio.gather(
            pump(receivers[0]),
            pump(receivers[1]),
            return_exceptions=True)
        assert isinstance(outputs[1], EventHubError)
        assert isinstance(outputs[0], int) and outputs[0] == 1
    except:
        raise
    finally:
        await client.stop_async()

