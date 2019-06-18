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

EVENT_POSITION = EventPosition.first_available_event()


class PartitionReceiverThread(Thread):
    def __init__(self, receiver):
        Thread.__init__(self)
        self.receiver = receiver

    def run(self):
        for item in self.receiver:
            print(item)


client = EventHubClient(host=HOSTNAME, event_hub_path=EVENT_HUB, credential=EventHubSharedKeyCredential(USER, KEY),
                    network_tracing=False)
receiver = client.create_receiver(partition_id="0", event_position=EVENT_POSITION)
with receiver:
    thread = PartitionReceiverThread(receiver)
    thread.start()
    thread.join(2)  # stop after 2 seconds
