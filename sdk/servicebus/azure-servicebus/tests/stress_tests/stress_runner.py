#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os
from argparse import ArgumentParser

from azure.servicebus import ServiceBusClient

from stress_test_base import StressTestRunner
from app_insights_metric import AzureMonitorMetric


CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
QUEUE_NAME = os.environ["SERVICE_BUS_QUEUE_NAME"]


def sync_send(args):
    # let's start with single sender first
    # message size
    pass


def async_send(args):
    # let's start with single sender first
    # message size
    pass


def sync_receive(args):
    # let's start with single receiver first
    # receive batch size in pull mode
    # prefetch size
    pass


def async_receive(args):
    # let's start with single receiver first
    # receive batch size in pull mode
    # prefetch size
    pass


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("--method", type=str)
    args, _ = parser.parse_known_args()

    if args.method == 'sync_send':
        sync_send(args)
    elif args.method == 'async_send':
        async_send(args)
    elif args.method == 'sync_receive':
        sync_receive(args)
    elif args.method == 'async_receive':
        async_receive(args)
