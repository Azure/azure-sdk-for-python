#!/usr/bin/env python

"""
An example to show receiving events from an Event Hub partition.
"""

import sys
import logging
from proton import Message
from eventhubs.client import EventHubClient
from eventhubs.client import Sender

class MySender(Sender):
    """
    The event data sender.
    """

    def __init__(self, partition=None):
        super(MySender, self).__init__(partition)

    def on_start(self):
        super(MySender, self).on_start()

try:
    logging.basicConfig(filename="test.log", level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

    # ADDRESS = ("amqps://"
    #            "<URL-encoded-SAS-policy>"
    #            ":"
    #            "<URL-encoded-SAS-key>"
    #            "@"
    #            "<mynamespace>.servicebus.windows.net"
    #            "/"
    #            "myeventhub")

    ADDRESS = ("amqps://"
    "RootManageSharedAccessKey"
    ":"
    "SE3o2xcXU2acPhSbm8me0VWvWE7TjP4qcFBYC4FkLmI="
    "@"
    "k8sworkshop.servicebus.windows.net"
    "/"
    "k8s") 

    EventHubClient(ADDRESS, MySender()).run()

except KeyboardInterrupt:
    pass
