#!/usr/bin/env python

"""
send test
"""

import logging
import argparse
import time
import os
import asyncio
import sys
from logging.handlers import RotatingFileHandler

from azure.eventhub import EventHubClientAsync, EventData


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

logger = get_logger("send_test_async.log", logging.INFO)


def check_send_successful(outcome, condition):
    if outcome.value != 0:
        print("Send failed {}".format(condition))


async def get_partitions(args):
    eh_data = await args.get_eventhub_info_async()
    return eh_data["partition_ids"]


async def pump(pid, sender, args, duration):
    deadline = time.time() + duration
    total = 0

    def data_generator():
        for i in range(args.batch):
            yield b"D" * args.payload

    if args.batch > 1:
        logger.info("{}: Sending batched messages".format(pid))
    else:
        logger.info("{}: Sending single messages".format(pid))

    try:
        while time.time() < deadline:
            if args.batch > 1:
                data = EventData(batch=data_generator())
            else:
                data = EventData(body=b"D" * args.payload)
            sender.transfer(data, callback=check_send_successful)
            total += args.batch
            if total % 100 == 0:
               await sender.wait_async()
               logger.info("{}: Send total {}".format(pid, total))
    except Exception as err:
        logger.error("{}: Send failed {}".format(pid, err))
        raise
    print("{}: Final Sent total {}".format(pid, total))


def test_long_running_partition_send_async(connection_str):
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", help="Duration in seconds of the test", type=int, default=30)
    parser.add_argument("--payload", help="payload size", type=int, default=1024)
    parser.add_argument("--batch", help="Number of events to send and wait", type=int, default=200)
    parser.add_argument("--partitions", help="Comma seperated partition IDs")
    parser.add_argument("--conn-str", help="EventHub connection string", default=connection_str)
    parser.add_argument("--eventhub", help="Name of EventHub")
    parser.add_argument("--address", help="Address URI to the EventHub entity")
    parser.add_argument("--sas-policy", help="Name of the shared access policy to authenticate with")
    parser.add_argument("--sas-key", help="Shared access key")
    parser.add_argument("--logger-name", help="Unique log file ID")

    loop = asyncio.get_event_loop()
    args, _ = parser.parse_known_args()

    if args.conn_str:
        client = EventHubClientAsync.from_connection_string(
            args.conn_str,
            eventhub=args.eventhub, debug=True)
    elif args.address:
        client = EventHubClientAsync(
            args.address,
            username=args.sas_policy,
            password=args.sas_key,
            auth_timeout=500)
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
            pid_range = args.partitions.split("-")
            if len(pid_range) > 1:
                partitions = [str(i) for i in range(int(pid_range[0]), int(pid_range[1]) + 1)]
            else:
                partitions = args.partitions.split(",")
        pumps = []
        for pid in partitions:
            sender = client.add_async_sender(partition=pid, send_timeout=0, keep_alive=False)
            pumps.append(pump(pid, sender, args, args.duration))
        loop.run_until_complete(client.run_async())
        results = loop.run_until_complete(asyncio.gather(*pumps, return_exceptions=True))
        assert not results
    except Exception as e:
        logger.error("Sender failed: {}".format(e))
    finally:
        logger.info("Shutting down sender")
        loop.run_until_complete(client.stop_async())

if __name__ == '__main__':
    test_long_running_partition_send_async(os.environ.get('EVENT_HUB_CONNECTION_STR'))
