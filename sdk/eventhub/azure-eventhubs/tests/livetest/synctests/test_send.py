# -- coding: utf-8 --
#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import pytest
import time
import json
import sys

from azure.eventhub import EventData, TransportType
from azure.eventhub.client import EventHubClient


@pytest.mark.liveTest
def test_send_with_partition_key(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(connection_str)
    sender = client._create_producer()
    with sender:
        data_val = 0
        for partition in [b"a", b"b", b"c", b"d", b"e", b"f"]:
            partition_key = b"test_partition_" + partition
            for i in range(50):
                data = EventData(str(data_val))
                #data.partition_key = partition_key
                data_val += 1
                sender.send(data, partition_key=partition_key)

    found_partition_keys = {}
    for index, partition in enumerate(receivers):
        received = partition.receive(timeout=5)
        for message in received:
            try:
                existing = found_partition_keys[message.partition_key]
                assert existing == index
            except KeyError:
                found_partition_keys[message.partition_key] = index
    client.close()


@pytest.mark.liveTest
def test_send_and_receive_large_body_size(connstr_receivers):
    if sys.platform.startswith('darwin'):
        pytest.skip("Skipping on OSX - open issue regarding message size")
    connection_str, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(connection_str)
    sender = client._create_producer()
    with sender:
        payload = 250 * 1024
        sender.send(EventData("A" * payload))

    received = []
    for r in receivers:
        received.extend(r.receive(timeout=10))

    assert len(received) == 1
    assert len(list(received[0].body)[0]) == payload
    client.close()


@pytest.mark.liveTest
def test_send_and_receive_zero_length_body(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(connection_str)
    sender = client._create_producer()
    with sender:
        sender.send(EventData(""))

    received = []
    for r in receivers:
        received.extend(r.receive(timeout=1))

    assert len(received) == 1
    assert list(received[0].body)[0] == b""
    client.close()


@pytest.mark.liveTest
def test_send_single_event(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(connection_str)
    sender = client._create_producer()
    with sender:
        sender.send(EventData(b"A single event"))

    received = []
    for r in receivers:
        received.extend(r.receive(timeout=1))

    assert len(received) == 1
    assert list(received[0].body)[0] == b"A single event"
    client.close()


@pytest.mark.liveTest
def test_send_batch_sync(connstr_receivers):
    connection_str, receivers = connstr_receivers

    def batched():
        for i in range(10):
            yield EventData("Event number {}".format(i))

    client = EventHubClient.from_connection_string(connection_str)
    sender = client._create_producer()
    with sender:
        sender.send(batched())

    time.sleep(1)
    received = []
    for r in receivers:
        received.extend(r.receive(timeout=3))

    assert len(received) == 10
    for index, message in enumerate(received):
        assert list(message.body)[0] == "Event number {}".format(index).encode('utf-8')
    client.close()


@pytest.mark.liveTest
def test_send_partition(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(connection_str)
    sender = client._create_producer(partition_id="1")
    with sender:
        sender.send(EventData(b"Data"))

    partition_0 = receivers[0].receive(timeout=2)
    assert len(partition_0) == 0
    partition_1 = receivers[1].receive(timeout=2)
    assert len(partition_1) == 1
    client.close()


@pytest.mark.liveTest
def test_send_non_ascii(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(connection_str)
    sender = client._create_producer(partition_id="0")
    with sender:
        sender.send(EventData(u"é,è,à,ù,â,ê,î,ô,û"))
        sender.send(EventData(json.dumps({"foo": u"漢字"})))
    time.sleep(1)
    partition_0 = receivers[0].receive(timeout=2)
    assert len(partition_0) == 2
    assert partition_0[0].body_as_str() == u"é,è,à,ù,â,ê,î,ô,û"
    assert partition_0[1].body_as_json() == {"foo": u"漢字"}
    client.close()


@pytest.mark.liveTest
def test_send_partition_batch(connstr_receivers):
    connection_str, receivers = connstr_receivers

    def batched():
        for i in range(10):
            yield EventData("Event number {}".format(i))

    client = EventHubClient.from_connection_string(connection_str)
    sender = client._create_producer(partition_id="1")
    with sender:
        sender.send(batched())
        time.sleep(1)

    partition_0 = receivers[0].receive(timeout=2)
    assert len(partition_0) == 0
    partition_1 = receivers[1].receive(timeout=2)
    assert len(partition_1) == 10
    client.close()


@pytest.mark.liveTest
def test_send_array_sync(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(connection_str)
    sender = client._create_producer()
    with sender:
        sender.send(EventData([b"A", b"B", b"C"]))

    received = []
    for r in receivers:
        received.extend(r.receive(timeout=1))

    assert len(received) == 1
    assert list(received[0].body) == [b"A", b"B", b"C"]
    client.close()


@pytest.mark.liveTest
def test_send_multiple_clients(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(connection_str)
    sender_0 = client._create_producer(partition_id="0")
    sender_1 = client._create_producer(partition_id="1")
    with sender_0:
        sender_0.send(EventData(b"Message 0"))
    with sender_1:
        sender_1.send(EventData(b"Message 1"))

    partition_0 = receivers[0].receive(timeout=2)
    assert len(partition_0) == 1
    partition_1 = receivers[1].receive(timeout=2)
    assert len(partition_1) == 1
    client.close()


@pytest.mark.liveTest
def test_send_batch_with_app_prop_sync(connstr_receivers):
    connection_str, receivers = connstr_receivers
    app_prop_key = "raw_prop"
    app_prop_value = "raw_value"
    app_prop = {app_prop_key: app_prop_value}

    def batched():
        for i in range(10):
            ed = EventData("Event number {}".format(i))
            ed.application_properties = app_prop
            yield ed
        for i in range(10, 20):
            ed = EventData("Event number {}".format(i))
            ed.application_properties = app_prop
            yield ed

    client = EventHubClient.from_connection_string(connection_str)
    sender = client._create_producer()
    with sender:
        sender.send(batched())

    time.sleep(1)

    received = []
    for r in receivers:
        received.extend(r.receive(timeout=3))

    assert len(received) == 20
    for index, message in enumerate(received):
        assert list(message.body)[0] == "Event number {}".format(index).encode('utf-8')
        assert (app_prop_key.encode('utf-8') in message.application_properties) \
            and (dict(message.application_properties)[app_prop_key.encode('utf-8')] == app_prop_value.encode('utf-8'))
    client.close()


@pytest.mark.liveTest
def test_send_over_websocket_sync(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(connection_str, transport_type=TransportType.AmqpOverWebsocket)
    sender = client._create_producer()

    event_list = []
    for i in range(20):
        event_list.append(EventData("Event Number {}".format(i)))

    with sender:
        sender.send(event_list)

    time.sleep(1)
    received = []
    for r in receivers:
        received.extend(r.receive(timeout=3))

    assert len(received) == 20
    client.close()


@pytest.mark.liveTest
def test_send_with_create_event_batch_sync(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(connection_str, transport_type=TransportType.AmqpOverWebsocket)
    sender = client._create_producer()

    event_data_batch = sender.create_batch(max_size=100000)
    while True:
        try:
            event_data_batch.try_add(EventData('A single event data'))
        except ValueError:
            break

    sender.send(event_data_batch)

    event_data_batch = sender.create_batch(max_size=100000)
    while True:
        try:
            event_data_batch.try_add(EventData('A single event data'))
        except ValueError:
            break

    sender.send(event_data_batch)
    sender.close()
    client.close()
