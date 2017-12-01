#!/usr/bin/env python

"""
send test
"""

import logging
import argparse
import time
import threading
import utils
from eventhubs import EventHubClient, Sender, EventData

logger = utils.get_logger("send_test.log", logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument("--duration", help="Duration in seconds of the test", type=int, default=3600)
parser.add_argument("--payload", help="payload size", type=int, default=512)
parser.add_argument("--batch", help="Number of events to send and wait", type=int, default=1)
parser.add_argument("address", help="Address Uri to the event hub entity", nargs="?")

args = parser.parse_args()

class TransferClient(object):
    def __init__(self, sender):
        self._sender = sender
        self._deadline = time.time() + args.duration
        self._total = 0
        self._success = 0
        self._failure = 0
        self._event = threading.Event()

    def run(self):
        for i in range(args.batch):
            self.start_send()
        self._event.wait()

    def start_send(self):
        self._sender.transfer(EventData("B" * args.payload), self.end_send)

    def end_send(self, event_data, error):
        self._total += 1
        if error:
            logger.error("send failed %s", error)
            self._failure += 1
        else:
            self._success += 1
        if self._total % 500 == 0:
            logger.info("Send total %d, success %d, failure %d",
                        self._total,
                        self._success,
                        self._failure)
        if time.time() < self._deadline:
            self.start_send()
        else:
            self._event.set()

try:
    sender = Sender()
    client = EventHubClient(args.address).publish(sender).run_daemon()
    if args.batch > 1:
        TransferClient(sender).run()
    else:
        total = 0
        deadline = time.time() + args.duration
        while time.time() < deadline:
            try:
                sender.send(EventData("D" * args.payload))
                total += 1
                if total % 500 == 0:
                    logger.info("Send total %d", total)
            except Exception as err:
                logger.error("Send failed %s", err)
    client.stop()
except KeyboardInterrupt:
    pass
