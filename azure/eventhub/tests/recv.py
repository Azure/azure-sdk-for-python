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

async def pump(_pid, receiver, _args, _dl):
    total = 0
    iteration = 0
    deadline = time.time() + _dl
    try:
        while time.time() < deadline:
            batch = await receiver.receive(timeout=5)
            size = len(batch)
            total += size
            iteration += 1
            if size == 0:
                print("{}: No events received, queue size {}, delivered {}".format(
                    _pid,
                    receiver.queue_size,
                    receiver.delivered))
            elif iteration >= 80:
                iteration = 0
                print("{}: total received {}, last sn={}, last offset={}".format(
                            _pid,
                            total,
                            batch[-1].sequence_number,
                            batch[-1].offset))
        print("{}: total received {}".format(
            _pid,
            total))
    except Exception as e:
        print("Partition {} receiver failed: {}".format(_pid, e))


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
    loop = asyncio.get_event_loop()
    args = parser.parse_args()
    if args.conn_str:
        client = EventHubClientAsync.from_connection_string(
            args.conn_str,
            eventhub=args.eventhub)
    elif args.address:
        client = EventHubClientAsync(
            args.address,
            username=args.sas_policy,
            password=args.sas_key)
    else:
        raise ValueError("Must specify either '--conn-str' or '--address'")

    pumps = []
    for pid in args.partitions.split(","):
        receiver = client.add_async_receiver(
            consumer_group=args.consumer,
            partition=pid,
            offset=Offset(args.offset),
            prefetch=5000)
        pumps.append(pump(pid, receiver, args, args.duration))
    loop.run_until_complete(client.run_async())
    loop.run_until_complete(asyncio.gather(*pumps))
except:
    raise
finally:
    loop.run_until_complete(client.stop_async())
    loop.close()
