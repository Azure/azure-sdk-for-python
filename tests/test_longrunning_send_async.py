#!/usr/bin/env python

"""
send test
"""

import logging
import argparse
import time
import threading
import os
import asyncio

from azure.eventhub import EventHubClientAsync, EventData

try:
    import tests
    logger = tests.get_logger("send_test.log", logging.INFO)
except ImportError:
    logger = logging.getLogger("uamqp")
    logger.setLevel(logging.INFO)


def check_send_successful(outcome, condition):
    if outcome.value != 0:
        print("Send failed {}".format(condition))


async def get_partitions(args):
    #client = EventHubClientAsync.from_connection_string(
    #    args.conn_str,
    #    eventhub=args.eventhub, debug=True)
    eh_data = await args.get_eventhub_info_async()
    return eh_data["partition_ids"]


async def pump(pid, sender, args, duration):
    deadline = time.time() + duration
    total = 0

    def data_generator():
        for i in range(args.batch):
            yield b"D" * args.payload

    if args.batch > 1:
        logger.error("Sending batched messages")
    else:
        logger.error("Sending single messages")

    try:
        while time.time() < deadline:
            if args.batch > 1:
                data = EventData(batch=data_generator())
            else:
                data = EventData(body=b"D" * args.payload)
            sender.transfer(data, callback=check_send_successful)
            total += args.batch
            if total % 10000 == 0:
               await sender.wait_async()
               logger.error("Send total {}".format(total))
    except Exception as err:
        logger.error("Send failed {}".format(err))
    logger.error("Sent total {}".format(total))


def test_long_running_partition_send_async():
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", help="Duration in seconds of the test", type=int, default=30)
    parser.add_argument("--payload", help="payload size", type=int, default=512)
    parser.add_argument("--batch", help="Number of events to send and wait", type=int, default=1)
    parser.add_argument("--partitions", help="Comma seperated partition IDs")
    parser.add_argument("--conn-str", help="EventHub connection string", default=os.environ.get('EVENT_HUB_CONNECTION_STR'))
    parser.add_argument("--eventhub", help="Name of EventHub")
    parser.add_argument("--address", help="Address URI to the EventHub entity")
    parser.add_argument("--sas-policy", help="Name of the shared access policy to authenticate with")
    parser.add_argument("--sas-key", help="Shared access key")

    loop = asyncio.get_event_loop()
    args, _ = parser.parse_known_args()
    if args.conn_str:
        client = EventHubClientAsync.from_connection_string(
            args.conn_str,
            eventhub=args.eventhub, debug=True)
    elif args.address:
        client = EventHubClient(
            args.address,
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
            sender = client.add_async_sender(partition=pid)
            pumps.append(pump(pid, sender, args, args.duration))
        loop.run_until_complete(client.run_async())
        loop.run_until_complete(asyncio.gather(*pumps))
    finally:
        loop.run_until_complete(client.stop_async())

if __name__ == '__main__':
    test_long_running_partition_send_async()
