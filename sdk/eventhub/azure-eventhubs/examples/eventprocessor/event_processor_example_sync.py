import logging
import os
import time
from azure.eventhub import EventHubConsumerClient, FileBasedPartitionManager, InMemoryPartitionManager

RECEIVE_TIMEOUT = 5  # timeout in seconds for a receiving operation. 0 or None means no timeout
RETRY_TOTAL = 3  # max number of retries for receive operations within the receive timeout. Actual number of retries clould be less if RECEIVE_TIMEOUT is too small
CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]

logging.basicConfig(level=logging.INFO)


def do_operation(event):
    pass


def process_events(partition_context, events):
    if events:
        print("received events: {} from partition: {}".format(len(events), partition_context.partition_id))
        for event in events:
            do_operation(event)

        partition_context.update_checkpoint(events[-1])
    else:
        print("empty events received", "partition:", partition_context.partition_id)


if __name__ == '__main__':
    #partition_manager = FileBasedPartitionManager('consumer_pm_store')
    partition_manager = InMemoryPartitionManager()
    client = EventHubConsumerClient.from_connection_string(
        CONNECTION_STR, partition_manager=partition_manager, receive_timeout=RECEIVE_TIMEOUT, retry_total=RETRY_TOTAL
    )

    try:
        task = client.receive(process_events, '$Default')
        time.sleep(5)
        task.cancel()

    except KeyboardInterrupt:
        task.cancel()


