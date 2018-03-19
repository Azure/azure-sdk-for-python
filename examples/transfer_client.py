#!/usr/bin/env python

"""
send test
"""

import logging
import argparse
import time
import threading
import utils
import logging
import os
from azure.eventhub import EventHubClient, Sender, EventData

logger = logging.getLogger('transferClientTest')

# Address can be in either of these formats:
# "amqps://<URL-encoded-SAS-policy>:<URL-encoded-SAS-key>@<mynamespace>.servicebus.windows.net/myeventhub"
# "amqps://<mynamespace>.servicebus.windows.net/myeventhub"
ADDRESS = os.environ.get('EVENT_HUB_ADDRESS')

# SAS policy and key are not required if they are encoded in the URL
USER = os.environ.get('EVENT_HUB_SAS_POLICY')
KEY = os.environ.get('EVENT_HUB_SAS_KEY')
BATCH = 1
PAYLOAD = 512
DURATION = 60


class TransferClient(object):
    def __init__(self, sender):
        self._sender = sender
        self._deadline = time.time() + DURATION
        self._total = 0
        self._success = 0
        self._failure = 0
        self._event = threading.Event()

    def run(self):
        for i in range(BATCH):
            self.start_send()
        self._event.wait()

    def start_send(self):
        self._sender.transfer(EventData("B" * PAYLOAD), self.end_send)

    def end_send(self, event_data, error):
        self._total += 1
        if error:
            print("send failed {}".format(error))
            self._failure += 1
        else:
            self._success += 1
        if self._total % 5000 == 0:
            print("Send total {}, success {}, failure {}".format(
                        self._total,
                        self._success,
                        self._failure))
        if time.time() < self._deadline:
            self.start_send()
        else:
            self._event.set()

try:
    if not ADDRESS:
        raise ValueError("No EventHubs URL supplied.")

    client = EventHubClient(ADDRESS, debug=False, username=USER, password=KEY)
    sender = client.add_sender()
    client.run()
    if BATCH > 1:
        TransferClient(sender).run()
    else:
        total = 0
        deadline = time.time() + DURATION
        while time.time() < deadline:
            try:
                sender.transfer(EventData("D" * PAYLOAD))
                total += 1
                if total % 5000 == 0:
                    sender.wait()
            except Exception as err:
                print("Send failed {}".format(err))
                raise
        print("Send total {}".format(total))
    client.stop()
except KeyboardInterrupt:
    pass
