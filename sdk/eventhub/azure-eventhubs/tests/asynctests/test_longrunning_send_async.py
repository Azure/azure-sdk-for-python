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
import pytest
from logging.handlers import RotatingFileHandler

from azure.eventhub import EventData, EventHubSharedKeyCredential
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


logger = get_logger("send_test_async.log", logging.INFO)


async def get_partitions(args):
    eh_data = await args.get_properties()
    return eh_data["partition_ids"]


async def pump(pid, sender, args, duration):
    deadline = time.time() + duration
    total = 0

    try:
        async with sender:
            event_list = []
            while time.time() < deadline:
                data = EventData(body=b"D" * args.payload)
                event_list.append(data)
                total += 1
                if total % 100 == 0:
                    await sender.send(event_list)
                    event_list = []
                    logger.info("{}: Send total {}".format(pid, total))
    except Exception as err:
        logger.error("{}: Send failed {}".format(pid, err))
        raise
    print("{}: Final Sent total {}".format(pid, total))


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_long_running_partition_send_async(connection_str):
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", help="Duration in seconds of the test", type=int, default=30)
    parser.add_argument("--payload", help="payload size", type=int, default=1024)
    parser.add_argument("--partitions", help="Comma separated partition IDs")
    parser.add_argument("--conn-str", help="EventHub connection string", default=connection_str)
    parser.add_argument("--eventhub", help="Name of EventHub")
    parser.add_argument("--address", help="Address URI to the EventHub entity")
    parser.add_argument("--sas-policy", help="Name of the shared access policy to authenticate with")
    parser.add_argument("--sas-key", help="Shared access key")
    parser.add_argument("--logger-name", help="Unique log file ID")

    loop = asyncio.get_event_loop()
    args, _ = parser.parse_known_args()

    if args.conn_str:
        client = EventHubClient.from_connection_string(
            args.conn_str,
            event_hub_path=args.eventhub, network_tracing=False)
    elif args.address:
        client = EventHubClient(host=args.address,
                                event_hub_path=args.eventhub,
                                credential=EventHubSharedKeyCredential(args.sas_policy, args.sas_key),
                                network_tracing=False)
    else:
        try:
            import pytest
            pytest.skip("Must specify either '--conn-str' or '--address'")
        except ImportError:
            raise ValueError("Must specify either '--conn-str' or '--address'")

    try:
        if not args.partitions:
            partitions = await client.get_partition_ids()
        else:
            pid_range = args.partitions.split("-")
            if len(pid_range) > 1:
                partitions = [str(i) for i in range(int(pid_range[0]), int(pid_range[1]) + 1)]
            else:
                partitions = args.partitions.split(",")
        pumps = []
        for pid in partitions:
            sender = client.create_producer(partition_id=pid, send_timeout=0)
            pumps.append(pump(pid, sender, args, args.duration))
        results = await asyncio.gather(*pumps, return_exceptions=True)
        assert not results
    except Exception as e:
        logger.error("EventHubProducer failed: {}".format(e))


if __name__ == '__main__':
    asyncio.run(test_long_running_partition_send_async(os.environ.get('EVENT_HUB_PERF_CONN_STR')))
