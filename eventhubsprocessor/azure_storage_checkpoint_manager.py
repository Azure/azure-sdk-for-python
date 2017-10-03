"""
Author: Aaron (Ari) Bornstien
"""
from abstract_lease_manager import AbstractLeaseManager
from abstract_checkpoint_manager import AbstractCheckpointManager

class AzureStorageCheckpointLeaseManager(AbstractCheckpointManager, AbstractLeaseManager):
    """
    Manages checkpoints and lease with azure storage blobs
    """
    def __init__(self, lease_renew_interval, lease_duration):
        AbstractCheckpointManager.__init__()
        AbstractLeaseManager.__init__(lease_renew_interval, lease_duration)

    # Checkpoint Managment Methods

    async def checkpoint_store_exists_async(self):
        """
        Does the checkpoint store exist?
        (Returns) true if it exists, false if not
        """
        pass

    async def create_checkpoint_store_if_not_exists_async(self):
        """
        Create the checkpoint store if it doesn't exist. Do nothing if it does exist.
        (Returns) true if the checkpoint store already exists or was created OK, false
        if there was a failure
        """
        pass

    def get_checkpoint_async(self, partition_id):
        """
        Get the checkpoint data associated with the given partition.
        Could return null if no checkpoint has been created for that partition.
        (Returns) Given partition checkpoint info, or null if none has been previously stored.
        """
        pass

    async def create_checkpoint_if_not_exists_async(self, partition_id):
        """
        Create the given partition checkpoint if it doesn't exist.Do nothing if it does exist.
        The offset/sequenceNumber for a freshly-created checkpoint should be set to StartOfStream/0.
        (Returns) The checkpoint for the given partition, whether newly created or already existing.
        """
        pass

    async def update_checkpoint_async(self, lease, checkpoint):
        """
        Update the checkpoint in the store with the offset/sequenceNumber in the provided checkpoint
        checkpoint:offset/sequeceNumber to update the store with.
        """
        pass

    async def delete_checkpoint_async(self, partition_id):
        """
        Delete the stored checkpoint for the given partition. If there is no stored checkpoint
        for the given partition, that is treated as success.
        """
        pass

    # Lease Managment Methods

    def get_lease_renew_interval(self):
        """
        Allows a lease manager implementation to specify to PartitionManager how often it should
        scan leases and renew them. In order to redistribute leases in a timely fashion after a
        host ceases operating, we recommend a relatively short interval, such as ten seconds.
        Should be less than half of the lease length, to prevent accidental expiration.
        """
        pass

    async def lease_store_exists_async(self):
        """
        Does the lease store exist?
        """
        pass

    async def create_lease_store_if_not_exists_async(self):
        """
        Create the lease store if it does not exist, do nothing if it does exist.
        (Returns) true if the lease store already exists or was created successfully, false if not
        """
        pass

    async def delete_lease_store_async(self):
        """
        Not used by EventProcessorHost, but a convenient function to have for testing.
        (Returns) true if the lease store was deleted successfully, false if not
        """
        pass

    async def get_lease_async(self, partition_id):
        """
        Return the lease info for the specified partition.
        Can return null if no lease has been created in the store for the specified partition.
        (Returns) lease info for the partition, or null
        """
        pass

    def get_all_leases(self):
        """
        Return the lease info for all partitions.
        A typical implementation could just call get_lease_async() on all partitions.
        (Returns) list of lease info.
        """
        pass

    async def create_lease_if_not_exists_async(self, partition_id):
        """
        Create in the store the lease info for the given partition, if it does not exist.
        Do nothing if it does exist in the store already.
        (Returns) the existing or newly-created lease info for the partition
        """
        pass

    async def deleteLeaseAsync(self, lease):
        """
        Delete the lease info for the given partition from the store.
        If there is no stored lease for the given partition, that is treated as success.
        """
        pass

    async def acquire_lease_async(self, lease):
        """
        Acquire the lease on the desired partition for this EventProcessorHost.
        Note that it is legal to acquire a lease that is already owned by another host.
        Lease-stealing is how partitions are redistributed when additional hosts are started.
        (Returns) true if the lease was acquired successfully, false if not
        """
        pass

    async def renew_lease_async(self, lease):
        """
        Renew a lease currently held by this host.
        If the lease has been stolen, or expired, or released, it is not possible to renew it.
        You will have to call getLease() and then acquireLease() again.
        (Returns) true if the lease was renewed successfully, false if not
        """
        pass

    async def release_lease_async(self, lease):
        """
        Give up a lease currently held by this host. If the lease has been stolen, or expired,
        releasing it is unnecessary, and will fail if attempted.
        (Returns) true if the lease was released successfully, false if not
        """
        pass

    async def update_lease_async(self, lease):
        """
        Update the store with the information in the provided lease. It is necessary to currently
        hold a lease in order to update it. If the lease has been stolen, or expired, or released,
        it cannot be updated. Updating should renew the lease before performing the update to
        avoid lease expiration during the process.
        (Returns) true if the updated was performed successfully, false if not.
        """
        pass
