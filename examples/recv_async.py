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
import asyncio
from eventhubs import EventHubClient, Offset
from eventhubs.async import AsyncReceiver

# pylint: disable=C0301
# pylint: disable=C0103
# pylint: disable=C0111

async def pump(recv, count):
    total = 0
    while count < 0 or total < count:
        try:
            batch = await asyncio.wait_for(recv.receive(100), 60.0)
            size = len(batch)
            total += size
            logging.info("Received %d events, sn %d, batch %d", total, batch[-1].sequence_number, size)
            # simulate an async event processing
            await asyncio.sleep(0.05)
        except asyncio.TimeoutError:
            logging.info("No events received, queue size %d, delivered %d", recv.messages.qsize(), recv.delivered)

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
    OFFSET = Offset("-1")

    logging.info("starting loop")
    loop = asyncio.get_event_loop()
    receiver = AsyncReceiver()
    client = EventHubClient(ADDRESS if len(sys.argv) == 1 else sys.argv[1]) \
        .subscribe(receiver, CONSUMER_GROUP, "0", OFFSET) \
        .run_daemon()

    loop.run_until_complete(pump(receiver, 1000))
    client.stop()
    loop.close()

except KeyboardInterrupt:
    pass
