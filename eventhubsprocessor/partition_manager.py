class PartitionManager:

    def __init__(self,  host):
        self.host = host
        self.cancellationTokenSource = new CancellationTokenSource(self) # comes from terminated thread 
        self.partitionPumps = {}
        self.partitionIds = None
    }

    # Returns a list of all the event hub partition ids
    def GetPartitionIdsAsync(self):
        pass
    
    # Intializes the partition checkpoint and lease store and then calls run async
    def StartAsync(self):
    
    # Starts the run loop and manages exceptions and cleanup 
    def RunAsync(self):
        pass

    # Intializes the partition checkpoint and lease store ensures that a checkpoint exists for all partions
    def InitializeStoresAsync(self): #throws InterruptedException, ExecutionException, ExceptionWithAction
        pass

    # This is the main execution loop for allocating and manging pumps
    def RunLoopAsync(self, cancellationToken): # throws Exception, ExceptionWithAction
        pass

    # Updates the laease on an exisiting pump
    def CheckAndAddPumpAsync(self, partitionId,  lease):
        pass

    # Create a new pump thread with a given lease
    def CreateNewPumpAsync(self, partitionId, lease):
        pass

    # Stops a single partion pump
    def RemovePumpAsync(self, partitionId, reason):
        pass
    # Stops all partiiton pumps 
    def RemoveAllPumpsAsync(self, reason):
        pass

    # Determines and return which lease to steal
            # If the number of leases is a multiple of the number of hosts, then the desired configuration is
            # that all hosts own the name number of leases, and the difference between the "biggest" owner and
            # any other is 0.
            #
            # If the number of leases is not a multiple of the number of hosts, then the most even configuration
            # possible is for some hosts to have (self, leases/hosts) leases and others to have (self, (self, leases/hosts) + 1).
            # For example, for 16 partitions distributed over five hosts, the distribution would be 4, 3, 3, 3, 3,
            # or any of the possible reorderings.
            #
            # In either case, if the difference between this host and the biggest owner is 2 or more, then the
            # system is not in the most evenly-distributed configuration, so steal one lease from the biggest.
            # If there is a tie for biggest, we pick whichever appears first in the list because
            # it doesn't really matter which "biggest" is trimmed down.
            #
            # Stealing one at a time prevents flapping because it reduces the difference between the biggest and
            # this host by two at a time. If the starting difference is two or greater, then the difference cannot
            # end up below 0. This host may become tied for biggest, but it cannot become larger than the host that
            # it is stealing from.
    def WhichLeaseToSteal(self, stealableLeases, haveLeaseCount):
        pass

    #Returns (self, Dictionary<string, int> owner count)
    def CountLeasesByOwner(self,  leases):
        pass


