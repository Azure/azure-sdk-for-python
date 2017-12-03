#!/usr/bin/env python

"""
An example to show receiving events from an Event Hub partition.
"""

# pylint: disable=C0111

import sys
import logging
from eventhubs import EventHubClient, Sender, EventData

import examples
logger = examples.get_logger(logging.INFO)

try:
    ADDRESS = ("amqps://"
               "<URL-encoded-SAS-policy>"
               ":"
               "<URL-encoded-SAS-key>"
               "@"
               "<mynamespace>.servicebus.windows.net"
               "/"
               "myeventhub")

    sender = Sender()
    client = EventHubClient(ADDRESS if len(sys.argv) == 1 else sys.argv[1]) \
                 .publish(sender) \
                 .run_daemon()

    for i in range(100):
        sender.send(EventData(str(i)))
        logger.info("Send message %d", i)

    client.stop()

except KeyboardInterrupt:
    pass
