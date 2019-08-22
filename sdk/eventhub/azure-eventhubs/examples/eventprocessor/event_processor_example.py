import asyncio
import logging
import os
from azure.eventhub.aio import EventHubClient
from azure.eventhub.eventprocessor import EventProcessor
from azure.eventhub.eventprocessor import Sqlite3PartitionManager

RECEIVE_TIMEOUT = 5  # timeout in seconds for a receiving operation. 0 or None means no timeout
RETRY_TOTAL = 3  # max number of retries for receive operations within the receive timeout. Actual number of retries clould be less if RECEIVE_TIMEOUT is too small
CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]

logging.basicConfig(level=logging.INFO)


async def do_operation(event):
    # do some sync or async operations. If the operation is i/o intensive, async will have better performance
    print(event)


class MyPartitionProcessor(object):
    async def process_events(self, events, checkpoint_manager):
        if events:
            await asyncio.gather(*[do_operation(event) for event in events])
            await checkpoint_manager.update_checkpoint(events[-1].offset, events[-1].sequence_number)
        else:
            print("empty events received", "partition:", checkpoint_manager.partition_id)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    client = EventHubClient.from_connection_string(CONNECTION_STR, receive_timeout=RECEIVE_TIMEOUT, retry_total=RETRY_TOTAL)
    partition_manager = Sqlite3PartitionManager(db_filename="eventprocessor_test_db")
    event_processor = EventProcessor(client, "$default", MyPartitionProcessor, partition_manager, polling_interval=1)
    try:
        loop.run_until_complete(event_processor.start())
    except KeyboardInterrupt:
        loop.run_until_complete(event_processor.stop())
    finally:
        loop.stop()
