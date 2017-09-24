from partition_pump.py import PartitionPump

class EventHubPartitionPump(PartitionPump):


    def __init__(self, host, lease):
        PartitionPump.__init__(host, lease)
        self.eventHubClient = None
        self.PartitionReceiver = None
        self.PartitionReceiveHandler = None

    def OnOpenAsync(self):
        #tbi
        pass
    
    # throws EventHubsException, IOException, InterruptedException, ExecutionException
    def OpenClientsAsync():
        pass

    #swallows all exceptions
    def CleanUpClientsAsync():
        pass 
   
    def OnClosingAsync(reason):
        pass
   
    class PartitionReceiveHandler():
    
        def __init__(self, eventHubPartitionPump):
            self.eventHubPartitionPump = eventHubPartitionPump
            self.MaxBatchSize = eventHubPartitionPump.Host.EventProcessorOptions.MaxBatchSize

        def getMaxBatchSize(self):
            return self.MaxBatchSize

        def ProcessEventsAsync(events):
            #tbi
            pass

        def ProcessErrorAsync(error):
            #tbi
            pass
