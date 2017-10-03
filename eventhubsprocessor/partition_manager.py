"""
Author: Aaron (Ari) Bornstien
"""
import asyncio

class PartitionManager:
    """
    Manages the partition event pump execution
    """
    def __init__(self, host):
        self.host = host
        self.partition_pumps = {}
        self.partition_ids = None
        # self.cancellation_token_source = CancellationTokenSource(self) # comes from terminated thread 

    async def get_partition_ids_async(self):
        """
        Returns a list of all the event hub partition ids
        """
        pass

    async def start_async(self):
        """
        Intializes the partition checkpoint and lease store and then calls run async.
        """
        pass

    async def run_async(self):
        """
        Starts the run loop and manages exceptions and cleanup
        """
        pass

    async def initialize_stores_async(self):
        """
        Intializes the partition checkpoint and lease store ensures that a checkpoint
        exists for all partions
        """
        pass

    async def run_loop_async(self, cancellation_token):
        """
        This is the main execution loop for allocating and manging pumps
        """
        pass

    async def check_and_add_pump_async(self, partition_id, lease):
        """
        Updates the laease on an exisiting pump
        """
        pass

    async def create_new_pump_async(self, partition_id, lease):
        """
        Create a new pump thread with a given lease
        """
        pass

    async def remove_pump_async(self, partition_id, reason):
        """
        Stops a single partion pump
        """
        pass

    async def remove_all_pumps_async(self, reason):
        """
        Stops all partiiton pumps
        """
        pass

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
        """
        pass

    def count_leases_by_owner(self, leases):
        """
        Returns a dictionary of leases by current owner
        """
        pass
