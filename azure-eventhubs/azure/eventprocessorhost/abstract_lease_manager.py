# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

"""
Author: Aaron (Ari) Bornstien
"""
from abc import ABC, abstractmethod

class AbstractLeaseManager(ABC):
    """
    If you wish to have EventProcessorHost store leases somewhere other than Azure Storage,
    you can write your own lease manager using this abstract class. The Azure Storage managers
    use the same storage for both lease and checkpoints, so both interfaces are implemented by
    the same class.You are free to do the same thing if you have  a unified store for both
    types of data.
    """

    def __init__(self, lease_renew_interval, lease_duration):
        self.lease_renew_interval = lease_renew_interval
        self.lease_duration = lease_duration

    @abstractmethod
    async def create_lease_store_if_not_exists_async(self):
        """
        Create the lease store if it does not exist, do nothing if it does exist.

        :return: `True` if the lease store already exists or was created successfully, `False` if not.
        :rtype: bool
        """

    @abstractmethod
    async def delete_lease_store_async(self):
        """
        Not used by EventProcessorHost, but a convenient function to have for testing.

        :return: `True` if the lease store was deleted successfully, `False` if not.
        :rtype: bool
        """

    async def get_lease_async(self, partition_id):
        """
        Return the lease info for the specified partition.
        Can return null if no lease has been created in the store for the specified partition.

        :param partition_id: The ID of a given partition.
        :type parition_id: str
        :return: Lease info for the partition, or `None`.
        :rtype:
        """

    @abstractmethod
    def get_all_leases(self):
        """
        Return the lease info for all partitions.
        A typical implementation could just call get_lease_async() on all partitions.

        :return: A list of lease info.
        :rtype:
        """

    @abstractmethod
    async def create_lease_if_not_exists_async(self, partition_id):
        """
        Create in the store the lease info for the given partition, if it does not exist.
        Do nothing if it does exist in the store already.

        :param partition_id: The ID of a given partition.
        :type parition_id: str
        :return: The existing or newly-created lease info for the partition.
        """

    @abstractmethod
    async def delete_lease_async(self, lease):
        """
        Delete the lease info for the given partition from the store.
        If there is no stored lease for the given partition, that is treated as success.

        :param lease: The lease to be deleted.
        :type lease: ~azure.eventprocessorhost.lease.Lease
        """

    @abstractmethod
    async def acquire_lease_async(self, lease):
        """
        Acquire the lease on the desired partition for this EventProcessorHost.
        Note that it is legal to acquire a lease that is already owned by another host.
        Lease-stealing is how partitions are redistributed when additional hosts are started.

        :param lease: The lease to be acquired.
        :type lease: ~azure.eventprocessorhost.lease.Lease
        :return: `True` if the lease was acquired successfully, `False` if not.
        :rtype: bool
        """

    @abstractmethod
    async def renew_lease_async(self, lease):
        """
        Renew a lease currently held by this host.
        If the lease has been stolen, or expired, or released, it is not possible to renew it.
        You will have to call get_lease_async() and then acquire_lease_async() again.

        :param lease: The lease to be renewed.
        :type lease: ~azure.eventprocessorhost.lease.Lease
        :return: `True` if the lease was renewed successfully, `False` if not.
        :rtype: bool
        """

    @abstractmethod
    async def release_lease_async(self, lease):
        """
        Give up a lease currently held by this host. If the lease has been stolen, or expired,
        releasing it is unnecessary, and will fail if attempted.

        :param lease: The lease to be released.
        :type lease: ~azure.eventprocessorhost.lease.Lease
        :return: `True` if the lease was released successfully, `False` if not.
        :rtype: bool
        """

    @abstractmethod
    async def update_lease_async(self, lease):
        """
        Update the store with the information in the provided lease. It is necessary to currently
        hold a lease in order to update it. If the lease has been stolen, or expired, or released,
        it cannot be updated. Updating should renew the lease before performing the update to
        avoid lease expiration during the process.

        :param lease: The lease to be updated.
        :type lease: ~azure.eventprocessorhost.lease.Lease
        :return: `True` if the updated was performed successfully, `False` if not.
        :rtype: bool
        """
