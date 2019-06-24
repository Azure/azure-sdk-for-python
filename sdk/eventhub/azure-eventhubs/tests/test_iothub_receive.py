#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os
import pytest
import time

from azure.eventhub import EventData, EventPosition, EventHubClient


@pytest.mark.liveTest
def test_iothub_receive_sync(iot_connection_str, device_id):
    client = EventHubClient.from_connection_string(iot_connection_str, network_tracing=False)
    receiver = client.create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition("-1"), operation='/messages/events')
    receiver._open()
    try:
        partitions = client.get_properties()
        assert len(partitions["partition_ids"]) >= 2
        received = receiver.receive(timeout=5)
        assert len(received) == 0
    finally:
        receiver.close()
