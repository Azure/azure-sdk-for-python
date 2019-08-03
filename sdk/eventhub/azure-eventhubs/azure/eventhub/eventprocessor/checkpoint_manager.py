# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------


from .partition_manager import PartitionManager


class CheckpointManager(object):
    """Every PartitionProcessor has a CheckpointManager to save the partition's checkpoint.

    """
    def __init__(self, partition_id: str, eventhub_name: str, consumer_group_name: str, owner_id: str, partition_manager: PartitionManager):
        self.partition_id = partition_id
        self.eventhub_name = eventhub_name
        self.consumer_group_name = consumer_group_name
        self.owner_id = owner_id
        self.partition_manager = partition_manager

    async def update_checkpoint(self, offset, sequence_number=None):
        """Users call this method in PartitionProcessor.process_events() to save checkpoints

        :param offset: offset of the processed EventData
        :param sequence_number: sequence_number of the processed EventData
        :return: None
        """
        await self.partition_manager.update_checkpoint(
            self.eventhub_name, self.consumer_group_name, self.partition_id, self.owner_id, offset,
            sequence_number
        )
