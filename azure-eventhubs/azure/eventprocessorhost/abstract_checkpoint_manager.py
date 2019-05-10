# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

"""
Author: Aaron (Ari) Bornstien
"""
from abc import ABC, abstractmethod

class AbstractCheckpointManager(ABC):
    """
    If you wish to have EventProcessorHost store checkpoints somewhere other than Azure Storage,
    you can write your own checkpoint manager using this abstract class.
    """
    def __init__(self):
        pass

    @abstractmethod
    async def create_checkpoint_store_if_not_exists_async(self):
        """
        Create the checkpoint store if it doesn't exist. Do nothing if it does exist.

        :return: `True` if the checkpoint store already exists or was created OK, `False`
         if there was a failure.
        :rtype: bool
        """

    @abstractmethod
    async def get_checkpoint_async(self, partition_id):
        """
        Get the checkpoint data associated with the given partition.
        Could return null if no checkpoint has been created for that partition.

        :param partition_id: The ID of a given parition.
        :type partition_id: str
        :return: Given partition checkpoint info, or `None` if none has been previously stored.
        :rtype: ~azure.eventprocessorhost.checkpoint.Checkpoint
        """

    @abstractmethod
    async def create_checkpoint_if_not_exists_async(self, partition_id):
        """
        Create the given partition checkpoint if it doesn't exist.Do nothing if it does exist.
        The offset/sequenceNumber for a freshly-created checkpoint should be set to StartOfStream/0.

        :param partition_id: The ID of a given parition.
        :type partition_id: str
        :return: The checkpoint for the given partition, whether newly created or already existing.
        :rtype: ~azure.eventprocessorhost.checkpoint.Checkpoint
        """

    @abstractmethod
    async def update_checkpoint_async(self, lease, checkpoint):
        """
        Update the checkpoint in the store with the offset/sequenceNumber in the provided checkpoint.

        :param lease: The lease to be updated.
        :type lease: ~azure.eventprocessorhost.lease.Lease
        :param checkpoint: offset/sequeceNumber to update the store with.
        :type checkpoint: ~azure.eventprocessorhost.checkpoint.Checkpoint
        """

    @abstractmethod
    async def delete_checkpoint_async(self, partition_id):
        """
        Delete the stored checkpoint for the given partition. If there is no stored checkpoint
        for the given partition, that is treated as success.

        :param partition_id: The ID of a given parition.
        :type partition_id: str
        """
