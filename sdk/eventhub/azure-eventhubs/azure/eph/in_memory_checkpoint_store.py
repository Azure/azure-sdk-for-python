import asyncio
import time
import uuid
from .partition_manager import PartitionManager


class InMemoryPartitionManager(PartitionManager):
    def __init__(self):
        self.lock = asyncio.Lock()
        self.store = dict()

    async def list_ownership(self, eventhub_name, consumer_group_name):
        return self.store.values()

    async def claim_ownership(self, partitions):
        for partition in partitions:
            partition_id = partition["partition_id"]
            if partition_id not in self.store:
                self.store[partition_id] = partition
                partition["last_modified_time"] = time.time()
                partition["ETag"] = uuid.uuid4()
        return partitions

    async def update_checkpoint(self, eventhub_name, consumer_group_name, partition_id, instance_id,
            offset, sequence_number):
        checkpoint = self.store.get(partition_id)
        if not checkpoint:
            checkpoint = dict()
            self.store[partition_id] = checkpoint
        checkpoint["eventhub_name"] = eventhub_name
        checkpoint["consumer_group_name"] = consumer_group_name
        checkpoint["instance_id"] = instance_id
        checkpoint["partition_id"] = partition_id
        checkpoint["offset"] = offset
        checkpoint["sequence_number"] = sequence_number

        print("checkpoint saved: ", checkpoint)
