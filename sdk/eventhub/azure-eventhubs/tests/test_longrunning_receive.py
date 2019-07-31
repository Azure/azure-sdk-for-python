#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
receive test.
"""

import logging
import argparse
import time
import os
import sys
import threading
import pytest

from logging.handlers import RotatingFileHandler

from azure.eventhub import EventPosition
from azure.eventhub import EventHubClient
from azure.eventhub import EventHubSharedKeyCredential


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

logger = get_logger("recv_test.log", logging.INFO)


def pump(receiver, duration):
    total = 0
    iteration = 0
    deadline = time.time() + duration
    with receiver:
        try:
            while time.time() < deadline:
                batch = receiver.receive(timeout=5)
                size = len(batch)
                total += size
                iteration += 1
                if size == 0:
                    print("{}: No events received, queue size {}, delivered {}".format(
                        receiver.partition,
                        receiver.queue_size,
                        total))
                elif iteration >= 5:
                    iteration = 0
                    print("{}: total received {}, last sn={}, last offset={}".format(
                                receiver.partition,
                                total,
                                batch[-1].sequence_number,
                                batch[-1].offset))
            print("{}: Total received {}".format(receiver.partition, total))
        except Exception as e:
            print("EventHubConsumer failed: {}".format(e))
            raise


@pytest.mark.liveTest
def test_long_running_receive(connection_str):
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

    args, _ = parser.parse_known_args()
    if args.conn_str:
        client = EventHubClient.from_connection_string(
            args.conn_str,
            event_hub_path=args.eventhub, network_tracing=False)
    elif args.address:
        client = EventHubClient(host=args.address,
                                event_hub_path=args.eventhub,
                                credential=EventHubSharedKeyCredential(args.sas_policy, args.sas_key),
                                auth_timeout=240,
                                network_tracing=False)
    else:
        try:
            import pytest
            pytest.skip("Must specify either '--conn-str' or '--address'")
        except ImportError:
            raise ValueError("Must specify either '--conn-str' or '--address'")

    if args.partitions:
        partitions = args.partitions.split(",")
    else:
        partitions = client.get_partition_ids()

    threads = []
    for pid in partitions:
        consumer = client.create_consumer(consumer_group="$default",
            partition_id=pid,
            event_position=EventPosition(args.offset),
            prefetch=300)
        thread = threading.Thread(target=pump, args=(consumer, args.duration))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()


if __name__ == '__main__':
    test_long_running_receive(os.environ.get('EVENT_HUB_PERF_CONN_STR'))
