# Encapsulates information related to an Event Hubs partition used by <see cref="IEventProcessor">.
class PartitionContext:
    def __init__(self, host, partitionId, eventHubPath, consumerGroupName):
        this.host = host
        this.PartitionId = partitionId
        this.EventHubPath = eventHubPat
        this.ConsumerGroupName = consumerGroupName
        this.ThisLock = #new object(self);
        this.Offset = PartitionReceiver.StartOfStream
        this.SequenceNumber = 0   

    # Gets the name of the consumer group.
    def getConsumerGroupName(self):
        return self.consumerGroupName

    # Gets the path of the event hub.
    def getEventHubPath(self):
        return self.EventHubPath(self)

    # Gets the partition ID for the context.
    def getPartitionId(self):
        return self.PartitionId 

    # Gets the host owner for the partition.
    def getOwner(self):
        return self.Lease.Owner
    
    def getOffset(self):
        return self.Offest

    def getSequenceNumber(self):
        return self.SequenceNumber
    
    # Unlike other properties which are immutable after creation, the lease is updated dynamically and needs a setter.
    def getLease(self):
        return self.Lease
    def setLease(self, lease):
        self.Lease = lease

    def getThisLock(self): 
        return self.ThisLock

    def SetOffsetAndSequenceNumber( eventData):
        # Migrate from C# to python
        # if (eventData == null):
        #     #throw new ArgumentNullException(nameof(eventData));
        # lock (this.ThisLock):
        #     self.Offset = eventData.SystemProperties.Offset
        #     self.SequenceNumber = eventData.SystemProperties.SequenceNumber
        pass
        
    def GetInitialOffsetAsync(self): # throws InterruptedException, ExecutionException
        pass

    # Writes the current offset and sequenceNumber to the checkpoint store via the checkpoint manager.
    def CheckpointAsync(self):
        pass

    # Stores the offset and sequenceNumber from the provided received EventData instance, then writes those values to the checkpoint store via the checkpoint manager.
    # (Params) eventData :A received EventData with valid offset and sequenceNumber
    # Throws ArgumentNullException If suplied eventData is null
    # Throws ArgumentOutOfRangeException If the sequenceNumber is less than the last checkpointed value
    def CheckpointAsyncEventData(EventData eventData):
        pass

    # Provides the parition context in the following format:"PartitionContext({EventHubPath}{ConsumerGroupName}{PartitionId}{SequenceNumber})"
    def ToString(self):
        pass 

    def PersistCheckpointAsync(checkpoint):
        pass
