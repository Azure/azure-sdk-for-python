#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
receive test.
"""

import sys
import logging
import asyncio
import argparse
import time
from eventhubs import EventHubClient, Offset
from eventhubs.async import AsyncReceiver
from tests import init_logger

async def pump(recv, deadline):
    total = 0
    iteration = 0
    while time.time() < deadline:
        try:
            batch = await asyncio.wait_for(recv.receive(100), 60.0)
            size = len(batch)
            total += size
            iteration += size
            if iteration >= 500:
                iteration = 0
                logging.info("total received %d, last sn=%d, last offset=%d",
                             total,
                             batch[-1].sequence_number,
                             batch[-1].offset)
        except asyncio.TimeoutError:
            logging.info("No events received, queue size %d, delivered %d",
                         recv.messages.qsize(),
                         recv.delivered)

logger = init_logger("recv_test.log", logging.INFO)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))
parser = argparse.ArgumentParser()
parser.add_argument("--duration", help="Duration in seconds of the test", type=int, default=3600)
parser.add_argument("--consumer", help="Consumer group name", default="$default")
parser.add_argument("--partition", help="Partition id", default="0")
parser.add_argument("--offset", help="Starting offset", default="-1")
parser.add_argument("address", help="Address Uri to the event hub entity", nargs="?")

try:
    args = parser.parse_args()
    loop = asyncio.get_event_loop()
    receiver = AsyncReceiver()
    client = EventHubClient(args.address) \
        .subscribe(receiver, args.consumer, args.partition, Offset(args.offset)) \
        .run_daemon()
    loop.run_until_complete(pump(receiver, time.time() + args.duration))
    client.stop()
    loop.close()
except KeyboardInterrupt:
    pass
