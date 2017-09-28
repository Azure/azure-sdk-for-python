#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show receiving events from an Event Hub partition.
"""

import sys
import logging
from eventhubs import EventHubClient, Offset

class MyReceiver(object):
    """
    The event data handler.
    """

    def __init__(self, partition):
        self.partition = partition
        self.total = 0
        self.last_sn = -1
        self.last_offset = "-1"

    def on_event_data(self, event_data):
        """
        Process one event data.
        """
        self.last_offset = event_data.offset
        self.last_sn = event_data.sequence_number
        self.total += 1
        logging.info("Partition %s, Received %s, sn=%d offset=%s",
                     self.partition,
                     self.total,
                     self.last_sn,
                     self.last_offset)

try:
    logging.basicConfig(filename="test.log", level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

    ADDRESS = ("amqps://"
               "<URL-encoded-SAS-policy>"
               ":"
               "<URL-encoded-SAS-key>"
               "@"
               "<mynamespace>.servicebus.windows.net"
               "/"
               "myeventhub")
    CONSUMER_GROUP = "$default"
    OFFSET = Offset("-1")

    EventHubClient(ADDRESS) \
        .subscribe(MyReceiver("0"), CONSUMER_GROUP, "0", OFFSET) \
        .subscribe(MyReceiver("1"), CONSUMER_GROUP, "1", OFFSET) \
        .run()
except KeyboardInterrupt:
    pass
