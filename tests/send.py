#!/usr/bin/env python

"""
send test
"""

import sys
import logging
import argparse
import time
from eventhubs import EventHubClient, Sender, EventData
from utils import init_logger

logger = init_logger("send_test.log", logging.INFO)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))
parser = argparse.ArgumentParser()
parser.add_argument("--duration", help="Duration in seconds of the test", type=int, default=3600)
parser.add_argument("--payload", help="payload size", type=int, default=512)
parser.add_argument("address", help="Address Uri to the event hub entity", nargs="?")

try:
    args = parser.parse_args()
    sender = Sender()
    client = EventHubClient(args.address).publish(sender).run_daemon()
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
