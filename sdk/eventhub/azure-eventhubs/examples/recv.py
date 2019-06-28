#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show receiving events from an Event Hub partition.
"""
import os
import logging
import time
from azure.eventhub import EventHubClient, EventPosition, EventHubSharedKeyCredential

import examples
logger = examples.get_logger(logging.INFO)

HOSTNAME = os.environ.get('EVENT_HUB_HOSTNAME')  # <mynamespace>.servicebus.windows.net
EVENT_HUB = os.environ.get('EVENT_HUB_NAME')

USER = os.environ.get('EVENT_HUB_SAS_POLICY')
KEY = os.environ.get('EVENT_HUB_SAS_KEY')

EVENT_POSITION = EventPosition("-1")
PARTITION = "0"


total = 0
last_sn = -1
last_offset = "-1"
client = EventHubClient(host=HOSTNAME, event_hub_path=EVENT_HUB, credential=EventHubSharedKeyCredential(USER, KEY),
                        network_tracing=False)

try:
    consumer = client.create_consumer(consumer_group="$default", partition_id=PARTITION, event_position=EVENT_POSITION, prefetch=5000)
    with consumer:
        start_time = time.time()
        batch = consumer.receive(timeout=5)
        while batch:
            for event_data in batch:
                last_offset = event_data.offset
                last_sn = event_data.sequence_number
                print("Received: {}, {}".format(last_offset, last_sn))
                print(event_data.body_as_str())
                total += 1
            batch = consumer.receive(timeout=5)

        end_time = time.time()
        run_time = end_time - start_time
        print("Received {} messages in {} seconds".format(total, run_time))

except KeyboardInterrupt:
    pass
