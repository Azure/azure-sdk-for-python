#!/usr/bin/env python

"""
An example to show receiving events from an Event Hub partition.
"""

# pylint: disable=C0111

import sys
import logging
import asyncio
from eventhubs import EventHubClient, EventData
from eventhubs.async import AsyncSender

import examples
logger = examples.get_logger(logging.INFO)

async def send(snd, count):
    for i in range(count):
        await snd.send(EventData(str(i)))
        logger.info("Send message %d", i)

try:
    ADDRESS = ("amqps://"
               "<URL-encoded-SAS-policy>"
               ":"
               "<URL-encoded-SAS-key>"
               "@"
               "<mynamespace>.servicebus.windows.net"
               "/"
               "myeventhub")

    sender = AsyncSender()
    client = EventHubClient(ADDRESS if len(sys.argv) == 1 else sys.argv[1]) \
                 .publish(sender) \
                 .run_daemon()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(send(sender, 100))
    client.stop()
    loop.close()

except KeyboardInterrupt:
    pass
