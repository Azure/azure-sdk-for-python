#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from azure.eventhub import EventHubClient, EventPosition, EventHubSharedKeyCredential, EventData

HOSTNAME = os.environ['EVENT_HUB_HOSTNAME']  # <mynamespace>.servicebus.windows.net
EVENT_HUB = os.environ['EVENT_HUB_NAME']
USER = os.environ['EVENT_HUB_SAS_POLICY']
KEY = os.environ['EVENT_HUB_SAS_KEY']
EVENT_POSITION = EventPosition("-1")


client = EventHubClient(host=HOSTNAME, event_hub_path=EVENT_HUB, credential=EventHubSharedKeyCredential(USER, KEY),
                        network_tracing=False)
consumer = client.create_consumer(consumer_group="$default", partition_id="0", event_position=EVENT_POSITION)
try:
    with consumer:
        for item in consumer:
            print(item)
except KeyboardInterrupt:
    print("Iterator stopped")
