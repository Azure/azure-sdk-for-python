#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from threading import Thread
import os
import time
import logging

from azure.eventhub import EventHubClient, EventPosition, EventHubSharedKeyCredential, EventData

import examples
logger = examples.get_logger(logging.INFO)


HOSTNAME = os.environ.get('EVENT_HUB_HOSTNAME')  # <mynamespace>.servicebus.windows.net
EVENT_HUB = os.environ.get('EVENT_HUB_NAME')

USER = os.environ.get('EVENT_HUB_SAS_POLICY')
KEY = os.environ.get('EVENT_HUB_SAS_KEY')

EVENT_POSITION = EventPosition("-1")


class PartitionConsumerThread(Thread):
    def __init__(self, consumer):
        Thread.__init__(self)
        self.consumer = consumer

    def run(self):
        with consumer:
            for item in self.consumer:
                print(item)


client = EventHubClient(host=HOSTNAME, event_hub_path=EVENT_HUB, credential=EventHubSharedKeyCredential(USER, KEY),
                    network_tracing=False)
consumer = client.create_consumer(consumer_group="$default", partition_id="0", event_position=EVENT_POSITION)

thread = PartitionConsumerThread(consumer)
thread.start()
