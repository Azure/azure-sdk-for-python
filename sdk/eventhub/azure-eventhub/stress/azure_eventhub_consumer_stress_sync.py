# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import time
import datetime
import argparse
import threading
import os
import logging
from collections import defaultdict

from azure.identity import ClientSecretCredential
from azure.eventhub.extensions.checkpointstoreblob import BlobCheckpointStore
from azure.eventhub import EventHubConsumerClient, TransportType, EventHubSharedKeyCredential

from logger import get_logger
from process_monitor import ProcessMonitor


def parse_starting_position(args):
    starting_position = None
    if args.starting_offset:
        starting_position = str(args.starting_offset)
    if args.starting_sequence_number:
        starting_position = int(args.starting_sequence_number)
    if args.starting_datetime:
        starting_position = datetime.datetime.strptime(str(args.starting_datetime), '%Y-%m-%d %H:%M:%S')

    if not starting_position:
        starting_position = "-1"

    return starting_position


parser = argparse.ArgumentParser()
parser.add_argument("--link_credit", default=3000, type=int)
parser.add_argument("--output_interval", type=float, default=1000)
parser.add_argument("--duration", help="Duration in seconds of the test", type=int, default=30)
parser.add_argument("--consumer_group", help="Consumer group name", default="$default")
parser.add_argument("--auth_timeout", help="Authorization Timeout", type=float, default=60)
parser.add_argument("--starting_offset", help="Starting offset", type=str)
parser.add_argument("--starting_sequence_number", help="Starting sequence number", type=int)
parser.add_argument("--starting_datetime", help="Starting datetime string, should be format of YYYY-mm-dd HH:mm:ss")
parser.add_argument("--partitions", help="Number of partitions. 0 means to get partitions from eventhubs", type=int, default=0)
parser.add_argument("--recv_partition_id", help="Receive from a specific partition if this is set", type=int)
parser.add_argument("--track_last_enqueued_event_properties", action="store_true")
parser.add_argument("--load_balancing_interval", help="time duration in seconds between two load balance", type=float, default=10)
parser.add_argument("--conn_str", help="EventHub connection string",
                    default=os.environ.get('EVENT_HUB_PERF_32_CONN_STR'))
parser.add_argument("--eventhub", help="Name of EventHub")
parser.add_argument("--address", help="Address URI to the EventHub entity")
parser.add_argument("--sas-policy", help="Name of the shared access policy to authenticate with")
parser.add_argument("--sas-key", help="Shared access key")
parser.add_argument(
    "--transport_type",
    help="Transport type, 0 means AMQP, 1 means AMQP over WebSocket",
    type=int,
    default=0
)
parser.add_argument("--parallel_recv_cnt", help="Number of receive clients doing parallel receiving", type=int)
parser.add_argument("--proxy_hostname", type=str)
parser.add_argument("--proxy_port", type=str)
parser.add_argument("--proxy_username", type=str)
parser.add_argument("--proxy_password", type=str)
parser.add_argument("--aad_client_id", help="AAD client id")
parser.add_argument("--aad_secret", help="AAD secret")
parser.add_argument("--aad_tenant_id", help="AAD tenant id")
parser.add_argument("--storage_conn_str", help="conn str of storage blob to store ownership and checkpoint data")
parser.add_argument("--storage_container_name", help="storage container name to store ownership and checkpoint data")
parser.add_argument("--uamqp_logging_enable", help="uamqp logging enable", action="store_true")
parser.add_argument("--print_console", help="print to console", action="store_true")
parser.add_argument("--log_filename", help="log file name", type=str)

args = parser.parse_args()
starting_position = parse_starting_position(args)
LOGGER = get_logger(args.log_filename, "stress_receive_sync", level=logging.INFO, print_console=args.print_console)
LOG_PER_COUNT = args.output_interval

start_time = time.perf_counter()
recv_cnt_map = defaultdict(int)
recv_time_map = dict()


class EventHubConsumerClientTest(EventHubConsumerClient):
    def get_partition_ids(self):
        if args.partitions != 0:
            return [str(i) for i in range(args.partitions)]
        else:
            return super(EventHubConsumerClientTest, self).get_partition_ids()


