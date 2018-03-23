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
from urllib.parse import quote_plus
from azure.eventhub import Offset
from azure.eventhub.async import EventHubClientAsync

logger = utils.get_logger("recv_test.log", logging.INFO)

async def pump(_pid, _recv, _dl):
    total = 0
    iteration = 0
    while time.time() < _dl:
        batch_gen = _recv.receive(batch_size=5000, timeout=60)
        batch = []
        async for event in batch_gen:
            batch.append(event)
        size = len(batch)
        total += size
        iteration += 1
        if size == 0:
            print("{}: No events received, queue size {}, delivered {}".format(
                _pid,
                _recv.messages.qsize(),
                _recv.delivered))
        if iteration >= 80:
            iteration = 0
            print("{}: total received {}, last sn={}, last offset={}".format(
                        _pid,
                        total,
                        batch[-1].sequence_number,
                        batch[-1].offset))
    print("{}: total received {}, last sn={}, last offset={}".format(
        _pid,
        total,
        batch[-1].sequence_number,
        batch[-1].offset))

parser = argparse.ArgumentParser()
parser.add_argument("--duration", help="Duration in seconds of the test", type=int, default=3600)
parser.add_argument("--consumer", help="Consumer group name", default="$default")
parser.add_argument("--partitions", help="Comma seperated partition IDs", default="0")
parser.add_argument("--offset", help="Starting offset", default="-1")
parser.add_argument("--conn-str", help="EventHub connection string")
parser.add_argument("--eventhub", help="Name of EventHub")
parser.add_argument("--address", help="Address URI to the EventHub entity")
parser.add_argument("--sas-policy", help="Name of the shared access policy to authenticate with")
parser.add_argument("--sas-key", help="Shared access key")

try:
    args = parser.parse_args()
    entity = None
    if args.conn_str:
        address, policy, key, entity = utils.parse_conn_str(args.conn_str)
    elif args.address:
        address = args.address
        policy = args.sas_policy
        key = args.sas_key
    else:
        raise ValueError("Must specify either '--conn-str' or '--address'")
    entity = entity or args.eventhub
    address = utils.build_uri(address, entity)

    loop = asyncio.get_event_loop()
    client = EventHubClientAsync(address, username=policy, password=key)
    deadline = time.time() + args.duration
    asyncio.gather()
    pumps = []
    for pid in args.partitions.split(","):
        receiver = client.add_async_receiver(
            consumer_group=args.consumer,
            partition=pid,
            offset=Offset(args.offset),
            prefetch=5000)
        pumps.append(pump(pid, receiver, deadline))
    loop.run_until_complete(client.run_async())
    loop.run_until_complete(asyncio.gather(*pumps))
    client.stop()
    loop.close()
except KeyboardInterrupt:
    pass
