import asyncio
import logging
import os
from azure.eventhub.aio import EventHubClient
from azure.eventhub.eventprocessor import EventProcessor
from azure.eventhub.eventprocessor import PartitionProcessor
from azure.eventhub.eventprocessor import Sqlite3PartitionManager

RECEIVE_TIMEOUT = 5  # timeout in seconds for a receiving operation. 0 or None means no timeout
RETRY_TOTAL = 3  # number of retries for receive operations
CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]

logging.basicConfig(level=logging.INFO)


async def do_operation(event):
    # do some sync or async operations. If the operation is i/o intensive, async will have better performance
    print(event)


class MyPartitionProcessor(PartitionProcessor):
    def __init__(self, checkpoint_manager):
        super(MyPartitionProcessor, self).__init__(checkpoint_manager)

    async def process_events(self, events):
        if events:
            await asyncio.gather(*[do_operation(event) for event in events])
            await self._checkpoint_manager.update_checkpoint(events[-1].offset, events[-1].sequence_number)


def partition_processor_factory(checkpoint_manager):
    return MyPartitionProcessor(checkpoint_manager)


async def run_until_interrupt():
    client = EventHubClient.from_connection_string(CONNECTION_STR, receive_timeout=RECEIVE_TIMEOUT, retry_total=RETRY_TOTAL)
    partition_manager = Sqlite3PartitionManager()
    event_processor = EventProcessor(client, "$default", MyPartitionProcessor, partition_manager)
    try:
        # You can also define a callable object for creating PartitionProcessor like below:
        # event_processor = EventProcessor(client, "$default", partition_processor_factory, partition_manager)
        await event_processor.start()
    except KeyboardInterrupt:
        await event_processor.stop()
    finally:
        await partition_manager.close()


async def run_awhile(duration):
    client = EventHubClient.from_connection_string(CONNECTION_STR, receive_timeout=RECEIVE_TIMEOUT,
                                                   retry_total=RETRY_TOTAL)
    partition_manager = Sqlite3PartitionManager()
    event_processor = EventProcessor(client, "$default", MyPartitionProcessor, partition_manager)
    try:
        asyncio.ensure_future(event_processor.start())
        await asyncio.sleep(duration)
        await event_processor.stop()
    finally:
        await partition_manager.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_until_interrupt())

    # use the following code to run for 60 seconds
    # loop.run_until_complete(run_awhile(60))
