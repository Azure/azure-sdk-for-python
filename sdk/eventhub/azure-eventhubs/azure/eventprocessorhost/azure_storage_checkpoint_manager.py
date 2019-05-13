# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

import re
import json
import uuid
import logging
import concurrent.futures
import functools
import asyncio
import requests

from azure.storage.blob import BlockBlobService
from azure.eventprocessorhost.azure_blob_lease import AzureBlobLease
from azure.eventprocessorhost.checkpoint import Checkpoint
from azure.eventprocessorhost.abstract_lease_manager import AbstractLeaseManager
from azure.eventprocessorhost.abstract_checkpoint_manager import AbstractCheckpointManager


_logger = logging.getLogger(__name__)


class AzureStorageCheckpointLeaseManager(AbstractCheckpointManager, AbstractLeaseManager):
    """
    Manages checkpoints and lease with azure storage blobs. In this implementation,
    checkpoints are data that's actually in the lease blob, so checkpoint operations
    turn into lease operations under the covers.

    :param str storage_account_name: The storage account name. This is used to
     authenticate requests signed with an account key and to construct the storage
     endpoint. It is required unless a connection string is given.
    :param str storage_account_key: The storage account key. This is used for shared key
     authentication. If neither account key or sas token is specified, anonymous access
     will be used.
    :param str lease_container_name: The name of the container that will be used to store
     leases. If it does not already exist it will be created. Default value is 'eph-leases'.
    :param int lease_renew_interval: The interval in seconds at which EPH will attempt to
     renew the lease of a particular partition. Default value is 10.
    :param int lease_duration: The duration in seconds of a lease on a partition.
     Default value is 30.
    :param str sas_token: A shared access signature token to use to authenticate requests
     instead of the account key. If account key and sas token are both specified,
     account key will be used to sign. If neither are specified, anonymous access will be used.
    :param str endpoint_suffix: The host base component of the url, minus the account name.
     Defaults to Azure (core.windows.net). Override this to use a National Cloud.
    :param str connection_string: If specified, this will override all other endpoint parameters.
     See http://azure.microsoft.com/en-us/documentation/articles/storage-configure-connection-string/
     for the connection string format.
    """

    def __init__(self, storage_account_name=None, storage_account_key=None, lease_container_name="eph-leases",
                 storage_blob_prefix=None, lease_renew_interval=10, lease_duration=30,
                 sas_token=None, endpoint_suffix="core.windows.net", connection_string=None):
        AbstractCheckpointManager.__init__(self)
        AbstractLeaseManager.__init__(self, lease_renew_interval, lease_duration)
        self.storage_account_name = storage_account_name
        self.storage_account_key = storage_account_key
        self.storage_sas_token = sas_token
        self.endpoint_suffix = endpoint_suffix
        self.connection_string = connection_string
        self.lease_container_name = lease_container_name
        self.storage_blob_prefix = storage_blob_prefix
        self.storage_client = None
        self.consumer_group_directory = None
        self.host = None
        self.storage_max_execution_time = 120
        self.request_session = requests.Session()
        self.request_session.mount('https://', requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100))
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=32)

        # Validate storage inputs
        if not self.storage_account_name and not self.connection_string:
            raise ValueError("Need a valid storage account name or connection string.")
        if not re.compile(r"^[a-z0-9](([a-z0-9\-[^\-])){1,61}[a-z0-9]$").match(self.lease_container_name):
            raise ValueError("Azure Storage lease container name is invalid.\
                              Please check naming conventions at\
                              https:# msdn.microsoft.com/en-us/library/azure/dd135715.aspx")

        if self.storage_blob_prefix:
            self.storage_blob_prefix.replace(" ", "")  # Convert all-whitespace to empty string.
        else:
            self.storage_blob_prefix = ""  # Convert null prefix to empty string.

    def initialize(self, host):
        """
        The EventProcessorHost can't pass itself to the AzureStorageCheckpointLeaseManager
        constructor because it is still being constructed. Do other initialization here
        also because it might throw and hence we don't want it in the constructor.
        """
        self.host = host
        self.storage_client = BlockBlobService(account_name=self.storage_account_name,
                                               account_key=self.storage_account_key,
                                               sas_token=self.storage_sas_token,
                                               endpoint_suffix=self.endpoint_suffix,
                                               connection_string=self.connection_string,
                                               request_session=self.request_session)
        self.consumer_group_directory = self.storage_blob_prefix + self.host.eh_config.consumer_group

    # Checkpoint Managment Methods

    async def create_checkpoint_store_if_not_exists_async(self):
        """
        Create the checkpoint store if it doesn't exist. Do nothing if it does exist.

        :return: `True` if the checkpoint store already exists or was created OK, `False`
         if there was a failure.
        :rtype: bool
        """
        await self.create_lease_store_if_not_exists_async()

    async def get_checkpoint_async(self, partition_id):
        """
        Get the checkpoint data associated with the given partition.
        Could return null if no checkpoint has been created for that partition.

        :param partition_id: The partition ID.
        :type partition_id: str
        :return: Given partition checkpoint info, or `None` if none has been previously stored.
        :rtype: ~azure.eventprocessorhost.checkpoint.Checkpoint
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

        :param partition_id: The partition ID.
        :type partition_id: str
        :return: The checkpoint for the given partition, whether newly created or already existing.
        :rtype: ~azure.eventprocessorhost.checkpoint.Checkpoint
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

        :param lease: The stored lease to be updated.
        :type lease: ~azure.eventprocessorhost.lease.Lease
        :param checkpoint: The checkpoint to update the lease with.
        :type checkpoint: ~azure.eventprocessorhost.checkpoint.Checkpoint
        """
        new_lease = AzureBlobLease()
        new_lease.with_source(lease)
        new_lease.offset = checkpoint.offset
        new_lease.sequence_number = checkpoint.sequence_number
        return await self.update_lease_async(new_lease)

    async def delete_checkpoint_async(self, partition_id):
        """
        Delete the stored checkpoint for the given partition. If there is no stored checkpoint
        for the given partition, that is treated as success.

        :param partition_id: The partition ID.
        :type partition_id: str
        """
        return  # Make this a no-op to avoid deleting leases by accident.

    # Lease Managment Methods

    async def create_lease_store_if_not_exists_async(self):
        """
        Create the lease store if it does not exist, do nothing if it does exist.

        :return: `True` if the lease store already exists or was created successfully, `False` if not.
        :rtype: bool
        """
        try:
            await self.host.loop.run_in_executor(
                self.executor,
                functools.partial(
                    self.storage_client.create_container,
                    self.lease_container_name))

        except Exception as err:  # pylint: disable=broad-except
            _logger.error("%r", err)
            raise err

        return True

    async def delete_lease_store_async(self):
        """
        Not used by EventProcessorHost, but a convenient function to have for testing.

        :return: `True` if the lease store was deleted successfully, `False` if not.
        :rtype: bool
        """
        return "Not Supported in Python"

    async def get_lease_async(self, partition_id):
        """
        Return the lease info for the specified partition.
        Can return null if no lease has been created in the store for the specified partition.

        :param partition_id: The partition ID.
        :type partition_id: str
        :return: lease info for the partition, or `None`.
        :rtype: ~azure.eventprocessorhost.lease.Lease
        """
        try:
            blob = await self.host.loop.run_in_executor(
                self.executor,
                functools.partial(
                    self.storage_client.get_blob_to_text,
                    self.lease_container_name, partition_id))
            lease = AzureBlobLease()
            lease.with_blob(blob)
            async def state():
                """
                Allow lease to curry storage_client to get state
                """
                try:
                    loop = asyncio.get_event_loop()
                    res = await loop.run_in_executor(
                        self.executor,
                        functools.partial(
                            self.storage_client.get_blob_properties,
                            self.lease_container_name,
                            partition_id))
                    return res.properties.lease.state
                except Exception as err:  # pylint: disable=broad-except
                    _logger.error("Failed to get lease state %r %r", err, partition_id)

            lease.state = state
            return lease
        except Exception as err:  # pylint: disable=broad-except
            _logger.error("Failed to get lease %r %r", err, partition_id)

    async def get_all_leases(self):
        """
        Return the lease info for all partitions.
        A typical implementation could just call get_lease_async() on all partitions.

        :return: A list of lease info.
        :rtype: list[~azure.eventprocessorhost.lease.Lease]
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

        :param partition_id: The ID of a given parition.
        :type partition_id: str
        :return: the existing or newly-created lease info for the partition.
        :rtype: ~azure.eventprocessorhost.lease.Lease
        """
        return_lease = None
        try:
            return_lease = AzureBlobLease()
            return_lease.partition_id = partition_id
            serializable_lease = return_lease.serializable()
            json_lease = json.dumps(serializable_lease)
            _logger.info("Creating Lease %r %r %r",
                         self.lease_container_name,
                         partition_id,
                         json.dumps({k:v for k, v in serializable_lease.items() if k != 'event_processor_context'}))
            await self.host.loop.run_in_executor(
                self.executor,
                functools.partial(
                    self.storage_client.create_blob_from_text,
                    self.lease_container_name,
                    partition_id,
                    json_lease))
        except Exception:  # pylint: disable=broad-except
            try:
                return_lease = await self.get_lease_async(partition_id)
            except Exception as err:  # pylint: disable=broad-except
                _logger.error("Failed to create lease %r", err)
                raise err
        return return_lease

    async def delete_lease_async(self, lease):
        """
        Delete the lease info for the given partition from the store.
        If there is no stored lease for the given partition, that is treated as success.

        :param lease: The stored lease to be deleted.
        :type lease: ~azure.eventprocessorhost.lease.Lease
        """
        await self.host.loop.run_in_executor(
            self.executor,
            functools.partial(
                self.storage_client.delete_blob,
                self.lease_container_name,
                lease.partition_id,
                lease_id=lease.token))

    async def acquire_lease_async(self, lease):
        """
        Acquire the lease on the desired partition for this EventProcessorHost.
        Note that it is legal to acquire a lease that is already owned by another host.
        Lease-stealing is how partitions are redistributed when additional hosts are started.

        :param lease: The stored lease to be acquired.
        :type lease: ~azure.eventprocessorhost.lease.Lease
        :return: `True` if the lease was acquired successfully, `False` if not.
        :rtype: bool
        """
        retval = True
        new_lease_id = str(uuid.uuid4())
        partition_id = lease.partition_id
        try:
            if asyncio.iscoroutinefunction(lease.state):
                state = await lease.state()
            else:
                state = lease.state()
            if state == "leased":
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
                    _logger.info("ChangingLease %r %r", self.host.guid, lease.partition_id)
                    await self.host.loop.run_in_executor(
                        self.executor,
                        functools.partial(
                            self.storage_client.change_blob_lease,
                            self.lease_container_name,
                            partition_id,
                            lease.token,
                            new_lease_id))
                    lease.token = new_lease_id
            else:
                _logger.info("AcquiringLease %r %r", self.host.guid, lease.partition_id)
                lease.token = await self.host.loop.run_in_executor(
                    self.executor,
                    functools.partial(
                        self.storage_client.acquire_blob_lease,
                        self.lease_container_name,
                        partition_id,
                        self.lease_duration,
                        new_lease_id))
            lease.owner = self.host.host_name
            lease.increment_epoch()
            # check if this solves the issue
            retval = await self.update_lease_async(lease)
        except Exception as err:  # pylint: disable=broad-except
            _logger.error("Failed to acquire lease %r %r %r", err, partition_id, lease.token)
            return False

        return retval

    async def renew_lease_async(self, lease):
        """
        Renew a lease currently held by this host.
        If the lease has been stolen, or expired, or released, it is not possible to renew it.
        You will have to call getLease() and then acquireLease() again.

        :param lease: The stored lease to be renewed.
        :type lease: ~azure.eventprocessorhost.lease.Lease
        :return: `True` if the lease was renewed successfully, `False` if not.
        :rtype: bool
        """
        try:
            await self.host.loop.run_in_executor(
                self.executor,
                functools.partial(
                    self.storage_client.renew_blob_lease,
                    self.lease_container_name,
                    lease.partition_id,
                    lease_id=lease.token,
                    timeout=self.lease_duration))
        except Exception as err:  # pylint: disable=broad-except
            if "LeaseIdMismatchWithLeaseOperation" in str(err):
                _logger.info("LeaseLost on partition %r", lease.partition_id)
            else:
                _logger.error("Failed to renew lease on partition %r with token %r %r",
                              lease.partition_id, lease.token, err)
            return False
        return True

    async def release_lease_async(self, lease):
        """
        Give up a lease currently held by this host. If the lease has been stolen, or expired,
        releasing it is unnecessary, and will fail if attempted.

        :param lease: The stored lease to be released.
        :type lease: ~azure.eventprocessorhost.lease.Lease
        :return: `True` if the lease was released successfully, `False` if not.
        :rtype: bool
        """
        lease_id = None
        try:
            _logger.info("Releasing lease %r %r", self.host.guid, lease.partition_id)
            lease_id = lease.token
            released_copy = AzureBlobLease()
            released_copy.with_lease(lease)
            released_copy.token = None
            released_copy.owner = None
            released_copy.state = None
            await self.host.loop.run_in_executor(
                self.executor,
                functools.partial(
                    self.storage_client.create_blob_from_text,
                    self.lease_container_name,
                    lease.partition_id,
                    json.dumps(released_copy.serializable()),
                    lease_id=lease_id))
            await self.host.loop.run_in_executor(
                self.executor,
                functools.partial(
                    self.storage_client.release_blob_lease,
                    self.lease_container_name,
                    lease.partition_id,
                    lease_id))
        except Exception as err:  # pylint: disable=broad-except
            _logger.error("Failed to release lease %r %r %r",
                          err, lease.partition_id, lease_id)
            return False
        return True

    async def update_lease_async(self, lease):
        """
        Update the store with the information in the provided lease. It is necessary to currently
        hold a lease in order to update it. If the lease has been stolen, or expired, or released,
        it cannot be updated. Updating should renew the lease before performing the update to
        avoid lease expiration during the process.

        :param lease: The stored lease to be updated.
        :type lease: ~azure.eventprocessorhost.lease.Lease
        :return: `True` if the updated was performed successfully, `False` if not.
        :rtype: bool
        """
        if lease is None:
            return False

        if not lease.token:
            return False

        _logger.debug("Updating lease %r %r", self.host.guid, lease.partition_id)

        # First, renew the lease to make sure the update will go through.
        if await self.renew_lease_async(lease):
            try:
                await self.host.loop.run_in_executor(
                    self.executor,
                    functools.partial(
                        self.storage_client.create_blob_from_text,
                        self.lease_container_name,
                        lease.partition_id,
                        json.dumps(lease.serializable()),
                        lease_id=lease.token))

            except Exception as err:  # pylint: disable=broad-except
                _logger.error("Failed to update lease %r %r %r",
                              self.host.guid, lease.partition_id, err)
                raise err
        else:
            return False
        return True