def on_event_received(partition_context, event):
    recv_cnt_map[partition_context.partition_id] += 1
    if recv_cnt_map[partition_context.partition_id] % LOG_PER_COUNT == 0:
        total_time_elapsed = time.perf_counter() - start_time

        partition_previous_time = recv_time_map.get(partition_context.partition_id)
        partition_current_time = time.perf_counter()
        recv_time_map[partition_context.partition_id] = partition_current_time
        LOGGER.info("Partition: %r, Total received: %r, Time elapsed: %r, Speed since start: %r/s, Current speed: %r/s",
                    partition_context.partition_id,
                    recv_cnt_map[partition_context.partition_id],
                    total_time_elapsed,
                    recv_cnt_map[partition_context.partition_id] / total_time_elapsed,
                    LOG_PER_COUNT / (partition_current_time - partition_previous_time) if partition_previous_time else None
                    )
        partition_context.update_checkpoint(event)


def create_client(args):
    if args.storage_conn_str:
        checkpoint_store = BlobCheckpointStore.from_connection_string(args.storage_conn_str, args.storage_container_name)
    else:
        checkpoint_store = None

    transport_type = TransportType.Amqp if args.transport_type == 0 else TransportType.AmqpOverWebsocket
    http_proxy = None
    if args.proxy_hostname:
        http_proxy = {
            "proxy_hostname": args.proxy_hostname,
            "proxy_port": args.proxy_port,
            "username": args.proxy_username,
            "password": args.proxy_password,
        }

    if args.conn_str:
        client = EventHubConsumerClientTest.from_connection_string(
            args.conn_str,
            args.consumer_group,
            eventhub_name=args.eventhub,
            checkpoint_store=checkpoint_store,
            load_balancing_interval=args.load_balancing_interval,
            auth_timeout=args.auth_timeout,
            http_proxy=http_proxy,
            transport_type=transport_type,
            logging_enable=args.uamqp_logging_enable
        )
    elif args.hostname:
        client = EventHubConsumerClientTest(
            fully_qualified_namespace=args.hostname,
            eventhub_name=args.eventhub,
            consumer_group=args.consumer_group,
            credential=EventHubSharedKeyCredential(args.sas_policy, args.sas_key),
            checkpoint_store=checkpoint_store,
            load_balancing_interval=args.load_balancing_interval,
            auth_timeout=args.auth_timeout,
            http_proxy=http_proxy,
            transport_type=transport_type,
            logging_enable=args.uamqp_logging_enable
        )
    elif args.aad_client_id:
        credential = ClientSecretCredential(args.tenant_id, args.aad_client_id, args.aad_secret)
        client = EventHubConsumerClientTest(
            fully_qualified_namespace=args.hostname,
            eventhub_name=args.eventhub,
            consumer_group=args.consumer_group,
            credential=credential,
            checkpoint_store=checkpoint_store,
            load_balancing_interval=args.load_balancing_interval,
            auth_timeout=args.auth_timeout,
            http_proxy=http_proxy,
            transport_type=transport_type,
            logging_enable=args.uamqp_logging_enable
        )

    return client


def run(args):
    with ProcessMonitor("monitor_{}".format(args.log_filename), "consumer_stress_sync", print_console=args.print_console):
        kwargs_dict = {
            "prefetch": args.link_credit,
            "partition_id": str(args.recv_partition_id) if args.recv_partition_id else None,
            "track_last_enqueued_event_properties": args.track_last_enqueued_event_properties,
            "starting_position": starting_position
        }
        if args.parallel_recv_cnt and args.parallel_recv_cnt > 1:
            clients = [create_client(args) for _ in range(args.parallel_recv_cnt)]
            threads = [
                threading.Thread(
                    target=clients[i].receive,
                    args=(on_event_received,),
                    kwargs=kwargs_dict,
                    daemon=True
                ) for i in range(args.parallel_recv_cnt)
            ]
        else:
            clients = [create_client(args)]
            threads = [threading.Thread(
                target=clients[0].receive,
                args=(on_event_received,),
                kwargs=kwargs_dict,
                daemon=True
            )]

        for thread in threads:
            thread.start()
        time.sleep(args.duration)
        for client in clients:
            client.close()
        for thread in threads:
            thread.join()


if __name__ == '__main__':
    run(args)
