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
from azure.eventhub import EventData, EventHubClient, EventHubSharedKeyCredential


HOSTNAME = os.environ['EVENT_HUB_HOSTNAME']  # <mynamespace>.servicebus.windows.net
EVENT_HUB = os.environ['EVENT_HUB_NAME']
USER = os.environ['EVENT_HUB_SAS_POLICY']
KEY = os.environ['EVENT_HUB_SAS_KEY']

client = EventHubClient(host=HOSTNAME, event_hub_path=EVENT_HUB, credential=EventHubSharedKeyCredential(USER, KEY),
                        network_tracing=False)
producer = client.create_producer(partition_id="1")

event_list = []
for i in range(1500):
    event_list.append(EventData('Hello World'))
start_time = time.time()
with producer:
    producer.send(event_list)
print("Runtime: {} seconds".format(time.time() - start_time))
