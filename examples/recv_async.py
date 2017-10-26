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

# pylint: disable=C0103
# pylint: disable=C0111

async def pump(recv):
    for k in range(10):
        _batch = await recv.receive(5)
        logging.info("Received %d events", len(_batch))
        for _ev in _batch:
            logging.info("  sn=%d offset=%s", _ev.sequence_number, _ev.offset)

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

    _recv = AsyncReceiver()
    _client = EventHubClient(ADDRESS if sys.argv.count == 1 else sys.argv[1]) \
        .subscribe(_recv, CONSUMER_GROUP, "0", OFFSET) \
        .run_daemon()

    _loop = asyncio.get_event_loop()
    _loop.run_until_complete(pump(_recv))

    _client.stop()

except KeyboardInterrupt:
    pass
