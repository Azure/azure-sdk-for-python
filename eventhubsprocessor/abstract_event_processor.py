# Abstract that must be extended by event processor classes.
from abc import ABC, abstractmethod
 
class AbstractEventProcessor(ABC):
 
    def __init__(self):
        super(AbstractEventProcessor, self).__init__()

    #Called by processor host to initialize the event processor.
    @abstractmethod
    def openAsync(context):
        pass

    # Called by processor host to indicate that the event processor is being stopped.
    # (Params) Context:Information about the partition
    @abstractmethod
    def closeAsync(context, reason):
        pass

    # Called by the processor host when a batch of events has arrived. This is where the real work of the event processor is done.</para>
    # (Params) Context: Information about the partition, Messages: The events to be processed.
    @abstractmethod
    def processEventsAsync(context, messages):
        pass

    # Called when the underlying client experiences an error while receiving. 
    # EventProcessorHost will take care of recovering from the error and continuing to pump messages, so no action is required from
    # (Params) Context: Information about the partition, Error: The error that occured.
    @abstractmethod
    def processErrorAsync(PartitionContext context, Exception error):
        pass