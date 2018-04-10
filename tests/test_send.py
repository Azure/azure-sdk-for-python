#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os
import pytest

from azure import eventhub
from azure.eventhub import EventData, EventHubClient


def test_send_with_partition_key(connection_str, receivers):
    pytest.skip("")
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    sender = client.add_sender()
    client.run()

    data_val = 0
    for partition in [b"a", b"b", b"c"]:
        partition_key = b"test_partition_" + partition
        for i in range(5):
            data = EventData(str(data_val))
            data.partition_key = partition_key
            data_val += 1
            sender.send(data)
    client.stop()

    found_partition_keys = {}
    for index, partition in enumerate(receivers):
        received = partition.receive(timeout=5)
        for message in received:
            try:
                existing = found_partition_keys[message.partition_key]
                assert existing == index
            except KeyError:
                found_partition_keys[message.partition_key] = index


def test_send_and_receive_zero_length_body(connection_str, receivers):
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    sender = client.add_sender()
    client.run()
    sender.send(EventData(""))
    client.stop()

    received = []
    for r in receivers:
        received.extend(r.receive(timeout=1))

    assert len(received) == 1
    assert received[0].body == None


def test_send_single_event(connection_str, receivers):
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    sender = client.add_sender()
    client.run()
    sender.send(EventData(b"A single event"))
    client.stop()

    received = []
    for r in receivers:
        received.extend(r.receive(timeout=1))

    assert len(received) == 1
    assert list(received[0].body)[0] == b"A single event"


def test_send_batch(connection_str, receivers):
    def batched():
        for i in range(10):
            yield "Event number {}".format(i)

    client = EventHubClient.from_connection_string(connection_str, debug=False)
    sender = client.add_sender()
    client.run()
    sender.send(EventData(batch=batched()))
    client.stop()

    time.sleep(1)
    received = []
    for r in receivers:
        received.extend(r.receive(timeout=3))

    assert len(received) == 10
    for index, message in enumerate(received):
        assert list(message.body)[0] == "Event number {}".format(index).encode('utf-8')


def test_send_partition(connection_str, receivers):
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    sender = client.add_sender(partition="1")
    client.run()
    sender.send(EventData(b"Data"))
    client.stop()

    partition_0 = receivers[0].receive(timeout=2)
    assert len(partition_0) == 0
    partition_1 = receivers[1].receive(timeout=2)
    assert len(partition_1) == 1


def test_send_partition_batch(connection_str, receivers):
    def batched():
        for i in range(10):
            yield "Event number {}".format(i)

    client = EventHubClient.from_connection_string(connection_str, debug=False)
    sender = client.add_sender(partition="1")
    client.run()
    sender.send(EventData(batch=batched()))
    client.stop()

    partition_0 = receivers[0].receive(timeout=2)
    assert len(partition_0) == 0
    partition_1 = receivers[1].receive(timeout=2)
    assert len(partition_1) == 10


def test_send_array(connection_str, receivers):
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    sender = client.add_sender()
    client.run()
    sender.send(EventData([b"A", b"B", b"C"]))
    client.stop()

    received = []
    for r in receivers:
        received.extend(r.receive(timeout=1))

    assert len(received) == 1
    assert list(received[0].body) == [b"A", b"B", b"C"]


def test_send_multiple_clients(connection_str, receivers):
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    sender_0 = client.add_sender(partition="0")
    sender_1 = client.add_sender(partition="1")
    client.run()
    sender_0.send(EventData(b"Message 0"))
    sender_1.send(EventData(b"Message 1"))
    client.stop()

    partition_0 = receivers[0].receive(timeout=2)
    assert len(partition_0) == 1
    partition_1 = receivers[1].receive(timeout=2)
    assert len(partition_1) == 1