#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os
import pytest
import time
import uuid

from uamqp.message import MessageProperties

from azure.eventhub import EventData, EventHubClient


@pytest.mark.liveTest
def test_iothub_send_single_event(iot_connection_str, device_id):
    client = EventHubClient.from_connection_string(iot_connection_str, network_tracing=False)
    sender = client.create_producer(operation='/messages/devicebound')
    try:
        sender.send(EventData(b"A single event", to_device=device_id))
    finally:
        sender.close()
