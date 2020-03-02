import os
from azure.eventhub import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblob import BlobCheckpointStore

CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
STORAGE_CONNECTION_STR = os.environ["AZURE_STORAGE_CONN_STR"]
BLOB_CONTAINER_NAME = "your-blob-container-name"  # Please make sure the blob container resource exists.
STORAGE_SERVICE_API_VERSION = "2019-02-02"


def on_event(partition_context, event):
    # Put your code here.
    # Avoid time-consuming operations.
    print(event)
    partition_context.update_checkpoint(event)


if __name__ == '__main__':
    checkpoint_store = BlobCheckpointStore.from_connection_string(
        STORAGE_CONNECTION_STR,
        container_name=BLOB_CONTAINER_NAME,
        api_version=STORAGE_SERVICE_API_VERSION  # api_version default value is "2019-02-02"
    )
    client = EventHubConsumerClient.from_connection_string(
        CONNECTION_STR,
        "$Default",
        checkpoint_store=checkpoint_store
    )

    try:
        client.receive(on_event)
    except KeyboardInterrupt:
        client.close()
