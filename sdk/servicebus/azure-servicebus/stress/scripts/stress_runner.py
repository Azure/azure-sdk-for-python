#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os
import asyncio
from argparse import ArgumentParser
from datetime import timedelta

from azure.servicebus import ServiceBusClient
from azure.servicebus.aio import ServiceBusClient as AsyncServiceBusClient

from stress_test_base import StressTestRunner, StressTestRunnerAsync
from app_insights_metric import AzureMonitorMetric
from process_monitor import ProcessMonitor

CONNECTION_STR = os.environ['SERVICE_BUS_CONNECTION_STR']
QUEUE_NAME = os.environ["SERVICE_BUS_QUEUE_NAME"]


def sync_send(client, args):
    azure_monitor_metric = AzureMonitorMetric("Sync ServiceBus Sender")
    process_monitor = ProcessMonitor("monitor_sender_stress_sync.log", "sender_stress_sync")
    stress_test = StressTestRunner(
        senders=[client.get_queue_sender(QUEUE_NAME)],
        receivers=[],
        message_size=args.message_size,
        send_batch_size=args.send_batch_size,
        duration=timedelta(seconds=args.duration),
        azure_monitor_metric=azure_monitor_metric,
        process_monitor=process_monitor,
        fail_on_exception=False
    )
    stress_test.run()


async def async_send(client, args):
    azure_monitor_metric = AzureMonitorMetric("Async ServiceBus Sender")
    process_monitor = ProcessMonitor("monitor_sender_stress_async.log", "sender_stress_async")
    stress_test = StressTestRunnerAsync(
        senders=[client.get_queue_sender(QUEUE_NAME)],
        receivers=[],
        message_size=args.message_size,
        send_batch_size=args.send_batch_size,
        duration=timedelta(seconds=args.duration),
        azure_monitor_metric=azure_monitor_metric,
        process_monitor=process_monitor,
        fail_on_exception=False
    )
    await stress_test.run_async()


def sync_receive(client, args):
    azure_monitor_metric = AzureMonitorMetric("Sync ServiceBus Receiver")
    process_monitor = ProcessMonitor("monitor_receiver_stress_sync.log", "receiver_stress_sync")
    stress_test = StressTestRunner(
        senders=[],
        receivers=[client.get_queue_receiver(QUEUE_NAME)],
        max_message_count=args.max_message_count,
        receive_type=args.receive_type,
        max_wait_time=args.max_wait_time,
        duration=timedelta(seconds=args.duration),
        azure_monitor_metric=azure_monitor_metric,
        process_monitor=process_monitor,
        fail_on_exception=False
    )
    stress_test.run()


async def async_receive(client, args):
    azure_monitor_metric = AzureMonitorMetric("Async ServiceBus Receiver")
    process_monitor = ProcessMonitor("monitor_receiver_stress_async.log", "receiver_stress_async")
    stress_test = StressTestRunnerAsync(
        senders=[],
        receivers=[client.get_queue_receiver(QUEUE_NAME)],
        max_message_count=args.max_message_count,
        receive_type=args.receive_type,
        max_wait_time=args.max_wait_time,
        duration=timedelta(seconds=args.duration),
        azure_monitor_metric=azure_monitor_metric,
        process_monitor=process_monitor,
        fail_on_exception=False
    )
    await stress_test.run_async()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("--method", type=str)
    parser.add_argument("--duration", type=int, default=259200)
    parser.add_argument("--logging-enable", action="store_true")

    parser.add_argument("--send-batch-size", type=int, default=100)
    parser.add_argument("--message-size", type=int, default=100)

    parser.add_argument("--receive-type", type=str, default="pull")
    parser.add_argument("--max_wait_time", type=int, default=10)
    parser.add_argument("--max_message_count", type=int, default=1)

    args, _ = parser.parse_known_args()
    loop = asyncio.get_event_loop()

    if args.method.startswith("sync"):
        sb_client = ServiceBusClient.from_connection_string(conn_str=CONNECTION_STR)
    else:
        sb_client = AsyncServiceBusClient.from_connection_string(conn_str=CONNECTION_STR)

    if args.method == 'sync_send':
        sync_send(sb_client, args)
    elif args.method == 'async_send':
        loop.run_until_complete(async_send(sb_client, args))
    elif args.method == 'sync_receive':
        sync_receive(sb_client, args)
    elif args.method == 'async_receive':
        loop.run_until_complete(async_receive(sb_client, args))
    else:
        raise RuntimeError("Must set a method to run stress test.")
