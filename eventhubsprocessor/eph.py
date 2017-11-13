"""
Author: Aaron (Ari) Bornstien
"""
import uuid
import asyncio
from eventhubsprocessor.partition_manager import PartitionManager
class EventProcessorHost:
    """
    Represents a host for processing Event Hubs event data at scale.
    """
    def __init__(self, event_processor, eh_connection_string, consumer_group_name,
                 storage_manager=None, eh_rest_auth=None,
                 eh_options=None, loop=None):
        self.event_processor = event_processor
        self.eh_connection_string = eh_connection_string
        self.eh_rest_auth = eh_rest_auth # Dictionary that contains eh rest api credentials {sb_name,eh_name,token}
        self.consumer_group_name = consumer_group_name
        self.guid = str(uuid.uuid4())
        self.host_name = "host" + str(self.guid)
        self.loop = loop or asyncio.get_event_loop()
        self.eh_options = eh_options or EPHOptions()
        self.partition_manager = PartitionManager(self)
        self.storage_manager = storage_manager
        if self.storage_manager:
            self.storage_manager.initialize(self)

    async def open_async(self):
        """
        Starts the host
        """
        if not self.loop: # If the \
            self.loop = asyncio.get_event_loop()
        await self.partition_manager.start_async()

    async def close_async(self):
        """
        Stops the host
        """
        await self.partition_manager.stop_async()


class EPHOptions:
    """
    Class that contains default and overidable EPH option
    """
    def __init__(self):
        self.max_batch_size = 10
        self.prefetch_count = 300
        self.receive_timeout = 60
        self.initial_offset_provider = "-1"
