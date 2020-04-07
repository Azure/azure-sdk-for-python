# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show receiving events from an IoT Hub partition.
This example is for Python Event Hubs SDK version 1.x.
If you use the latest Event Hubs SDK version 5.x, the example code is
at https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventhub/azure-eventhub/samples/async_samples/iot_hub_connection_string_receive_async.py
"""
from azure import eventhub
from azure.eventhub import EventData, EventHubClient, Offset

import os
import logging
logger = logging.getLogger('azure.eventhub')

iot_connection_str = os.environ['IOTHUB_CONNECTION_STR']

client = EventHubClient.from_iothub_connection_string(iot_connection_str, debug=True)
receiver = client.add_receiver("$default", "0", operation='/messages/events')
try:
    client.run()
    eh_info = client.get_eventhub_info()
    print(eh_info)

    received = receiver.receive(timeout=5)
    print(received)
finally:
    client.stop()
