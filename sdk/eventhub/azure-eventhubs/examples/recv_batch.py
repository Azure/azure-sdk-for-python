#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show receiving events from an Event Hub partition and processing
the event in on_event_data callback.

"""
import os
import sys
import logging
from azure.eventhub import EventHubClient, Receiver, Offset

import examples
logger = examples.get_logger(logging.INFO)

# Address can be in either of these formats:
# "amqps://<URL-encoded-SAS-policy>:<URL-encoded-SAS-key>@<mynamespace>.servicebus.windows.net/myeventhub"
# "amqps://<mynamespace>.servicebus.windows.net/myeventhub"
ADDRESS = os.environ.get('EVENT_HUB_ADDRESS')

# SAS policy and key are not required if they are encoded in the URL
USER = os.environ.get('EVENT_HUB_SAS_POLICY')
KEY = os.environ.get('EVENT_HUB_SAS_KEY')
CONSUMER_GROUP = "$default"
OFFSET = Offset("-1")
PARTITION = "0"


total = 0
last_sn = -1
last_offset = "-1"
client = EventHubClient(ADDRESS, debug=False, username=USER, password=KEY)
try:
    receiver = client.add_receiver(CONSUMER_GROUP, PARTITION, prefetch=100, offset=OFFSET)
    client.run()
    batched_events = receiver.receive(max_batch_size=10)
    for event_data in batched_events:
        last_offset = event_data.offset.value
        last_sn = event_data.sequence_number
        total += 1
        print("Partition {}, Received {}, sn={} offset={}".format(
            PARTITION,
            total,
            last_sn,
            last_offset))

except KeyboardInterrupt:
    pass
finally:
    client.stop()