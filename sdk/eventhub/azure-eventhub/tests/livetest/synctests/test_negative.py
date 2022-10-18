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
    EventDataBatch)
from azure.eventhub.exceptions import (
    ConnectError,
    AuthenticationError,
    EventDataSendError
)
from azure.eventhub import EventHubConsumerClient
from azure.eventhub import EventHubProducerClient
try:
    from azure.eventhub._transport._uamqp_transport import UamqpTransport
except (ImportError, ModuleNotFoundError):
    UamqpTransport = None


@pytest.mark.liveTest
def test_send_batch_with_invalid_hostname(invalid_hostname, uamqp_transport):
    amqp_transport = UamqpTransport if uamqp_transport else None
    if sys.platform.startswith('darwin'):
        pytest.skip("Skipping on OSX - it keeps reporting 'Unable to set external certificates' "
                    "and blocking other tests")
    client = EventHubProducerClient.from_connection_string(invalid_hostname, uamqp_transport=uamqp_transport)
    with client:
        with pytest.raises(ConnectError):
            batch = EventDataBatch()
            batch.add(EventData("test data"))
            client.send_batch(batch)

    # test setting callback
    def on_error(events, pid, err):
        assert len(events) == 1
        assert not pid
        on_error.err = err

    on_error.err = None
    client = EventHubProducerClient.from_connection_string(invalid_hostname, on_error=on_error, uamqp_transport=uamqp_transport)
    with client:
        batch = EventDataBatch()
        batch.add(EventData("test data"))
        client.send_batch(batch)
    assert isinstance(on_error.err, ConnectError)

    on_error.err = None
    client = EventHubProducerClient.from_connection_string(invalid_hostname, on_error=on_error, uamqp_transport=uamqp_transport)
    with client:
        client.send_event(EventData("test data"))
    assert isinstance(on_error.err, ConnectError)


@pytest.mark.liveTest
def test_receive_with_invalid_hostname_sync(invalid_hostname, uamqp_transport):
    def on_event(partition_context, event):
        pass

    client = EventHubConsumerClient.from_connection_string(
        invalid_hostname, consumer_group='$default', uamqp_transport=uamqp_transport
    )
    with client:
        thread = threading.Thread(target=client.receive,
                                  args=(on_event, ))
        thread.start()
        time.sleep(2)
        assert len(client._event_processors) == 1
    thread.join()


@pytest.mark.liveTest
def test_send_batch_with_invalid_key(invalid_key, uamqp_transport):
    client = EventHubProducerClient.from_connection_string(invalid_key, uamqp_transport=uamqp_transport)
    amqp_transport = UamqpTransport if uamqp_transport else None
    try:
        with pytest.raises(ConnectError):
            batch = EventDataBatch()
            batch.add(EventData("test data"))
            client.send_batch(batch)
    finally:
        client.close()


@pytest.mark.liveTest
def test_send_batch_to_invalid_partitions(connection_str, uamqp_transport):
    partitions = ["XYZ", "-1", "1000", "-"]
    for p in partitions:
        client = EventHubProducerClient.from_connection_string(connection_str, uamqp_transport=uamqp_transport)
        try:
            with pytest.raises(ConnectError):
                batch = client.create_batch(partition_id=p)
                batch.add(EventData("test data"))
                client.send_batch(batch)
        finally:
            client.close()


@pytest.mark.liveTest
def test_send_batch_too_large_message(connection_str, uamqp_transport):
    if sys.platform.startswith('darwin'):
        pytest.skip("Skipping on OSX - open issue regarding message size")
    client = EventHubProducerClient.from_connection_string(connection_str, uamqp_transport=uamqp_transport)
    try:
        data = EventData(b"A" * 1100000)
        batch = client.create_batch()
        with pytest.raises(ValueError):
            batch.add(data)
    finally:
        client.close()


@pytest.mark.liveTest
def test_send_batch_null_body(connection_str, uamqp_transport):
    client = EventHubProducerClient.from_connection_string(connection_str, uamqp_transport=uamqp_transport)
    try:
        with pytest.raises(ValueError):
            data = EventData(None)
            batch = client.create_batch()
            batch.add(data)
            client.send_batch(batch)
    finally:
        client.close()


@pytest.mark.liveTest
def test_create_batch_with_invalid_hostname_sync(invalid_hostname, uamqp_transport):
    if sys.platform.startswith('darwin'):
        pytest.skip("Skipping on OSX - it keeps reporting 'Unable to set external certificates' "
                    "and blocking other tests")
    client = EventHubProducerClient.from_connection_string(invalid_hostname, uamqp_transport=uamqp_transport)
    with client:
        with pytest.raises(ConnectError):
            client.create_batch(max_size_in_bytes=300)


@pytest.mark.liveTest
def test_create_batch_with_too_large_size_sync(connection_str, uamqp_transport):
    client = EventHubProducerClient.from_connection_string(connection_str, uamqp_transport=uamqp_transport)
    with client:
        with pytest.raises(ValueError):
            client.create_batch(max_size_in_bytes=5 * 1024 * 1024)
