#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show sending events to an Event Hub partition.
This is just an example of sending EventData, not performance optimal.
To have the best performance, send a batch EventData with one send() call.
"""

# pylint: disable=C0111

import time
import os
from azure.eventhub import EventHubClient, EventData, EventHubSharedKeyCredential


HOSTNAME = os.environ['EVENT_HUB_HOSTNAME']  # <mynamespace>.servicebus.windows.net
EVENT_HUB = os.environ['EVENT_HUB_NAME']
USER = os.environ['EVENT_HUB_SAS_POLICY']
KEY = os.environ['EVENT_HUB_SAS_KEY']

client = EventHubClient(host=HOSTNAME, event_hub_path=EVENT_HUB, credential=EventHubSharedKeyCredential(USER, KEY),
                        network_tracing=False)
producer = client.create_producer(partition_id="0")
start_time = time.time()
with producer:
    # not performance optimal, but works. Please do send events in batch to get much better performance.
    for i in range(100):
        ed = EventData("msg")
        print("Sending message: {}".format(i))
        producer.send(ed)  # please use batch_send for better performance. Refer to event_data_batch.py
