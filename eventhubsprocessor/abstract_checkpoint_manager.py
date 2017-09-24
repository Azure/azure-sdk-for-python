#  If you wish to have EventProcessorHost store checkpoints somewhere other than Azure Storage, you can write your own checkpoint manager using this abstract class.  
from abc import ABC, abstractmethod
  
class AbstractCheckpointManager(ABC):
    def __init__(self):
        super(AbstractCheckpointManager, self).__init__()
    
    #  Does the checkpoint store exist?
    #  (Returns) true if it exists, false if not
    @abstractmethod
    def checkpointStoreExistsAsync():
        pass

    #  Create the checkpoint store if it doesn't exist. Do nothing if it does exist.
    #  (Returns) true if the checkpoint store already exists or was created OK, false if there was a failure
    @abstractmethod
    def createCheckpointStoreIfNotExistsAsync():
        pass

    #  Get the checkpoint data associated with the given partition. Could return null if no checkpoint has been created for that partition.
    #  (Params) partitionId: Id of partition to create the checkpoint for.
    #  (Returns) Checkpoint info for the given partition, or null if none has been previously stored.
    @abstractmethod
    def getCheckpointAsync(partitionId):
        pass

    #  Create the checkpoint for the given partition if it doesn't exist. Do nothing if it does exist.
    #  The offset/sequenceNumber for a freshly-created checkpoint should be set to StartOfStream/0.
    #  (Params) partitionId: Id of partition to create the checkpoint for.
    #  (Returns) The checkpoint for the given partition, whether newly created or already existing.
    @abstractmethod
    def createCheckpointIfNotExistsAsync(partitionId):
        pass

    #  Update the checkpoint in the store with the offset/sequenceNumber in the provided checkpoint.
    #  (Params) lease: Partition information against which to perform a checkpoint, checkpoint: offset/sequeceNumber to update the store with.
    @abstractmethod
    def updateCheckpointAsync(lease, checkpoint):
        pass

    #  Delete the stored checkpoint for the given partition. If there is no stored checkpoint for the given partition, that is treated as success.
    #  (Params) partitionId: id of partition to delete checkpoint from store
    @abstractmethod
    def deleteCheckpointAsync(partitionId):
        pass