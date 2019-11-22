import os
from azure.eventhub import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblob import BlobCheckpointStore

CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
STORAGE_CONNECTION_STR = os.environ["AZURE_STORAGE_CONN_STR"]


def on_event(partition_context, event):
    # do something with event
    print(event)
    partition_context.update_checkpoint(event)


if __name__ == '__main__':
    checkpoint_store = BlobCheckpointStore.from_connection_string(STORAGE_CONNECTION_STR, "eventprocessor")
    client = EventHubConsumerClient.from_connection_string(
        CONNECTION_STR, "$default", checkpoint_store=checkpoint_store)

    try:
        client.receive(on_event)
    except KeyboardInterrupt:
        client.close()
