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

from azure.eventhub import EventData, TransportType
from azure.eventhub.aio import EventHubClient


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_with_partition_key_async(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    sender = client.create_sender()

    data_val = 0
    for partition in [b"a", b"b", b"c", b"d", b"e", b"f"]:
        partition_key = b"test_partition_" + partition
        for i in range(50):
            data = EventData(str(data_val))
            data.partition_key = partition_key
            data_val += 1
            await sender.send(data)

    found_partition_keys = {}
    for index, partition in enumerate(receivers):
        received = partition.receive(timeout=5)
        for message in received:
            try:
                existing = found_partition_keys[message.partition_key]
                assert existing == index
            except KeyError:
                found_partition_keys[message.partition_key] = index


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_and_receive_zero_length_body_async(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    sender = client.create_sender()
    async with sender:
        await sender.send(EventData(""))

    received = []
    for r in receivers:
        received.extend(r.receive(timeout=1))

    assert len(received) == 1
    assert list(received[0].body)[0] == b""


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_single_event_async(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    sender = client.create_sender()
    async with sender:
        await sender.send(EventData(b"A single event"))

    received = []
    for r in receivers:
        received.extend(r.receive(timeout=1))

    assert len(received) == 1
    assert list(received[0].body)[0] == b"A single event"


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_batch_async(connstr_receivers):
    connection_str, receivers = connstr_receivers
    def batched():
        for i in range(10):
            yield EventData("Event number {}".format(i))

    client = EventHubClient.from_connection_string(connection_str, debug=False)
    sender = client.create_sender()
    async with sender:
        await sender.send_batch(batched())

    time.sleep(1)
    received = []
    for r in receivers:
        received.extend(r.receive(timeout=3))

    assert len(received) == 10
    for index, message in enumerate(received):
        assert list(message.body)[0] == "Event number {}".format(index).encode('utf-8')


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_partition_async(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    sender = client.create_sender(partition="1")
    async with sender:
        await sender.send(EventData(b"Data"))

    partition_0 = receivers[0].receive(timeout=2)
    assert len(partition_0) == 0
    partition_1 = receivers[1].receive(timeout=2)
    assert len(partition_1) == 1


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_non_ascii_async(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    sender = client.create_sender(partition="0")
    async with sender:
        await sender.send(EventData("é,è,à,ù,â,ê,î,ô,û"))
        await sender.send(EventData(json.dumps({"foo": "漢字"})))

    partition_0 = receivers[0].receive(timeout=2)
    assert len(partition_0) == 2
    assert partition_0[0].body_as_str() == "é,è,à,ù,â,ê,î,ô,û"
    assert partition_0[1].body_as_json() == {"foo": "漢字"}


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_partition_batch_async(connstr_receivers):
    connection_str, receivers = connstr_receivers

    def batched():
        for i in range(10):
            yield EventData("Event number {}".format(i))

    client = EventHubClient.from_connection_string(connection_str, debug=False)
    sender = client.create_sender(partition="1")
    async with sender:
        await sender.send_batch(batched())

    partition_0 = receivers[0].receive(timeout=2)
    assert len(partition_0) == 0
    partition_1 = receivers[1].receive(timeout=2)
    assert len(partition_1) == 10


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_array_async(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    sender = client.create_sender()
    async with sender:
        await sender.send(EventData([b"A", b"B", b"C"]))

    received = []
    for r in receivers:
        received.extend(r.receive(timeout=1))

    assert len(received) == 1
    assert list(received[0].body) == [b"A", b"B", b"C"]


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_multiple_clients_async(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    sender_0 = client.create_sender(partition="0")
    sender_1 = client.create_sender(partition="1")
    async with sender_0 and sender_1:
        await sender_0.send(EventData(b"Message 0"))
        await sender_1.send(EventData(b"Message 1"))

    partition_0 = receivers[0].receive(timeout=2)
    assert len(partition_0) == 1
    partition_1 = receivers[1].receive(timeout=2)
    assert len(partition_1) == 1


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_batch_with_app_prop_async(connstr_receivers):
    # pytest.skip("Waiting on uAMQP release")
    connection_str, receivers = connstr_receivers
    app_prop_key = "raw_prop"
    app_prop_value = "raw_value"
    app_prop = {app_prop_key: app_prop_value}

    def batched():
        for i in range(10):
            ed = EventData("Event number {}".format(i))
            ed.application_properties = app_prop
            yield "Event number {}".format(i)
        for i in range(10, 20):
            ed = EventData("Event number {}".format(i))
            ed.application_properties = app_prop
            yield "Event number {}".format(i)

    client = EventHubClient.from_connection_string(connection_str, debug=False)
    sender = client.create_sender()
    async with sender:
        await sender.send_batch(batched())

    time.sleep(1)

    received = []
    for r in receivers:
        received.extend(r.receive(timeout=3))

    assert len(received) == 20
    for index, message in enumerate(received):
        assert list(message.body)[0] == "Event number {}".format(index).encode('utf-8')
        assert (app_prop_key.encode('utf-8') in message.application_properties) \
            and (dict(message.application_properties)[app_prop_key.encode('utf-8')] == app_prop_value.encode('utf-8'))


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_over_websocket_async(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(connection_str, transport_type=TransportType.AmqpOverWebsocket, debug=False)
    sender = client.create_sender()

    event_list = []
    for i in range(20):
        event_list.append(EventData("Event Number {}".format(i)))

    async with sender:
        await sender.send(event_list)

    time.sleep(1)
    received = []
    for r in receivers:
        received.extend(r.receive(timeout=3))

    assert len(received) == 20
