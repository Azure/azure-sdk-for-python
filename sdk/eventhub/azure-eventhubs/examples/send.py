#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show sending individual events to an Event Hub partition.
Although this works, sending events in batches will get better performance.
See 'send_list_of_event_data.py' and 'send_event_data_batch.py' for an example of batching.
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
    for i in range(100):
        ed = EventData("msg")
        print("Sending message: {}".format(i))
        producer.send(ed)
print("Send 100 messages in {} seconds".format(time.time() - start_time))
