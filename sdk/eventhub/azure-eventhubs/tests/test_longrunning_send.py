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
import logging
import pytest
from logging.handlers import RotatingFileHandler

from azure.eventhub import EventHubClient, EventHubProducer, EventData, EventHubSharedKeyCredential


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


def check_send_successful(outcome, condition):
    if outcome.value != 0:
        print("Send failed {}".format(condition))


def main(client, args):
    sender = client.create_producer()
    deadline = time.time() + args.duration
    total = 0

    try:
        with sender:
            event_list = []
            while time.time() < deadline:
                data = EventData(body=b"D" * args.payload)
                event_list.append(data)
                total += 1
                if total % 100 == 0:
                    sender.send(event_list)
                    event_list = []
                    print("Send total {}".format(total))
    except Exception as err:
        print("Send failed {}".format(err))
        raise
    print("Sent total {}".format(total))


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
        main(client, args)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    test_long_running_send(os.environ.get('EVENT_HUB_CONNECTION_STR'))
