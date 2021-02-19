import asyncio
import os
from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblobaio import BlobCheckpointStore

CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']
STORAGE_CONNECTION_STR = os.environ["AZURE_STORAGE_CONN_STR"]
BLOB_CONTAINER_NAME = "your-blob-container-name"  # Please make sure the blob container resource exists.


async def on_event(partition_context, event):
    # Put your code here.
    # Do some sync or async operations. If the operation is i/o intensive, async will have better performance.
    print(event)
    await partition_context.update_checkpoint(event)


async def main(client):
    async with client:
        await client.receive(on_event)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    checkpoint_store = BlobCheckpointStore.from_connection_string(
        STORAGE_CONNECTION_STR,
        container_name=BLOB_CONTAINER_NAME,
    )
    client = EventHubConsumerClient.from_connection_string(
        CONNECTION_STR,
        consumer_group='$Default',
        eventhub_name=EVENTHUB_NAME,
        checkpoint_store=checkpoint_store
    )
    try:
        loop.run_until_complete(main(client))
    finally:
        loop.stop()
