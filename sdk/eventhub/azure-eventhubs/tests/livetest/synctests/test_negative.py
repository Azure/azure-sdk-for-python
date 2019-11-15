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
    if sys.platform.startswith('darwin'):
        pytest.skip("Skipping on OSX - it keeps reporting 'Unable to set external certificates' "
                    "and blocking other tests")
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
def test_send_with_invalid_key(live_eventhub):
    conn_str = "Endpoint=sb://{}/;SharedAccessKeyName={};SharedAccessKey={};EntityPath={}".format(
        live_eventhub['hostname'],
        live_eventhub['key_name'],
        'invalid',
        live_eventhub['event_hub'])
    client = EventHubProducerClient.from_connection_string(conn_str)
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


@pytest.mark.liveTest
def test_create_batch_with_invalid_hostname_sync(invalid_hostname):
    client = EventHubProducerClient.from_connection_string(invalid_hostname)
    with client:
        with pytest.raises(ConnectError):
            client.create_batch(max_size=300)


@pytest.mark.liveTest
def test_create_batch_with_too_large_size_sync(connection_str):
    client = EventHubProducerClient.from_connection_string(connection_str)
    with client:
        with pytest.raises(ValueError):
            client.create_batch(max_size=5 * 1024 * 1024)
