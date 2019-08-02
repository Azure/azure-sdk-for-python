# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------


from .partition_manager import PartitionManager


class CheckpointManager(object):
    """Every PartitionProcessor has a CheckpointManager to save the partition's checkpoint.

    """
    def __init__(self, partition_id, eventhub_name, consumer_group_name, instance_id, partition_manager: PartitionManager):
        self._partition_id = partition_id
        self._eventhub_name = eventhub_name
        self._consumer_group_name = consumer_group_name
        self._instance_id = instance_id
        self._partition_manager = partition_manager

    async def update_checkpoint(self, offset, sequence_number):
        """Users call this method in PartitionProcessor.process_events() to save checkpoints

        :param offset: offset of the processed EventData
        :param sequence_number: sequence_number of the processed EventData
        :return: None
        """
        await self._partition_manager.update_checkpoint(
            self._eventhub_name, self._consumer_group_name, self._partition_id, self._instance_id, offset,
            sequence_number
        )
