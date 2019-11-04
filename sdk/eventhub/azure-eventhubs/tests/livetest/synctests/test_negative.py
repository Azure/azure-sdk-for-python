#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import pytest
import time
import sys

from azure.eventhub import (
    EventData,
    EventPosition,
    AuthenticationError,
    ConnectError,
    EventDataSendError)

from azure.eventhub.client import EventHubClient


@pytest.mark.liveTest
def test_send_with_invalid_hostname(invalid_hostname):
    client = EventHubClient.from_connection_string(invalid_hostname)
    sender = client._create_producer()
    with pytest.raises(AuthenticationError):
        sender.send(EventData("test data"))
    sender.close()
    client.close()


@pytest.mark.liveTest
def test_receive_with_invalid_hostname_sync(invalid_hostname):
    client = EventHubClient.from_connection_string(invalid_hostname)
    receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition("-1"))
    with pytest.raises(AuthenticationError):
        receiver.receive(timeout=5)
    receiver.close()
    client.close()


@pytest.mark.liveTest
def test_send_with_invalid_key(invalid_key):
    client = EventHubClient.from_connection_string(invalid_key)
    sender = client._create_producer()
    with pytest.raises(AuthenticationError):
        sender.send(EventData("test data"))
    sender.close()
    client.close()


@pytest.mark.liveTest
def test_receive_with_invalid_key_sync(invalid_key):
    client = EventHubClient.from_connection_string(invalid_key)
    receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition("-1"))

    with pytest.raises(AuthenticationError):
        receiver.receive(timeout=10)
    receiver.close()
    client.close()


@pytest.mark.liveTest
def test_send_with_invalid_policy(invalid_policy):
    client = EventHubClient.from_connection_string(invalid_policy)
    sender = client._create_producer()
    with pytest.raises(AuthenticationError):
        sender.send(EventData("test data"))
    sender.close()
    client.close()


@pytest.mark.liveTest
def test_receive_with_invalid_policy_sync(invalid_policy):
    client = EventHubClient.from_connection_string(invalid_policy)
    receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition("-1"))
    with pytest.raises(AuthenticationError):
        receiver.receive(timeout=5)
    receiver.close()
    client.close()


@pytest.mark.liveTest
def test_send_partition_key_with_partition_sync(connection_str):
    pytest.skip("Skipped tentatively. Confirm whether to throw ValueError or just warn users")
    client = EventHubClient.from_connection_string(connection_str)
    sender = client._create_producer(partition_id="1")
    try:
        data = EventData(b"Data")
        data._set_partition_key(b"PKey")
        with pytest.raises(ValueError):
            sender.send(data)
    finally:
        sender.close()
        client.close()


@pytest.mark.liveTest
def test_non_existing_entity_sender(connection_str):
    client = EventHubClient.from_connection_string(connection_str, event_hub_path="nemo")
    sender = client._create_producer(partition_id="1")
    with pytest.raises(AuthenticationError):
        sender.send(EventData("test data"))
    sender.close()
    client.close()


@pytest.mark.liveTest
def test_non_existing_entity_receiver(connection_str):
    client = EventHubClient.from_connection_string(connection_str, event_hub_path="nemo")
    receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition("-1"))
    with pytest.raises(AuthenticationError):
        receiver.receive(timeout=5)
    receiver.close()
    client.close()


@pytest.mark.liveTest
def test_receive_from_invalid_partitions_sync(connection_str):
    partitions = ["XYZ", "-1", "1000", "-"]
    for p in partitions:
        client = EventHubClient.from_connection_string(connection_str)
        receiver = client._create_consumer(consumer_group="$default", partition_id=p, event_position=EventPosition("-1"))
        try:
            with pytest.raises(ConnectError):
                receiver.receive(timeout=5)
        finally:
            receiver.close()
            client.close()


@pytest.mark.liveTest
def test_send_to_invalid_partitions(connection_str):
    partitions = ["XYZ", "-1", "1000", "-"]
    for p in partitions:
        client = EventHubClient.from_connection_string(connection_str)
        sender = client._create_producer(partition_id=p)
        try:
            with pytest.raises(ConnectError):
                sender.send(EventData("test data"))
        finally:
            sender.close()
            client.close()


@pytest.mark.liveTest
def test_send_too_large_message(connection_str):
    if sys.platform.startswith('darwin'):
        pytest.skip("Skipping on OSX - open issue regarding message size")
    client = EventHubClient.from_connection_string(connection_str)
    sender = client._create_producer()
    try:
        data = EventData(b"A" * 1100000)
        with pytest.raises(EventDataSendError):
            sender.send(data)
    finally:
        sender.close()
        client.close()


@pytest.mark.liveTest
def test_send_null_body(connection_str):
    client = EventHubClient.from_connection_string(connection_str)
    sender = client._create_producer()
    try:
        with pytest.raises(ValueError):
            data = EventData(None)
            sender.send(data)
    finally:
        sender.close()
        client.close()


@pytest.mark.liveTest
def test_message_body_types(connstr_senders):
    connection_str, senders = connstr_senders
    client = EventHubClient.from_connection_string(connection_str)
    receiver = client._create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition('@latest'))
    try:
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
        receiver.close()
        client.close()


@pytest.mark.liveTest
def test_create_batch_with_invalid_hostname_sync(invalid_hostname):
    client = EventHubClient.from_connection_string(invalid_hostname)
    sender = client._create_producer()
    with pytest.raises(AuthenticationError):
        sender.create_batch(max_size=300)
    sender.close()
    client.close()


@pytest.mark.liveTest
def test_create_batch_with_too_large_size_sync(connection_str):
    client = EventHubClient.from_connection_string(connection_str)
    sender = client._create_producer()
    with pytest.raises(ValueError):
        sender.create_batch(max_size=5 * 1024 * 1024)
    sender.close()
    client.close()
