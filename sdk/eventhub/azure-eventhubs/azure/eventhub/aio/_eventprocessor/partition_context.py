# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------


from .partition_manager import PartitionManager


class PartitionContext(object):
    """Contains partition related context information for a PartitionProcessor instance to use.

    Users can use update_checkpoint() of this class to save checkpoint data.
    """
    def __init__(self, fully_qualified_namespace: str, eventhub_name: str, consumer_group_name: str,
                 partition_id: str, owner_id: str, partition_manager: PartitionManager=None):
        self.fully_qualified_namespace = fully_qualified_namespace
        self.partition_id = partition_id
        self.eventhub_name = eventhub_name
        self.consumer_group_name = consumer_group_name
        self.owner_id = owner_id
        self._partition_manager = partition_manager

    async def update_checkpoint(self, event):
        """
        Updates the checkpoint using the given information for the associated partition and consumer group in the
        chosen storage service.

        :param event: The EventData instance. Its offset and sequence number are to be saved in the checkpoint store.
        :type event: EventData
        :return: None
        """
        if self._partition_manager:
            await self._partition_manager.update_checkpoint(
                self.fully_qualified_namespace, self.eventhub_name, self.consumer_group_name,
                self.partition_id, event.offset, event.sequence_number
            )
