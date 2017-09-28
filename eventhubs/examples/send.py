#!/usr/bin/env python

"""
An example to show receiving events from an Event Hub partition.
"""

# pylint: disable=C0111

import sys
import logging
from eventhubs import EventHubClient

class MySender(object):
    """
    The event data sender.
    """

    def __init__(self, partition=None):
        pass

    def on_start(self):
        pass

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
    EventHubClient(ADDRESS).publish(MySender()).run()

except KeyboardInterrupt:
    pass
