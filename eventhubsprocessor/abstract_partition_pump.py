from abc import ABC, abstractmethod

class PartitionPump(ABC):
    
    def __init__(self, host, lease):
        super(AbstractEventProcessor, self).__init__()
        self.Host = host
        self.Lease = lease
        self.ProcessingAsyncLock #= new AsyncLock()
        self.PumpStatus = "Uninitialized"
        self.Processor = None
        self.PartitionContext = None


    def OpenAsync():
        pass #TBI

    @abstractmethod
    def OnOpenAsync():
        pass

    def IsClosing():
        pass #TBI

    def CloseAsync(reason):
        pass #TBI

    @abstractmethod
    def OnClosingAsync(reason):
        pass

    def ProcessEventsAsync(events)
        pass #TBI

    def ProcessErrorAsync(error):
        pass #TBI
