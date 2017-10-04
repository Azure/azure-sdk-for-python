#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
An example to show running the EventHubClient in background.

"""

import sys
import logging
from eventhubs import EventHubClient, Receiver, Offset

try:
    import Queue
except:
    import queue as Queue

class MyReceiver(Receiver):
    def __init__(self, partition):
        super(MyReceiver, self).__init__()
        self.partition = partition
        self.messages = Queue.Queue()

    def receive(self):
        return self.messages.get()

    def on_event_data(self, event_data):
        self.messages.put(event_data)

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
    OFFSET = Offset("@latest")

    recv = MyReceiver("0")
    client = EventHubClient(ADDRESS if sys.argv.count == 1 else sys.argv[1]) \
        .subscribe(recv, CONSUMER_GROUP, "0", OFFSET) \
        .run_async()
    # read some events
    for k in range(10):
        _e = recv.receive()
        logging.info("Received sn=%d offset=%s", _e.sequence_number, _e.offset)
    client.stop()

except KeyboardInterrupt:
    pass
