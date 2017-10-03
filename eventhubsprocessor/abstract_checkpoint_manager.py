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
    async def checkpoint_store_exists_async(self):
        """
        Does the checkpoint store exist?
        (Returns) true if it exists, false if not
        """
        pass

    @abstractmethod
    async def create_checkpoint_store_if_not_exists_async(self):
        """
        Create the checkpoint store if it doesn't exist. Do nothing if it does exist.
        (Returns) true if the checkpoint store already exists or was created OK, false
        if there was a failure
        """
        pass

    @abstractmethod
    def get_checkpoint_async(self, partition_id):
        """
        Get the checkpoint data associated with the given partition.
        Could return null if no checkpoint has been created for that partition.
        (Returns) Given partition checkpoint info, or null if none has been previously stored.
        """
        pass

    @abstractmethod
    async def create_checkpoint_if_not_exists_async(self, partition_id):
        """
        Create the given partition checkpoint if it doesn't exist.Do nothing if it does exist.
        The offset/sequenceNumber for a freshly-created checkpoint should be set to StartOfStream/0.
        (Returns) The checkpoint for the given partition, whether newly created or already existing.
        """
        pass

    @abstractmethod
    async def update_checkpoint_async(self, lease, checkpoint):
        """
        Update the checkpoint in the store with the offset/sequenceNumber in the provided checkpoint
        checkpoint:offset/sequeceNumber to update the store with.
        """
        pass

    @abstractmethod
    async def delete_checkpoint_async(self, partition_id):
        """
        Delete the stored checkpoint for the given partition. If there is no stored checkpoint
        for the given partition, that is treated as success.
        """
        pass
