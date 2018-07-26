#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os
import pytest
import time

from azure import eventhub
from azure.eventhub import EventData, EventHubClient, Offset

def test_iothub_receive_sync(iot_connection_str, device_id):
    client = EventHubClient.from_iothub_connection_string(iot_connection_str, debug=True)
    receiver = client.add_receiver("$default", "0", operation='/messages/events')
    try:
        client.run()
        received = receiver.receive(timeout=5)
        assert len(received) == 0
    finally:
        client.stop()