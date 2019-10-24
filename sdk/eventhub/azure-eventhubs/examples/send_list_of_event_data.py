#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show batch sending events to an Event Hub.
"""

# pylint: disable=C0111

import time
import os
from azure.eventhub import EventData, EventHubProducerClient


EVENT_HUB_CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
EVENT_HUB = os.environ['EVENT_HUB_NAME']

producer = EventHubProducerClient.from_connection_string(conn_str=EVENT_HUB_CONNECTION_STR, event_hub_path=EVENT_HUB)

event_list = []
for i in range(1500):
    event_list.append(EventData('Hello World'))
start_time = time.time()
with producer:
    producer.send(event_list, partition_id='0')
print("Runtime: {} seconds".format(time.time() - start_time))
