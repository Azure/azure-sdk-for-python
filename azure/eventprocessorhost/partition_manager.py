# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

import logging
import asyncio
from queue import Queue
from collections import Counter

from azure.eventhub import EventHubClientAsync
from azure.eventprocessorhost.eh_partition_pump import EventHubPartitionPump
from azure.eventprocessorhost.cancellation_token import CancellationToken


_logger = logging.getLogger(__name__)


class PartitionManager:
    """
    Manages the partition event pump execution.
    """

    def __init__(self, host):
        self.host = host
        self.partition_pumps = {}
        self.partition_ids = None
        self.run_task = None
        self.cancellation_token = CancellationToken()

    async def get_partition_ids_async(self):
        """
        Returns a list of all the event hub partition IDs.

        :rtype: list[str]
        """
        if not self.partition_ids:
            try:
                eh_client = EventHubClientAsync(
                    self.host.eh_config.client_address,
                    debug=self.host.eph_options.debug_trace,
                    http_proxy=self.host.eph_options.http_proxy)
                try:
                    eh_info = await eh_client.get_eventhub_info_async()
                    self.partition_ids = eh_info['partition_ids']
                except Exception as err:  # pylint: disable=broad-except
                    raise Exception("Failed to get partition ids", repr(err))
            finally:
                await eh_client.stop_async()
        return self.partition_ids

    async def start_async(self):
        """
        Intializes the partition checkpoint and lease store and then calls run async.
        """
        if self.run_task:
            raise Exception("A PartitionManager cannot be started multiple times.")

        partition_count = await self.initialize_stores_async()
        _logger.info("%r PartitionCount: %r", self.host.guid, partition_count)
        self.run_task = asyncio.ensure_future(self.run_async())

    async def stop_async(self):
        """
        Terminiates the partition manger.
        """
        self.cancellation_token.cancel()
        if self.run_task and not self.run_task.done():
            await self.run_task

    async def run_async(self):
        """
        Starts the run loop and manages exceptions and cleanup.
        """
        try:
            await self.run_loop_async()
        except Exception as err:  # pylint: disable=broad-except
            _logger.error("Run loop failed %r", err)

        try:
            _logger.info("Shutting down all pumps %r", self.host.guid)
            await self.remove_all_pumps_async("Shutdown")
        except Exception as err:  # pylint: disable=broad-except
            raise Exception("Failed to remove all pumps {!r}".format(err))

    async def initialize_stores_async(self):
        """
        Intializes the partition checkpoint and lease store ensures that a checkpoint
        exists for all partitions. Note in this case checkpoint and lease stores are
        the same storage manager construct.

        :return: Returns the number of partitions.
        :rtype: int
        """
        await self.host.storage_manager.create_checkpoint_store_if_not_exists_async()
        partition_ids = await self.get_partition_ids_async()
        retry_tasks = []
        for partition_id in partition_ids:
            retry_tasks.append(
                self.retry_async(
                    self.host.storage_manager.create_checkpoint_if_not_exists_async,
                    partition_id=partition_id,
                    retry_message="Failure creating checkpoint for partition, retrying",
                    final_failure_message="Out of retries creating checkpoint blob for partition",
                    max_retries=5,
                    host_id=self.host.host_name))

        await asyncio.gather(*retry_tasks)
        return len(partition_ids)

    def retry(self, func, partition_id, retry_message, final_failure_message, max_retries, host_id):
        """
        Make attempt_renew_lease async call sync.
        """
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.retry_async(func, partition_id, retry_message,
                                                 final_failure_message, max_retries, host_id))

    async def retry_async(self, func, partition_id, retry_message,
                          final_failure_message, max_retries, host_id):
        """
        Throws if it runs out of retries. If it returns, action succeeded.
        """
        created_okay = False
        retry_count = 0
        while not created_okay and retry_count <= max_retries:
            try:
                await func(partition_id)
                created_okay = True
            except Exception as err:  # pylint: disable=broad-except
                _logger.error("%r %r %r %r", retry_message, host_id, partition_id, err)
                retry_count += 1
        if not created_okay:
            raise Exception(host_id, final_failure_message)

    async def run_loop_async(self):
        """
        This is the main execution loop for allocating and manging pumps.
        """
        while not self.cancellation_token.is_cancelled:
            lease_manager = self.host.storage_manager
            # Inspect all leases.
            # Acquire any expired leases.
            # Renew any leases that currently belong to us.
            getting_all_leases = await lease_manager.get_all_leases()
            leases_owned_by_others_q = Queue()
            renew_tasks = [
                self.attempt_renew_lease_async(
                    get_lease_task,
                    owned_by_others_q=leases_owned_by_others_q,
                    lease_manager=lease_manager)
                for get_lease_task in getting_all_leases]
            await asyncio.gather(*renew_tasks)

            # Extract all leasees leases_owned_by_others and our_lease_count from the
            all_leases = {}
            leases_owned_by_others = []
            our_lease_count = 0
            while not leases_owned_by_others_q.empty():
                lease_owned_by_other = leases_owned_by_others_q.get()
                # Check if lease is owned by other and append
                if lease_owned_by_other[0]:
                    leases_owned_by_others.append(lease_owned_by_other[1])
                else:
                    our_lease_count += 1
                all_leases[lease_owned_by_other[1].partition_id] = lease_owned_by_other[1]

            # Grab more leases if available and needed for load balancing
            leases_owned_by_others_count = len(leases_owned_by_others)
            if leases_owned_by_others_count > 0:
                steal_this_lease = self.which_lease_to_steal(
                    leases_owned_by_others, our_lease_count)
                if steal_this_lease:
                    try:
                        _logger.info("Lease to steal %r", steal_this_lease.serializable())
                        if await lease_manager.acquire_lease_async(steal_this_lease):
                            _logger.info("Stole lease sucessfully %r %r",
                                         self.host.guid, steal_this_lease.partition_id)
                        else:
                            _logger.info("Failed to steal lease for partition %r %r",
                                         self.host.guid, steal_this_lease.partition_id)
                    except Exception as err:  # pylint: disable=broad-except
                        _logger.error("Failed to steal lease %r", err)

            for partition_id in all_leases:
                try:
                    updated_lease = all_leases[partition_id]
                    if updated_lease.owner == self.host.host_name:
                        _logger.debug("Attempting to renew lease %r %r",
                                      self.host.guid, partition_id)
                        await self.check_and_add_pump_async(partition_id, updated_lease)
                    else:
                        _logger.debug("Removing pump due to lost lease.")
                        await self.remove_pump_async(partition_id, "LeaseLost")
                except Exception as err:  # pylint: disable=broad-except
                    _logger.error("Failed to update lease %r", err)
            await asyncio.sleep(lease_manager.lease_renew_interval)

    async def check_and_add_pump_async(self, partition_id, lease):
        """
        Updates the lease on an exisiting pump.

        :param partition_id: The partition ID.
        :type partition_id: str
        :param lease: The lease to be used.
        :type lease: ~azure.eventprocessorhost.lease.Lease
        """
        if partition_id in self.partition_pumps:
            # There already is a pump. Make sure the pump is working and replace the lease.
            captured_pump = self.partition_pumps[partition_id]
            if captured_pump.pump_status == "Errored" or captured_pump.is_closing():
                # The existing pump is bad. Remove it.
                await self.remove_pump_async(partition_id, "Shutdown")
            else:
                # Pump is working, should just replace the lease.
                # This is causing a race condition since if the checkpoint is being updated
                # when the lease changes then the pump will error and shut down
                captured_pump.set_lease(lease)
        else:
            _logger.info("Starting pump %r %r", self.host.guid, partition_id)
            await self.create_new_pump_async(partition_id, lease)

    async def create_new_pump_async(self, partition_id, lease):
        """
        Create a new pump thread with a given lease.

        :param partition_id: The partition ID.
        :type partition_id: str
        :param lease: The lease to be used.
        :type lease: ~azure.eventprocessorhost.lease.Lease
        """
        loop = asyncio.get_event_loop()
        partition_pump = EventHubPartitionPump(self.host, lease)
        # Do the put after start, if the start fails then put doesn't happen
        loop.create_task(partition_pump.open_async())
        self.partition_pumps[partition_id] = partition_pump
        _logger.info("Created new partition pump %r %r", self.host.guid, partition_id)

    async def remove_pump_async(self, partition_id, reason):
        """
        Stops a single partiton pump.

        :param partition_id: The partition ID.
        :type partition_id: str
        :param reason: A reason for closing.
        :type reason: str
        """
        if partition_id in self.partition_pumps:
            captured_pump = self.partition_pumps[partition_id]
            if not captured_pump.is_closing():
                await captured_pump.close_async(reason)
            # else, pump is already closing/closed, don't need to try to shut it down again
            del self.partition_pumps[partition_id]  # remove pump
            _logger.debug("Removed pump %r %r", self.host.guid, partition_id)
            _logger.debug("%r pumps still running", len(self.partition_pumps))
        else:
            # PartitionManager main loop tries to remove pump for every partition that the
            # host does not own, just to be sure. Not finding a pump for a partition is normal
            # and expected most of the time.
            _logger.debug("No pump found to remove for this partition %r %r",
                          self.host.guid, partition_id)

    async def remove_all_pumps_async(self, reason):
        """
        Stops all partition pumps
        (Note this might be wrong and need to await all tasks before returning done).

        :param reason: A reason for closing.
        :type reason: str
        :rtype: bool
        """
        pump_tasks = [self.remove_pump_async(p_id, reason) for p_id in self.partition_pumps]
        await asyncio.gather(*pump_tasks)
        return True

    def which_lease_to_steal(self, stealable_leases, have_lease_count):
        """
        Determines and return which lease to steal
        If the number of leases is a multiple of the number of hosts, then the desired
        configuration is that all hosts own the name number of leases, and the
        difference between the "biggest" owner and any other is 0.

        If the number of leases is not a multiple of the number of hosts, then the most
        even configurationpossible is for some hosts to have (self, leases/hosts) leases
        and others to have (self, (self, leases/hosts) + 1). For example, for 16 partitions
        distributed over five hosts, the distribution would be 4, 3, 3, 3, 3, or any of the
        possible reorderings.

        In either case, if the difference between this host and the biggest owner is 2 or more,
        then thesystem is not in the most evenly-distributed configuration, so steal one lease
        from the biggest. If there is a tie for biggest, we pick whichever appears first in the
        list because it doesn't really matter which "biggest" is trimmed down.

        Stealing one at a time prevents flapping because it reduces the difference between the
        biggest and this host by two at a time. If the starting difference is two or greater,
        then the difference cannot end up below 0. This host may become tied for biggest, but it
        cannot become larger than the host that it is stealing from.

        :param stealable_leases: List of leases to determine which can be stolen.
        :type stealable_leases: list[~azure.eventprocessorhost.lease.Lease]
        :param have_lease_count: Lease count.
        :type have_lease_count: int
        :rtype: ~azure.eventprocessorhost.lease.Lease
        """
        counts_by_owner = self.count_leases_by_owner(stealable_leases)
        biggest_owner = (sorted(counts_by_owner.items(), key=lambda kv: kv[1])).pop()
        steal_this_lease = None
        if (biggest_owner[1] - have_lease_count) >= 2:
            steal_this_lease = [l for l in stealable_leases if l.owner == biggest_owner[0]][0]

        return steal_this_lease

    def count_leases_by_owner(self, leases):  # pylint: disable=no-self-use
        """
        Returns a dictionary of leases by current owner.
        """
        owners = [l.owner for l in leases]
        return dict(Counter(owners))

    def attempt_renew_lease(self, lease_task, owned_by_others_q, lease_manager):
        """
        Make attempt_renew_lease async call sync.
        """
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.attempt_renew_lease_async(lease_task, owned_by_others_q, lease_manager))

    async def attempt_renew_lease_async(self, lease_task, owned_by_others_q, lease_manager):
        """
        Attempts to renew a potential lease if possible and
        marks in the queue as none adds to adds to the queue.
        """
        try:
            possible_lease = await lease_task
            if await possible_lease.is_expired():
                _logger.info("Trying to aquire lease %r %r",
                             self.host.guid, possible_lease.partition_id)
                if await lease_manager.acquire_lease_async(possible_lease):
                    owned_by_others_q.put((False, possible_lease))
                else:
                    owned_by_others_q.put((True, possible_lease))

            elif possible_lease.owner == self.host.host_name:
                try:
                    _logger.debug("Trying to renew lease %r %r",
                                  self.host.guid, possible_lease.partition_id)
                    if await lease_manager.renew_lease_async(possible_lease):
                        owned_by_others_q.put((False, possible_lease))
                    else:
                        owned_by_others_q.put((True, possible_lease))
                except Exception as err:  # pylint: disable=broad-except
                    # Update to 'Lease Lost' exception.
                    _logger.error("Lease lost exception %r %r %r",
                                  err, self.host.guid, possible_lease.partition_id)
                    owned_by_others_q.put((True, possible_lease))
            else:
                owned_by_others_q.put((True, possible_lease))

        except Exception as err:  # pylint: disable=broad-except
            _logger.error(
                "Failure during getting/acquiring/renewing lease, skipping %r", err)
