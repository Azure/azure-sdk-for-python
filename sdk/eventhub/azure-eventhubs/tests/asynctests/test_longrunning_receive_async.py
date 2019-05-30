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
import os
import sys
import pytest
from logging.handlers import RotatingFileHandler

from azure.eventhub import EventPosition
from azure.eventhub.aio import EventHubClient


def get_logger(filename, level=logging.INFO):
    azure_logger = logging.getLogger("azure.eventhub")
    azure_logger.setLevel(level)
    uamqp_logger = logging.getLogger("uamqp")
    uamqp_logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(formatter)
    if not azure_logger.handlers:
        azure_logger.addHandler(console_handler)
    if not uamqp_logger.handlers:
        uamqp_logger.addHandler(console_handler)

    if filename:
        file_handler = RotatingFileHandler(filename, maxBytes=20*1024*1024, backupCount=3)
        file_handler.setFormatter(formatter)
        azure_logger.addHandler(file_handler)
        uamqp_logger.addHandler(file_handler)

    return azure_logger

logger = get_logger("recv_test_async.log", logging.INFO)


async def get_partitions(client):
    eh_data = await client.get_properties()
    return eh_data["partition_ids"]


async def pump(_pid, receiver, _args, _dl):
    total = 0
    iteration = 0
    deadline = time.time() + _dl

    try:
        async with receiver:
            while time.time() < deadline:
                batch = await receiver.receive(timeout=1)
                size = len(batch)
                total += size
                iteration += 1
                if size == 0:
                    print("{}: No events received, queue size {}, delivered {}".format(
                        _pid,
                        receiver.queue_size,
                        total))
                elif iteration >= 5:
                    iteration = 0
                    print("{}: total received {}, last sn={}, last offset={}".format(
                                _pid,
                                total,
                                batch[-1].sequence_number,
                                batch[-1].offset.value))
            print("{}: total received {}".format(
                _pid,
                total))
    except Exception as e:
        print("Partition {} receiver failed: {}".format(_pid, e))
        raise


@pytest.mark.liveTest
def test_long_running_receive_async(connection_str):
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", help="Duration in seconds of the test", type=int, default=30)
    parser.add_argument("--consumer", help="Consumer group name", default="$default")
    parser.add_argument("--partitions", help="Comma seperated partition IDs")
    parser.add_argument("--offset", help="Starting offset", default="-1")
    parser.add_argument("--conn-str", help="EventHub connection string", default=connection_str)
    parser.add_argument("--eventhub", help="Name of EventHub")
    parser.add_argument("--address", help="Address URI to the EventHub entity")
    parser.add_argument("--sas-policy", help="Name of the shared access policy to authenticate with")
    parser.add_argument("--sas-key", help="Shared access key")

    loop = asyncio.get_event_loop()
    args, _ = parser.parse_known_args()
    if args.conn_str:
        client = EventHubClient.from_connection_string(
            args.conn_str,
            eventhub=args.eventhub, auth_timeout=240, debug=False)
    elif args.address:
        client = EventHubClient(
            args.address,
            auth_timeout=240,
            username=args.sas_policy,
            password=args.sas_key)
    else:
        try:
            import pytest
            pytest.skip("Must specify either '--conn-str' or '--address'")
        except ImportError:
            raise ValueError("Must specify either '--conn-str' or '--address'")

    try:
        if not args.partitions:
            partitions = loop.run_until_complete(get_partitions(client))
        else:
            partitions = args.partitions.split(",")
        pumps = []
        for pid in partitions:
            receiver = client.create_receiver(
                partition_id=pid,
                event_position=EventPosition(args.offset),
                prefetch=50)
            pumps.append(pump(pid, receiver, args, args.duration))
        loop.run_until_complete(asyncio.gather(*pumps))
    finally:
        pass


if __name__ == '__main__':
    test_long_running_receive_async(os.environ.get('EVENT_HUB_CONNECTION_STR'))
