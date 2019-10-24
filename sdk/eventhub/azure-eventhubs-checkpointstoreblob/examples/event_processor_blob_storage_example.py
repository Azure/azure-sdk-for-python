import logging
import os
from azure.eventhub import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblob import BlobPartitionManager
from azure.storage.blob import ContainerClient

RECEIVE_TIMEOUT = 5  # timeout in seconds for a receiving operation. 0 or None means no timeout
RETRY_TOTAL = 3  # max number of retries for receive operations within the receive timeout. Actual number of retries clould be less if RECEIVE_TIMEOUT is too small
CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
STORAGE_CONNECTION_STR = os.environ["AZURE_STORAGE_CONN_STR"]

logging.basicConfig(level=logging.INFO)


def do_operation(event):
    # do some sync or async operations. If the operation is i/o intensive, async will have better performance
    print(event)


def process_events(partition_context, events):
    if events:
        print("received events: {} from partition: {}".format(len(events), partition_context.partition_id))
        for event in events:
            do_operation(event)
        partition_context.update_checkpoint(events[-1])
    else:
        print("empty events received", "partition:", partition_context.partition_id)


if __name__ == '__main__':
    container_client = ContainerClient.from_connection_string(STORAGE_CONNECTION_STR, "eventprocessor")
    partition_manager = BlobPartitionManager(container_client=container_client)
    client = EventHubConsumerClient.from_connection_string(CONNECTION_STR, partition_manager=partition_manager, receive_timeout=RECEIVE_TIMEOUT, retry_total=RETRY_TOTAL)
    try:
        client.receive(process_events, "$default")
    except KeyboardInterrupt:
        client.close()
