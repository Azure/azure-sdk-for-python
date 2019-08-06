#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
send test
"""

import argparse
import time
import os
import sys
import threading
import logging
import pytest
from logging.handlers import RotatingFileHandler

from azure.eventhub import EventHubClient, EventDataBatch, EventData, EventHubSharedKeyCredential


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


logger = get_logger("send_test.log", logging.INFO)


def send(sender, args):
    # sender = client.create_producer()
    deadline = time.time() + args.duration
    total = 0
    try:
        with sender:
            batch = sender.create_batch()
            while time.time() < deadline:
                data = EventData(body=b"D" * args.payload)
                try:
                    batch.try_add(data)
                    total += 1
                except ValueError:
                    sender.send(batch, timeout=0)
                    print("Sent total {} of partition {}".format(total, sender.partition))
                    batch = sender.create_batch()
    except Exception as err:
        print("Partition {} send failed {}".format(sender.partition, err))
        raise
    print("Sent total {} of partition {}".format(total, sender.partition))


@pytest.mark.liveTest
def test_long_running_send(connection_str):
    if sys.platform.startswith('darwin'):
        import pytest
        pytest.skip("Skipping on OSX")
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", help="Duration in seconds of the test", type=int, default=30)
    parser.add_argument("--payload", help="payload size", type=int, default=512)
    parser.add_argument("--conn-str", help="EventHub connection string", default=connection_str)
    parser.add_argument("--eventhub", help="Name of EventHub")
    parser.add_argument("--address", help="Address URI to the EventHub entity")
    parser.add_argument("--sas-policy", help="Name of the shared access policy to authenticate with")
    parser.add_argument("--sas-key", help="Shared access key")

    args, _ = parser.parse_known_args()
    if args.conn_str:
        client = EventHubClient.from_connection_string(
            args.conn_str,
            event_hub_path=args.eventhub)
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

    try:
        partition_ids = client.get_partition_ids()
        threads = []
        for pid in partition_ids:
            sender = client.create_producer(partition_id=pid)
            thread = threading.Thread(target=send, args=(sender, args))
            thread.start()
            threads.append(thread)
        thread.join()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    test_long_running_send(os.environ.get('EVENT_HUB_PERF_CONN_STR'))
