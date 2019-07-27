from typing import List
from abc import ABC, abstractmethod
from .checkpoint_manager import CheckpointManager

from azure.eventhub import EventData


class PartitionProcessor(ABC):
    def __init__(self, eventhub_name, consumer_group_name, partition_id, checkpoint_manager: CheckpointManager):
        self.partition_id = partition_id
        self.eventhub_name = eventhub_name
        self.consumer_group_name = consumer_group_name
        self.checkpoint_manager = checkpoint_manager

    async def close(self, reason):
        """Called when EventProcessor stops processing this PartitionProcessor.

        """
        pass

    @abstractmethod
    async def process_events(self, events: List[EventData]):
        """Called when a batch of events have been received.

        """
        pass

    async def process_error(self, error):
        """Called when the underlying event hub partition consumer experiences an non-retriable error during receiving.

        """
        pass
