#!/usr/bin/env python

"""
An example to show receiving events from an Event Hub partition.
"""

import sys
import logging
from eventhubs import EventHubClient, EventData

class MyReceiver(object):
    """
    The event data handler.
    """

    def __init__(self):
        self.total = 0
        self.last_sn = -1
        self.last_offset = None

    def on_event_data(self, message):
        """
        Process one event data.
        """
        self.last_offset = EventData.offset(message)
        self.last_sn = EventData.sequence_number(message)
        # message.properties (dict) - application defined properties
        # message.body (object) - application set object
        self.total += 1
        if self.total % 50 == 0:
            # do checkpoint for every 50 events received
            logging.info("Received %s, sn=%d offset=%s",
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
    PARTITION = "1"
    OFFSET = "-1"
    EventHubClient(ADDRESS).subscribe(MyReceiver(), CONSUMER_GROUP, PARTITION, OFFSET).run()
except KeyboardInterrupt:
    pass
