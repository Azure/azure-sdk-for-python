#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os
import pytest
import time
import sys

from azure import eventhub
from azure.eventhub import (
    EventData,
    Offset,
    EventHubError,
    EventHubClient)


def test_send_with_invalid_hostname(invalid_hostname, connstr_receivers):
    _, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(invalid_hostname, debug=False)
    sender = client.add_sender()
    with pytest.raises(EventHubError):
        client.run()


def test_receive_with_invalid_hostname_sync(invalid_hostname):
    client = EventHubClient.from_connection_string(invalid_hostname, debug=True)
    receiver = client.add_receiver("$default", "0")
    with pytest.raises(EventHubError):
        client.run()


def test_send_with_invalid_key(invalid_key, connstr_receivers):
    _, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(invalid_key, debug=False)
    sender = client.add_sender()
    with pytest.raises(EventHubError):
        client.run()


def test_receive_with_invalid_key_sync(invalid_key):
    client = EventHubClient.from_connection_string(invalid_key, debug=True)
    receiver = client.add_receiver("$default", "0")
    with pytest.raises(EventHubError):
        client.run()


def test_send_with_invalid_policy(invalid_policy, connstr_receivers):
    _, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(invalid_policy, debug=False)
    sender = client.add_sender()
    with pytest.raises(EventHubError):
        client.run()


def test_receive_with_invalid_policy_sync(invalid_policy):
    client = EventHubClient.from_connection_string(invalid_policy, debug=True)
    receiver = client.add_receiver("$default", "0")
    with pytest.raises(EventHubError):
        client.run()


def test_send_partition_key_with_partition_sync(connection_str):
    client = EventHubClient.from_connection_string(connection_str, debug=True)
    sender = client.add_sender(partition="1")
    try:
        client.run()
        data = EventData(b"Data")
        data.partition_key = b"PKey"
        with pytest.raises(ValueError):
            sender.send(data)
    finally:
        client.stop()


def test_non_existing_entity_sender(connection_str):
    client = EventHubClient.from_connection_string(connection_str, eventhub="nemo", debug=False)
    sender = client.add_sender(partition="1")
    with pytest.raises(EventHubError):
        client.run()


def test_non_existing_entity_receiver(connection_str):
    client = EventHubClient.from_connection_string(connection_str, eventhub="nemo", debug=False)
    receiver = client.add_receiver("$default", "0")
    with pytest.raises(EventHubError):
        client.run()


def test_receive_from_invalid_partitions_sync(connection_str):
    partitions = ["XYZ", "-1", "1000", "-" ]
    for p in partitions:
        client = EventHubClient.from_connection_string(connection_str, debug=True)
        receiver = client.add_receiver("$default", p)
        try:
            with pytest.raises(EventHubError):
                client.run()
                receiver.receive(timeout=10)
        finally:
            client.stop()


def test_send_to_invalid_partitions(connection_str):
    partitions = ["XYZ", "-1", "1000", "-" ]
    for p in partitions:
        client = EventHubClient.from_connection_string(connection_str, debug=False)
        sender = client.add_sender(partition=p)
        try:
            with pytest.raises(EventHubError):
                client.run()
        finally:
            client.stop()


def test_send_too_large_message(connection_str):
    if sys.platform.startswith('darwin'):
        pytest.skip("Skipping on OSX - open issue regarding message size")
    client = EventHubClient.from_connection_string(connection_str, debug=True)
    sender = client.add_sender()
    try:
        client.run()
        data = EventData(b"A" * 300000)
        with pytest.raises(EventHubError):
            sender.send(data)
    finally:
        client.stop()


def test_send_null_body(connection_str):
    partitions = ["XYZ", "-1", "1000", "-" ]
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    sender = client.add_sender()
    try:
        client.run()
        with pytest.raises(ValueError):
            data = EventData(None)
            sender.send(data)
    finally:
        client.stop()


def test_message_body_types(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str, debug=False)
    receiver = client.add_receiver("$default", "0", offset=Offset('@latest'))
    try:
        client.run()

        received = receiver.receive(timeout=5)
        assert len(received) == 0
        senders[0].send(EventData(b"Bytes Data"))
        time.sleep(1)
        received = receiver.receive(timeout=5)
        assert len(received) == 1
        assert list(received[0].body) == [b'Bytes Data']
        assert received[0].body_as_str() == "Bytes Data"
        with pytest.raises(TypeError):
            received[0].body_as_json()

        senders[0].send(EventData("Str Data"))
        time.sleep(1)
        received = receiver.receive(timeout=5)
        assert len(received) == 1
        assert list(received[0].body) == [b'Str Data']
        assert received[0].body_as_str() == "Str Data"
        with pytest.raises(TypeError):
            received[0].body_as_json()

        senders[0].send(EventData(b'{"test_value": "JSON bytes data", "key1": true, "key2": 42}'))
        time.sleep(1)
        received = receiver.receive(timeout=5)
        assert len(received) == 1
        assert list(received[0].body) == [b'{"test_value": "JSON bytes data", "key1": true, "key2": 42}']
        assert received[0].body_as_str() == '{"test_value": "JSON bytes data", "key1": true, "key2": 42}'
        assert received[0].body_as_json() == {"test_value": "JSON bytes data", "key1": True, "key2": 42}

        senders[0].send(EventData('{"test_value": "JSON str data", "key1": true, "key2": 42}'))
        time.sleep(1)
        received = receiver.receive(timeout=5)
        assert len(received) == 1
        assert list(received[0].body) == [b'{"test_value": "JSON str data", "key1": true, "key2": 42}']
        assert received[0].body_as_str() == '{"test_value": "JSON str data", "key1": true, "key2": 42}'
        assert received[0].body_as_json() == {"test_value": "JSON str data", "key1": True, "key2": 42}

        senders[0].send(EventData(42))
        time.sleep(1)
        received = receiver.receive(timeout=5)
        assert len(received) == 1
        assert received[0].body_as_str() == "42"
        assert received[0].body == 42
    except:
        raise
    finally:
        client.stop()