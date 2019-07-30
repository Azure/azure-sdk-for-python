import asyncio
import logging
import os
from azure.eventhub.aio import EventHubClient
from azure.eventhub.eventprocessor import EventProcessor
from azure.eventhub.eventprocessor import PartitionProcessor
from azure.eventhub.eventprocessor import Sqlite3PartitionManager

logging.basicConfig(level=logging.INFO)


#  Create you own PartitionProcessor
class MyPartitionProcessor(PartitionProcessor):
    async def process_events(self, events):
        print("PartitionProcessor for eventhub:{}, consumer group:{}, partition id:{}, number of events processed:{}".
              format(self._eventhub_name, self._consumer_group_name, self._partition_id, len(events)))
        if events:
            await self._checkpoint_manager.update_checkpoint(events[-1].offset, events[-1].sequence_number)


CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]


async def stop_after_awhile(event_processor, duration):
    await asyncio.sleep(duration)
    await event_processor.stop()


async def main():
    client = EventHubClient.from_connection_string(CONNECTION_STR)
    partition_manager = Sqlite3PartitionManager(db_filename=":memory:")
    event_processor = EventProcessor("$default", client, MyPartitionProcessor, partition_manager)
    await asyncio.gather(event_processor.start(), stop_after_awhile(event_processor, 100))

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
