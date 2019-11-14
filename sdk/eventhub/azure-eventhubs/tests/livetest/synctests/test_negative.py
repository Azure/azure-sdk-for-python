#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import pytest
import time
import sys
import threading

from azure.eventhub import (
    EventData,
    EventPosition,
    AuthenticationError,
    ConnectError,
    EventDataSendError)

from azure.eventhub import EventHubConsumerClient
from azure.eventhub import EventHubProducerClient


@pytest.mark.liveTest
def test_send_with_invalid_hostname(invalid_hostname):
    client = EventHubProducerClient.from_connection_string(invalid_hostname)
    with client:
        with pytest.raises(ConnectError):
            client.send(EventData("test data"))


@pytest.mark.liveTest
def test_receive_with_invalid_hostname_sync(invalid_hostname):
    def on_event(partition_context, event):
        pass

    client = EventHubConsumerClient.from_connection_string(invalid_hostname)
    with client:
        thread = threading.Thread(target=client.receive,
                                  args=(on_event, ),
                                  kwargs={"consumer_group": '$default'})
        thread.start()
        time.sleep(2)
        assert len(client._event_processors) == 1
    thread.join()


@pytest.mark.liveTest
def test_send_with_invalid_key(invalid_key):
    client = EventHubProducerClient.from_connection_string(invalid_key)
    with pytest.raises(ConnectError):
        client.send(EventData("test data"))
    client.close()


@pytest.mark.liveTest
def test_send_to_invalid_partitions(connection_str):
    partitions = ["XYZ", "-1", "1000", "-"]
    for p in partitions:
        client = EventHubProducerClient.from_connection_string(connection_str)
        try:
            with pytest.raises(ConnectError):
                client.send(EventData("test data"), partition_id=p)
        finally:
            client.close()


@pytest.mark.liveTest
def test_send_too_large_message(connection_str):
    if sys.platform.startswith('darwin'):
        pytest.skip("Skipping on OSX - open issue regarding message size")
    client = EventHubProducerClient.from_connection_string(connection_str)
    try:
        data = EventData(b"A" * 1100000)
        with pytest.raises(EventDataSendError):
            client.send(data)
    finally:
        client.close()


@pytest.mark.liveTest
def test_send_null_body(connection_str):
    client = EventHubProducerClient.from_connection_string(connection_str)
    try:
        with pytest.raises(ValueError):
            data = EventData(None)
            client.send(data)
    finally:
        client.close()


'''
This can be turned into unit test of EventData.
@pytest.mark.liveTest
def test_message_body_types(connstr_senders):
    def on_events(partition_context, events):
        on_events.called = True
        pass
    
    connection_str, senders = connstr_senders
    client = EventHubConsumerClient.from_connection_string(connection_str)
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
'''

@pytest.mark.liveTest
def test_create_batch_with_invalid_hostname_sync(invalid_hostname):
    client = EventHubProducerClient.from_connection_string(invalid_hostname)
    with pytest.raises(ConnectError):
        client.create_batch(max_size=300)
    client.close()


@pytest.mark.liveTest
def test_create_batch_with_too_large_size_sync(connection_str):
    client = EventHubProducerClient.from_connection_string(connection_str)
    with pytest.raises(ValueError):
        client.create_batch(max_size=5 * 1024 * 1024)
    client.close()
