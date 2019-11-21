import asyncio
import logging
import os
from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblobaio import BlobCheckpointStore
from azure.storage.blob.aio import ContainerClient

CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]
STORAGE_CONNECTION_STR = os.environ["AZURE_STORAGE_CONN_STR"]

logging.basicConfig(level=logging.INFO)


async def do_operation(event):
    # put your code here
    # do some sync or async operations. If the operation is i/o intensive, async will have better performance
    print(event)


async def process_events(partition_context, events):
    # put your code here
    await asyncio.gather(*[do_operation(event) for event in events])
    await partition_context.update_checkpoint(events[-1])


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    container_client = ContainerClient.from_connection_string(STORAGE_CONNECTION_STR, "eventprocessor")
    checkpoint_store = BlobCheckpointStore(container_client=container_client)
    client = EventHubConsumerClient.from_connection_string(CONNECTION_STR, checkpoint_store=checkpoint_store)
    try:
        loop.run_until_complete(client.receive(process_events, "$default"))
    except KeyboardInterrupt:
        loop.run_until_complete(client.close())
    finally:
        loop.stop()
