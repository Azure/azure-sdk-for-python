import logging
import os
from azure.eventhub import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblob import BlobCheckpointStore
from azure.storage.blob import ContainerClient

CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
STORAGE_CONNECTION_STR = os.environ["AZURE_STORAGE_CONN_STR"]

logging.basicConfig(level=logging.INFO)


def do_operation(event):
    # put your code here
    print(event)


def process_events(partition_context, events):
    # put your code here
    print("received events: {} from partition: {}".format(len(events), partition_context.partition_id))
    for event in events:
        do_operation(event)
    partition_context.update_checkpoint(events[-1])


if __name__ == '__main__':
    container_client = ContainerClient.from_connection_string(STORAGE_CONNECTION_STR, "eventprocessor")
    checkpoint_store = BlobCheckpointStore(container_client=container_client)
    client = EventHubConsumerClient.from_connection_string(CONNECTION_STR, checkpoint_store=checkpoint_store)
    try:
        client.receive(process_events, "$default")
    except KeyboardInterrupt:
        client.close()
