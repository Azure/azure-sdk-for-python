# -- coding: utf-8 --
#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os
import asyncio
import pytest
import time
import json

from azure.eventhub import EventData, TransportType, EventDataBatch
from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub.exceptions import EventDataSendError

@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_with_partition_key_async(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubProducerClient.from_connection_string(connection_str)
    async with client:
        data_val = 0
        for partition in [b"a", b"b", b"c", b"d", b"e", b"f"]:
            partition_key = b"test_partition_" + partition
            for i in range(50):
                batch = await client.create_batch(partition_key=partition_key)
                batch.add(EventData(str(data_val)))
                data_val += 1
                await client.send_batch(batch)

        await client.send_batch(await client.create_batch())

    found_partition_keys = {}
    for index, partition in enumerate(receivers):
        received = partition.receive_message_batch(timeout=5000)
        for message in received:
            try:
                event_data = EventData._from_message(message)
                existing = found_partition_keys[event_data.partition_key]
                assert existing == index
            except KeyError:
                found_partition_keys[event_data.partition_key] = index


@pytest.mark.parametrize("payload", [b"", b"A single event"])
@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_and_receive_small_body_async(connstr_receivers, payload):
    connection_str, receivers = connstr_receivers
    client = EventHubProducerClient.from_connection_string(connection_str)
    async with client:
        batch = await client.create_batch()
        batch.add(EventData(payload))
        await client.send_batch(batch)
    received = []
    for r in receivers:
        received.extend([EventData._from_message(x) for x in r.receive_message_batch(timeout=5000)])

    assert len(received) == 1
    assert list(received[0].body)[0] == payload


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_partition_async(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubProducerClient.from_connection_string(connection_str)
    async with client:
        batch = await client.create_batch(partition_id="1")
        batch.add(EventData(b"Data"))
        await client.send_batch(batch)

    partition_0 = receivers[0].receive_message_batch(timeout=5000)
    assert len(partition_0) == 0
    partition_1 = receivers[1].receive_message_batch(timeout=5000)
    assert len(partition_1) == 1


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_non_ascii_async(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubProducerClient.from_connection_string(connection_str)
    async with client:
        batch = await client.create_batch(partition_id="0")
        batch.add(EventData(u"é,è,à,ù,â,ê,î,ô,û"))
        batch.add(EventData(json.dumps({"foo": u"漢字"})))
        await client.send_batch(batch)
    await asyncio.sleep(1)
    # receive_message_batch() returns immediately once it receives any messages before the max_batch_size
    # and timeout reach. Could be 1, 2, or any number between 1 and max_batch_size.
    # So call it twice to ensure the two events are received.
    partition_0 = [EventData._from_message(x) for x in receivers[0].receive_message_batch(timeout=5000)] + \
                  [EventData._from_message(x) for x in receivers[0].receive_message_batch(timeout=5000)]

    assert len(partition_0) == 2
    assert partition_0[0].body_as_str() == u"é,è,à,ù,â,ê,î,ô,û"
    assert partition_0[1].body_as_json() == {"foo": u"漢字"}


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_multiple_partition_with_app_prop_async(connstr_receivers):
    connection_str, receivers = connstr_receivers
    app_prop_key = "raw_prop"
    app_prop_value = "raw_value"
    app_prop = {app_prop_key: app_prop_value}
    client = EventHubProducerClient.from_connection_string(connection_str)
    async with client:
        ed0 = EventData(b"Message 0")
        ed0.properties = app_prop
        batch = await client.create_batch(partition_id="0")
        batch.add(ed0)
        await client.send_batch(batch)

        ed1 = EventData(b"Message 1")
        ed1.properties = app_prop
        batch = await client.create_batch(partition_id="1")
        batch.add(ed1)
        await client.send_batch(batch)

    partition_0 = [EventData._from_message(x) for x in receivers[0].receive_message_batch(timeout=5000)]
    assert len(partition_0) == 1
    assert partition_0[0].properties[b"raw_prop"] == b"raw_value"
    partition_1 = [EventData._from_message(x) for x in receivers[1].receive_message_batch(timeout=5000)]
    assert len(partition_1) == 1
    assert partition_1[0].properties[b"raw_prop"] == b"raw_value"


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_over_websocket_async(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubProducerClient.from_connection_string(connection_str,
                                                           transport_type=TransportType.AmqpOverWebsocket)

    async with client:
        batch = await client.create_batch(partition_id="0")
        batch.add(EventData("Event Data"))
        await client.send_batch(batch)

    time.sleep(1)
    received = []
    received.extend(receivers[0].receive_message_batch(max_batch_size=5, timeout=10000))
    assert len(received) == 1


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_with_create_event_batch_async(connstr_receivers):
    connection_str, receivers = connstr_receivers
    app_prop_key = "raw_prop"
    app_prop_value = "raw_value"
    app_prop = {app_prop_key: app_prop_value}
    client = EventHubProducerClient.from_connection_string(connection_str,
                                                           transport_type=TransportType.AmqpOverWebsocket)
    async with client:
        event_data_batch = await client.create_batch(max_size_in_bytes=100000)
        while True:
            try:
                ed = EventData('A single event data')
                ed.properties = app_prop
                event_data_batch.add(ed)
            except ValueError:
                break
        await client.send_batch(event_data_batch)
        received = []
        for r in receivers:
            received.extend(r.receive_message_batch(timeout=10000))
        assert len(received) >= 1
        assert EventData._from_message(received[0]).properties[b"raw_prop"] == b"raw_value"



@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_list_async(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubProducerClient.from_connection_string(connection_str)
    payload = "A1"
    async with client:
        await client.send_batch([EventData(payload)])
    received = []
    for r in receivers:
        received.extend([EventData._from_message(x) for x in r.receive_message_batch(timeout=10000)])

    assert len(received) == 1
    assert received[0].body_as_str() == payload


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_list_partition_async(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubProducerClient.from_connection_string(connection_str)
    payload = "A1"
    async with client:
        await client.send_batch([EventData(payload)], partition_id="0")
        message = receivers[0].receive_message_batch(timeout=10000)[0]
        received = EventData._from_message(message)
    assert received.body_as_str() == payload


@pytest.mark.parametrize("to_send, exception_type",
                         [([EventData("A"*1024)]*1100, ValueError),
                          ("any str", AttributeError)
                          ])
@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_list_wrong_data_async(connection_str, to_send, exception_type):
    client = EventHubProducerClient.from_connection_string(connection_str)
    async with client:
        with pytest.raises(exception_type):
            await client.send_batch(to_send)


@pytest.mark.parametrize("partition_id, partition_key", [("0", None), (None, "pk")])
async def test_send_batch_pid_pk_async(invalid_hostname, partition_id, partition_key):
    # Use invalid_hostname because this is not a live test.
    client = EventHubProducerClient.from_connection_string(invalid_hostname)
    batch = EventDataBatch(partition_id=partition_id, partition_key=partition_key)
    async with client:
        with pytest.raises(TypeError):
            await client.send_batch(batch, partition_id=partition_id, partition_key=partition_key)
