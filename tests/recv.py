#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
receive test.
"""

import logging
import asyncio
import argparse
import time
import utils
from eventhubs import EventHubClient, Offset
from eventhubs.async import AsyncReceiver

logger = utils.get_logger("recv_test.log", logging.INFO)

async def pump(_pid, _recv, _dl):
    total = 0
    iteration = 0
    while time.time() < _dl:
        try:
            batch = await asyncio.wait_for(_recv.receive(100), 60.0)
            size = len(batch)
            total += size
            iteration += size
            if iteration >= 80:
                iteration = 0
                logger.info("%s: total received %d, last sn=%d, last offset=%s",
                            _pid,
                            total,
                            batch[-1].sequence_number,
                            batch[-1].offset)
        except asyncio.TimeoutError:
            logger.info("%s: No events received, queue size %d, delivered %d",
                        _pid,
                        _recv.messages.qsize(),
                        _recv.delivered)

parser = argparse.ArgumentParser()
parser.add_argument("--duration", help="Duration in seconds of the test", type=int, default=3600)
parser.add_argument("--consumer", help="Consumer group name", default="$default")
parser.add_argument("--partitions", help="Comma seperated partition IDs", default="0")
parser.add_argument("--offset", help="Starting offset", default="-1")
parser.add_argument("address", help="Address Uri to the event hub entity", nargs="?")

try:
    args = parser.parse_args()
    loop = asyncio.get_event_loop()
    client = EventHubClient(args.address)
    deadline = time.time() + args.duration
    asyncio.gather()
    pumps = []
    for pid in args.partitions.split(","):
        receiver = AsyncReceiver()
        client.subscribe(receiver, args.consumer, pid, Offset(args.offset))
        pumps.append(pump(pid, receiver, deadline))
    client.run_daemon()
    loop.run_until_complete(asyncio.gather(*pumps))
    client.stop()
    loop.close()
except KeyboardInterrupt:
    pass
