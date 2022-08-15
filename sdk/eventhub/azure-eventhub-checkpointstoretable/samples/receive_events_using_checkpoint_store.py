import os
from azure.eventhub import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoretable import TableCheckpointStore

CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
EVENTHUB_NAME = os.environ["EVENT_HUB_NAME"]
STORAGE_CONNECTION_STR = os.environ["AZURE_STORAGE_CONN_STR"]
TABLE_NAME = "your-table-name"  # Please make sure the table resource exists.


def on_event(partition_context, event):
    # Put your code here.
    # Avoid time-consuming operations.
    print(event)
    partition_context.update_checkpoint(event)


if __name__ == "__main__":
    checkpoint_store = TableCheckpointStore.from_connection_string(
        STORAGE_CONNECTION_STR,
        table_name=TABLE_NAME,
    )
    client = EventHubConsumerClient.from_connection_string(
        CONNECTION_STR,
        consumer_group="$Default",
        eventhub_name=EVENTHUB_NAME,
        checkpoint_store=checkpoint_store,
    )

    try:
        client.receive(on_event)
    except KeyboardInterrupt:
        client.close()
