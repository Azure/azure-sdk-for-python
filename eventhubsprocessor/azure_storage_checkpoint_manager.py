"""
Author: Aaron (Ari) Bornstien
"""
import re
import json
import uuid
import logging
from azure.storage.blob import BlockBlobService
from eventhubsprocessor.azure_blob_lease import AzureBlobLease
from eventhubsprocessor.checkpoint import Checkpoint
from eventhubsprocessor.abstract_lease_manager import AbstractLeaseManager
from eventhubsprocessor.abstract_checkpoint_manager import AbstractCheckpointManager

class AzureStorageCheckpointLeaseManager(AbstractCheckpointManager, AbstractLeaseManager):
    """
    Manages checkpoints and lease with azure storage blobs. In this implementation,
    checkpoints are data that's actually in the lease blob, so checkpoint operations
    turn into lease operations under the covers.
    """
    def __init__(self, storage_account_name, storage_account_key, lease_container_name,
                 storage_blob_prefix=None, lease_renew_interval=10, lease_duration=30):
        AbstractCheckpointManager.__init__(self)
        AbstractLeaseManager.__init__(self, lease_renew_interval, lease_duration)
        self.storage_account_name = storage_account_name
        self.storage_account_key = storage_account_key
        self.lease_container_name = lease_container_name
        self.storage_blob_prefix = storage_blob_prefix
        self.storage_client = None
        self.consumer_group_directory = None
        self.host = None
        self.storage_max_execution_time = 120

        # Validate storage inputs
        if not self.storage_account_name or not self.storage_account_key:
            raise ValueError("Need a valid storage account name and key")
        if not re.compile(r"^[a-z0-9](([a-z0-9\-[^\-])){1,61}[a-z0-9]$").match(self.lease_container_name):
            raise ValueError("Azure Storage lease container name is invalid.\
                              Please check naming conventions at\
                              https:# msdn.microsoft.com/en-us/library/azure/dd135715.aspx")

        if self.storage_blob_prefix:
            self.storage_blob_prefix.replace(" ", "") # Convert all-whitespace to empty string.
        else:
            self.storage_blob_prefix = "" # Convert null prefix to empty string.

    def initialize(self, host):
        """
        The EventProcessorHost can't pass itself to the AzureStorageCheckpointLeaseManager
        constructor because it is still being constructed. Do other initialization here
        also because it might throw and hence we don't want it in the constructor.
        """
        self.host = host
        self.storage_client = BlockBlobService(account_name=self.storage_account_name,
                                               account_key=self.storage_account_key)
        self.consumer_group_directory = self.storage_blob_prefix + self.host.consumer_group_name

    # Checkpoint Managment Methods

    async def create_checkpoint_store_if_not_exists_async(self):
        """
        Create the checkpoint store if it doesn't exist. Do nothing if it does exist.
        (Returns) true if the checkpoint store already exists or was created OK, false
        if there was a failure
        """
        await self.create_lease_store_if_not_exists_async()

    async def get_checkpoint_async(self, partition_id):
        """
        Get the checkpoint data associated with the given partition.
        Could return null if no checkpoint has been created for that partition.
        (Returns) Given partition checkpoint info, or null if none has been previously stored.
        """
        lease = await self.get_lease_async(partition_id)
        checkpoint = None
        if lease:
            if lease.offset:
                checkpoint = Checkpoint(partition_id, lease.offset,
                                        lease.sequence_number)
        return checkpoint

    async def create_checkpoint_if_not_exists_async(self, partition_id):
        """
        Create the given partition checkpoint if it doesn't exist.Do nothing if it does exist.
        The offset/sequenceNumber for a freshly-created checkpoint should be set to StartOfStream/0.
        (Returns) The checkpoint for the given partition, whether newly created or already existing.
        """
        checkpoint = await self.get_checkpoint_async(partition_id)
        if not checkpoint:
            await self.create_lease_if_not_exists_async(partition_id)
            checkpoint = Checkpoint(partition_id)
        return checkpoint

    async def update_checkpoint_async(self, lease, checkpoint):
        """
        Update the checkpoint in the store with the offset/sequenceNumber in the provided checkpoint
        checkpoint:offset/sequeceNumber to update the store with.
        """
        new_lease = AzureBlobLease()
        new_lease.with_source(lease)
        new_lease.offset = checkpoint.offset
        new_lease.sequence_number = checkpoint.sequence_number
        await self.update_lease_async(new_lease)

    async def delete_checkpoint_async(self, partition_id):
        """
        Delete the stored checkpoint for the given partition. If there is no stored checkpoint
        for the given partition, that is treated as success.
        """
        return  # Make this a no-op to avoid deleting leases by accident.

    # Lease Managment Methods

    async def create_lease_store_if_not_exists_async(self):
        """
        Create the lease store if it does not exist, do nothing if it does exist.
        (Returns) true if the lease store already exists or was created successfully, false if not
        """
        try:
            self.storage_client.create_container(self.lease_container_name)

        except Exception as err:
            logging.error(repr(err))
            raise err

        return True

    async def delete_lease_store_async(self):
        """
        Not used by EventProcessorHost, but a convenient function to have for testing.
        (Returns) true if the lease store was deleted successfully, false if not
        """
        return "Not Supported in Python"

    async def get_lease_async(self, partition_id):
        """
        Return the lease info for the specified partition.
        Can return null if no lease has been created in the store for the specified partition.
        (Returns) lease info for the partition, or null
        """
        try:
            blob = self.storage_client.get_blob_to_text(self.lease_container_name, partition_id)
            lease = AzureBlobLease()
            lease.with_blob(blob)
            def state():
                """
                Allow lease to curry storage_client to get state
                """
                try:
                    return self.storage_client.get_blob_properties(self.lease_container_name,
                                                                   partition_id).properties.lease.state
                except Exception as err:
                    logging.error("Failed to get lease state %s %s", err, partition_id)

            lease.state = state
            return lease
        except Exception as err:
            logging.error("Failed to get lease %s %s", err, partition_id)

    async def get_all_leases(self):
        """
        Return the lease info for all partitions.
        A typical implementation could just call get_lease_async() on all partitions.
        (Returns) list of lease info.
        """
        lease_futures = []
        partition_ids = await self.host.partition_manager.get_partition_ids_async()
        for partition_id in partition_ids:
            lease_futures.append(self.get_lease_async(partition_id))
        return lease_futures

    async def create_lease_if_not_exists_async(self, partition_id):
        """
        Create in the store the lease info for the given partition, if it does not exist.
        Do nothing if it does exist in the store already.
        (Returns) the existing or newly-created lease info for the partition
        """
        return_lease = None
        try:
            return_lease = AzureBlobLease()
            return_lease.partition_id = partition_id
            json_lease = json.dumps(return_lease.serializable())
            logging.info("Creating Lease %s %s %s", self.lease_container_name,
                         partition_id, json_lease)
            self.storage_client.create_blob_from_text(self.lease_container_name,
                                                      partition_id, json_lease)
        except Exception:
            try:
                return_lease = await self.get_lease_async(partition_id)
            except Exception as err:
                logging.error("Failed to create lease %s ", repr(err))
                raise err
        return return_lease

    async def delete_lease_async(self, lease):
        """
        Delete the lease info for the given partition from the store.
        If there is no stored lease for the given partition, that is treated as success.
        """
        self.storage_client.delete_blob(self.lease_container_name, lease.partition_id,
                                        lease_id=lease.token)

    async def acquire_lease_async(self, lease):
        """
        Acquire the lease on the desired partition for this EventProcessorHost.
        Note that it is legal to acquire a lease that is already owned by another host.
        Lease-stealing is how partitions are redistributed when additional hosts are started.
        (Returns) true if the lease was acquired successfully, false if not
        """
        retval = True
        new_lease_id = str(uuid.uuid4())
        partition_id = lease.partition_id
        try:
            if lease.state() == "leased":
                if not lease.token:
                    # We reach here in a race condition: when this instance of EventProcessorHost
                    # scanned the lease blobs, this partition was unowned (token is empty) but
                    # between then and now, another instance of EPH has established a lease
                    # (getLeaseState() is LEASED). We normally enforcethat we only steal the lease
                    # if it is still owned by the instance which owned it when we scanned, but we
                    # can't do that when we don't know who owns it. The safest thing to do is just
                    # fail the acquisition. If that means that one EPH instance gets more partitions
                    # than it should, rebalancing will take care of that quickly enough.
                    retval = False
                else:
                    logging.info("ChangingLease %s %s", self.host.guid, lease.partition_id)
                    self.storage_client.change_blob_lease(self.lease_container_name,
                                                          partition_id, lease.token,
                                                          new_lease_id)
                    lease.token = new_lease_id
            else:
                logging.info("AcquiringLease %s %s", self.host.guid, lease.partition_id)
                lease.token = self.storage_client.acquire_blob_lease(self.lease_container_name,
                                                                     partition_id,
                                                                     self.lease_duration,
                                                                     new_lease_id)
            lease.owner = self.host.host_name
            lease.increment_epoch()
            #check if this solves the issue
            await self.update_lease_async(lease)
        except Exception as err:
            logging.error("Failed to acquire lease %s %s %s", repr(err),
                          partition_id, lease.token)
            return False
        

        return retval

    async def renew_lease_async(self, lease):
        """
        Renew a lease currently held by this host.
        If the lease has been stolen, or expired, or released, it is not possible to renew it.
        You will have to call getLease() and then acquireLease() again.
        (Returns) true if the lease was renewed successfully, false if not
        """
        try:
            self.storage_client.renew_blob_lease(self.lease_container_name,
                                                 lease.partition_id,
                                                 lease_id=lease.token,
                                                 timeout=self.lease_duration)
        except Exception as err:
            if "LeaseIdMismatchWithLeaseOperation" in str(err):
                logging.info("LeaseLost")
            else:
                logging.error("Failed to renew lease on partition %s with token %s %s",
                              lease.partition_id, lease.token, repr(err))
            return False
        return True

    async def release_lease_async(self, lease):
        """
        Give up a lease currently held by this host. If the lease has been stolen, or expired,
        releasing it is unnecessary, and will fail if attempted.
        (Returns) true if the lease was released successfully, false if not
        """
        try:
            logging.info("Releasing lease %s %s", self.host.guid, lease.partition_id)
            lease_id = lease.token
            released_copy = AzureBlobLease()
            released_copy.with_lease(lease)
            released_copy.token = None
            released_copy.owner = None
            released_copy.state = None
            self.storage_client.create_blob_from_text(self.lease_container_name,
                                                      lease.partition_id,
                                                      json.dumps(released_copy.serializable()),
                                                      lease_id=lease_id)
            self.storage_client.release_blob_lease(self.lease_container_name,
                                                   lease.partition_id,
                                                   lease_id)
        except Exception as err:
            logging.error("Failed to release lease %s %s %s",
                          repr(err), lease.partition_id, lease_id)
            return False
        return True


    async def update_lease_async(self, lease):
        """
        Update the store with the information in the provided lease. It is necessary to currently
        hold a lease in order to update it. If the lease has been stolen, or expired, or released,
        it cannot be updated. Updating should renew the lease before performing the update to
        avoid lease expiration during the process.
        (Returns) true if the updated was performed successfully, false if not.
        """
        if lease is None:
            return False

        if not lease.token:
            return False

        logging.info("Updating lease %s %s", self.host.guid, lease.partition_id)

        # First, renew the lease to make sure the update will go through.
        if await self.renew_lease_async(lease):
            try:
                self.storage_client.create_blob_from_text(self.lease_container_name,
                                                          lease.partition_id,
                                                          json.dumps(lease.serializable()),
                                                          lease_id=lease.token)

            except Exception as err:
                logging.error("Failed to update lease %s %s %s", self.host.guid,
                              lease.partition_id, repr(err))
                raise err
        else:
            return False
        return True
