#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os
import pytest
import time

from azure.eventhub import EventData, EventHubClient


@pytest.mark.liveTest
def test_iothub_receive_sync(iot_connection_str, device_id):
    client = EventHubClient.from_iothub_connection_string(iot_connection_str, debug=True)
    receiver = client.create_receiver(partition_id="0", operation='/messages/events')
    try:
        partitions = client.get_properties()
        assert partitions["partition_ids"] == ["0", "1", "2", "3"]
        received = receiver.receive(timeout=5)
        assert len(received) == 0
    finally:
        receiver.close()
