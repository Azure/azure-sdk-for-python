#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import pytest

from azure.eventhub import EventPosition, EventHubClient


@pytest.mark.liveTest
def test_iothub_receive_sync(iot_connection_str, device_id):
    client = EventHubClient.from_connection_string(iot_connection_str, network_tracing=False)
    receiver = client.create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition("-1"), operation='/messages/events')
    try:
        received = receiver.receive(timeout=10)
        assert len(received) == 0
    finally:
        receiver.close()


@pytest.mark.liveTest
def test_iothub_get_properties_sync(iot_connection_str, device_id):
    client = EventHubClient.from_connection_string(iot_connection_str, network_tracing=False)
    properties = client.get_properties()
    assert properties["partition_ids"] == ["0", "1", "2", "3"]


@pytest.mark.liveTest
def test_iothub_get_partition_ids_sync(iot_connection_str, device_id):
    client = EventHubClient.from_connection_string(iot_connection_str, network_tracing=False)
    partitions = client.get_partition_ids()
    assert partitions == ["0", "1", "2", "3"]


@pytest.mark.liveTest
def test_iothub_get_partition_properties_sync(iot_connection_str, device_id):
    client = EventHubClient.from_connection_string(iot_connection_str, network_tracing=False)
    partition_properties = client.get_partition_properties("0")
    assert partition_properties["id"] == "0"


@pytest.mark.liveTest
def test_iothub_receive_after_mgmt_ops_sync(iot_connection_str, device_id):
    client = EventHubClient.from_connection_string(iot_connection_str, network_tracing=False)
    partitions = client.get_partition_ids()
    assert partitions == ["0", "1", "2", "3"]
    receiver = client.create_consumer(consumer_group="$default", partition_id=partitions[0], event_position=EventPosition("-1"), operation='/messages/events')
    with receiver:
        received = receiver.receive(timeout=10)
        assert len(received) == 0


@pytest.mark.liveTest
def test_iothub_mgmt_ops_after_receive_sync(iot_connection_str, device_id):
    client = EventHubClient.from_connection_string(iot_connection_str, network_tracing=False)
    receiver = client.create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition("-1"), operation='/messages/events')
    with receiver:
        received = receiver.receive(timeout=10)
        assert len(received) == 0

    partitions = client.get_partition_ids()
    assert partitions == ["0", "1", "2", "3"]
