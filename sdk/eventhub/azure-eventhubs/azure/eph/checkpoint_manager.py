from .partition_manager import PartitionManager


class CheckpointManager(object):
    """Users use checkpoint manager to update checkpoint。

    """
    def __init__(self, partition_id, eventhub_name, consumer_group_name, instance_id, partition_manager: PartitionManager):
        self.partition_id = partition_id
        self.eventhub_name = eventhub_name
        self.consumer_group_name = consumer_group_name
        self.instance_id = instance_id
        self.partition_manager = partition_manager

    async def update_checkpoint(self,
                                offset, sequence_number):
        await self.partition_manager.\
            update_checkpoint(self.eventhub_name, self.consumer_group_name, self.partition_id, self.instance_id,
            offset, sequence_number)
