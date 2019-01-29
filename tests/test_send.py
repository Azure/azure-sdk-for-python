# -- coding: utf-8 --
#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os
import pytest
import time
import json
import sys

from azure import eventhub
from azure.eventhub import EventData, EventHubClient


def test_send_with_partition_key(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    sender = client.add_sender()
    try:
        client.run()

        data_val = 0
        for partition in [b"a", b"b", b"c", b"d", b"e", b"f"]:
            partition_key = b"test_partition_" + partition
            for i in range(50):
                data = EventData(str(data_val))
                data.partition_key = partition_key
                data_val += 1
                sender.send(data)
    except:
        raise
    finally:
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


def test_send_and_receive_large_body_size(connstr_receivers):
    if sys.platform.startswith('darwin'):
        pytest.skip("Skipping on OSX - open issue regarding message size")
    connection_str, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    sender = client.add_sender()
    try:
        client.run()
        payload = 250 * 1024
        sender.send(EventData("A" * payload))
    except:
        raise
    finally:
        client.stop()

    received = []
    for r in receivers:
        received.extend(r.receive(timeout=4))

    assert len(received) == 1
    assert len(list(received[0].body)[0]) == payload


def test_send_and_receive_zero_length_body(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    sender = client.add_sender()
    try:
        client.run()
        sender.send(EventData(""))
    except:
        raise
    finally:
        client.stop()

    received = []
    for r in receivers:
        received.extend(r.receive(timeout=1))

    assert len(received) == 1
    assert list(received[0].body)[0] == b""


def test_send_single_event(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    sender = client.add_sender()
    try:
        client.run()
        sender.send(EventData(b"A single event"))
    except:
        raise
    finally:
        client.stop()

    received = []
    for r in receivers:
        received.extend(r.receive(timeout=1))

    assert len(received) == 1
    assert list(received[0].body)[0] == b"A single event"


def test_send_batch_sync(connstr_receivers):
    connection_str, receivers = connstr_receivers
    def batched():
        for i in range(10):
            yield "Event number {}".format(i)

    client = EventHubClient.from_connection_string(connection_str, debug=False)
    sender = client.add_sender()
    try:
        client.run()
        sender.send(EventData(batch=batched()))
    except:
        raise
    finally:
        client.stop()

    time.sleep(1)
    received = []
    for r in receivers:
        received.extend(r.receive(timeout=3))

    assert len(received) == 10
    for index, message in enumerate(received):
        assert list(message.body)[0] == "Event number {}".format(index).encode('utf-8')


def test_send_partition(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    sender = client.add_sender(partition="1")
    try:
        client.run()
        sender.send(EventData(b"Data"))
    except:
        raise
    finally:
        client.stop()

    partition_0 = receivers[0].receive(timeout=2)
    assert len(partition_0) == 0
    partition_1 = receivers[1].receive(timeout=2)
    assert len(partition_1) == 1


def test_send_non_ascii(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    sender = client.add_sender(partition="0")
    try:
        client.run()
        sender.send(EventData(u"é,è,à,ù,â,ê,î,ô,û"))
        sender.send(EventData(json.dumps({"foo": u"漢字"})))
    except:
        raise
    finally:
        client.stop()

    partition_0 = receivers[0].receive(timeout=2)
    assert len(partition_0) == 2
    assert partition_0[0].body_as_str() == u"é,è,à,ù,â,ê,î,ô,û"
    assert partition_0[1].body_as_json() == {"foo": u"漢字"}


def test_send_partition_batch(connstr_receivers):
    connection_str, receivers = connstr_receivers
    def batched():
        for i in range(10):
            yield "Event number {}".format(i)

    client = EventHubClient.from_connection_string(connection_str, debug=False)
    sender = client.add_sender(partition="1")
    try:
        client.run()
        sender.send(EventData(batch=batched()))
        time.sleep(1)
    except:
        raise
    finally:
        client.stop()

    partition_0 = receivers[0].receive(timeout=2)
    assert len(partition_0) == 0
    partition_1 = receivers[1].receive(timeout=2)
    assert len(partition_1) == 10


def test_send_array_sync(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(connection_str, debug=True)
    sender = client.add_sender()
    try:
        client.run()
        sender.send(EventData([b"A", b"B", b"C"]))
    except:
        raise
    finally:
        client.stop()

    received = []
    for r in receivers:
        received.extend(r.receive(timeout=1))

    assert len(received) == 1
    assert list(received[0].body) == [b"A", b"B", b"C"]


def test_send_multiple_clients(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    sender_0 = client.add_sender(partition="0")
    sender_1 = client.add_sender(partition="1")
    try:
        client.run()
        sender_0.send(EventData(b"Message 0"))
        sender_1.send(EventData(b"Message 1"))
    except:
        raise
    finally:
        client.stop()

    partition_0 = receivers[0].receive(timeout=2)
    assert len(partition_0) == 1
    partition_1 = receivers[1].receive(timeout=2)
    assert len(partition_1) == 1