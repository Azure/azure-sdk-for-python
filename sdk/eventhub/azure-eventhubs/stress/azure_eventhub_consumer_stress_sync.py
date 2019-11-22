import time
import argparse
import threading
import os
import logging
from collections import defaultdict
from logger import get_logger

from azure.storage.blob import ContainerClient
from azure.eventhub.extensions.checkpointstoreblob import BlobCheckpointStore
from azure.eventhub import EventHubConsumerClient

parser = argparse.ArgumentParser()
parser.add_argument("--link_credit", default=3000, type=int)
parser.add_argument("--output_interval", type=float, default=1000)
parser.add_argument("--duration", help="Duration in seconds of the test", type=int, default=30)
parser.add_argument("--consumer", help="Consumer group name", default="$default")
parser.add_argument("--offset", help="Starting offset", default="-1")
parser.add_argument("--partitions", help="Number of partitions. 0 means to get partitions from eventhubs", type=int, default=0)
parser.add_argument("--load_balancing_interval", help="time duration in seconds between two load balance", type=float, default=10)
parser.add_argument("--conn_str", help="EventHub connection string",
                    default=os.environ.get('EVENT_HUB_PERF_32_CONN_STR'))
parser.add_argument("--eventhub", help="Name of EventHub")
parser.add_argument("--address", help="Address URI to the EventHub entity")
parser.add_argument("--sas-policy", help="Name of the shared access policy to authenticate with")
parser.add_argument("--sas-key", help="Shared access key")
parser.add_argument("--aad_client_id", help="AAD client id")
parser.add_argument("--aad_secret", help="AAD secret")
parser.add_argument("--aad_tenant_id", help="AAD tenant id")
parser.add_argument("--payload", help="payload size", type=int, default=1024)
parser.add_argument("--storage_conn_str", help="conn str of storage blob to store ownership and checkpoint data")
parser.add_argument("--storage_container_name", help="storage container name to store ownership and checkpoint data")
parser.add_argument("--print_console", help="print to console", type=bool, default=False)

args = parser.parse_args()
LOGGER = get_logger("stress_receive_sync.log", "stress_receive_sync", level=logging.INFO, print_console=args.print_console)
LOG_PER_COUNT = args.output_interval

start_time = time.perf_counter()
recv_cnt_map = defaultdict(int)
recv_time_map = dict()


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


def run(args):
    class EventHubConsumerClientTest(EventHubConsumerClient):
        def get_partition_ids(self):
            if args.partitions != 0:
                return [str(i) for i in range(args.partitions)]
            else:
                return super(EventHubConsumerClientTest, self).get_partition_ids()

    if args.storage_conn_str:
        checkpoint_store = BlobCheckpointStore(
            ContainerClient.from_connection_string(args.storage_conn_str, args.storage_container_name))
    else:
        checkpoint_store = None
    client = EventHubConsumerClientTest.from_connection_string(
        args.conn_str, args.consumer, eventhub_name=args.eventhub, checkpoint_store=checkpoint_store,
        load_balancing_interval=args.load_balancing_interval
    )
    with client:
        thread = threading.Thread(target=client.receive,
                                  args=(on_event_received,),
                                  kwargs={"prefetch": args.link_credit})
        thread.start()
        time.sleep(args.duration)
    thread.join()


if __name__ == '__main__':
    run(args)
