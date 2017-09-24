from abstract_lease_manager import AbstractLeaseManager
from abstract_checkpoint_manager import AbstractCheckpointManager

class AzureStorageCheckpointLeaseManager(AbstractCheckpointManager, AbstractLeaseManager):
## Checkpoint Managment Methods 
    #  Does the checkpoint store exist?
    #  (Returns) true if it exists, false if not
    def checkpointStoreExistsAsync():
        pass

    #  Create the checkpoint store if it doesn't exist. Do nothing if it does exist.
    #  (Returns) true if the checkpoint store already exists or was created OK, false if there was a failure
    def createCheckpointStoreIfNotExistsAsync():
        pass

    #  Get the checkpoint data associated with the given partition. Could return null if no checkpoint has been created for that partition.
    #  (Params) partitionId: Id of partition to create the checkpoint for.
    #  (Returns) Checkpoint info for the given partition, or null if none has been previously stored.
    def getCheckpointAsync(partitionId):
        pass

    #  Create the checkpoint for the given partition if it doesn't exist. Do nothing if it does exist.
    #  The offset/sequenceNumber for a freshly-created checkpoint should be set to StartOfStream/0.
    #  (Params) partitionId: Id of partition to create the checkpoint for.
    #  (Returns) The checkpoint for the given partition, whether newly created or already existing.
    def createCheckpointIfNotExistsAsync(partitionId):
        pass

    #  Update the checkpoint in the store with the offset/sequenceNumber in the provided checkpoint.
    #  (Params) lease: Partition information against which to perform a checkpoint, checkpoint: offset/sequeceNumber to update the store with.
    def updateCheckpointAsync(lease, checkpoint):
        pass

    #  Delete the stored checkpoint for the given partition. If there is no stored checkpoint for the given partition, that is treated as success.
    #  (Params) partitionId: id of partition to delete checkpoint from store
    def deleteCheckpointAsync(partitionId):
        pass    
        
## Lease Managment Methods
    # Allows a lease manager implementation to specify to PartitionManager how often it should scan leases and renew them. 
    # In order to redistribute leases in a timely fashion after a host ceases operating, we recommend a relatively short interval, such as ten seconds. 
    # Should be less than half of the lease length, to prevent accidental expiration.
    def getLeaseRenewInterval():
        pass

    # Mostly useful for testing.
    def getLeaseDuration():
        pass

    # Does the lease store exist?
    def leaseStoreExistsAsync():
        pass

    # Create the lease store if it does not exist, do nothing if it does exist.
    # (Returns) true if the lease store already exists or was created successfully, false if not
    def createLeaseStoreIfNotExistsAsync():
        pass

    # Not used by EventProcessorHost, but a convenient function to have for testing.
    # (Returns) true if the lease store was deleted successfully, false if not
    def deleteLeaseStoreAsync():
        pass

    # Return the lease info for the specified partition. Can return null if no lease has been created in the store for the specified partition.
    # (Params) partitionId: id of partition to get lease for</param
    # (Returns) lease info for the partition, or null
    def getLeaseAsync(partitionId):
        pass

    # Return the lease info for all partitions.
    # A typical implementation could just call GetLeaseAsync() on all partitions.
    # (Returns) list of lease info.
    def getAllLeases():
        pass

    # Create in the store the lease info for the given partition, if it does not exist. Do nothing if it does exist in the store already. 
    # (Params) partitionId: id of partition to get lease for</param
    # (Returns) the existing or newly-created lease info for the partition
    def createLeaseIfNotExistsAsync(partitionId):
        pass

    # Delete the lease info for the given partition from the store. If there is no stored lease for the given partition, that is treated as success.
    # (Params) lease: Lease info for the desired partition as previously obtained from GetLeaseAsync()
    def deleteLeaseAsync(lease):
        pass

    # Acquire the lease on the desired partition for this EventProcessorHost.
    # Note that it is legal to acquire a lease that is already owned by another host. Lease-stealing is how partitions are redistributed when additional hosts are started.
    # (Params) lease: Lease info for the desired partition as previously obtained from GetLeaseAsync()
    # (Returns) true if the lease was acquired successfully, false if not
    def acquireLeaseAsync(lease):
        pass

    # Renew a lease currently held by this host.
    # If the lease has been stolen, or expired, or released, it is not possible to renew it. You will have to call getLease() and then acquireLease() again.
    # (Params) lease: Lease info for the desired partition as previously obtained from GetLeaseAsync()
    # (Returns) true if the lease was renewed successfully, false if not
    def renewLeaseAsync(lease):
        pass

    # Give up a lease currently held by this host.
    # If the lease has been stolen, or expired, releasing it is unnecessary, and will fail if attempted.
    # (Params) lease: Lease to be given up
    # (Returns) true if the lease was released successfully, false if not
    def releaseLeaseAsync(lease):
        pass

    # Update the store with the information in the provided lease.
    # It is necessary to currently hold a lease in order to update it. If the lease has been stolen, or expired, or released, it cannot be updated.
    # Updating should renew the lease before performing the update to avoid lease expiration during the process.
    # (Params) lease: New lease info to be stored
    # (Returns) true if the updated was performed successfully, false if not
    def updateLeaseAsync(lease):
        pass