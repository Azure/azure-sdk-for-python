 class Checkpoint:

    def __init__(self):
        pass
        
    # Creates a new Checkpoint for a particular partition ID.
    # (Params) partitionId:The partition ID for the checkpoint
    def withDefaults(self, partitionId):
        self.custom(partitionId, PartitionReceiver.StartOfStream, 0)
    
    # Creates a new Checkpoint for a particular partition ID, with the offset and sequence number.
    # (Params)partitionId:The partition ID for the checkpoint, offset:The offset for the last processed sequenceNumber:The sequence number of the last processed 
    def custom(self, partitionId,  offset, sequenceNumber):
        self.PartitionId = partitionId
        self.Offset = offset
        self.SequenceNumber = sequenceNumber

    # Creates a new Checkpoint from an existing checkpoint.
    # (Params) source:The existing checkpoint to copy
    def withSource(self, checkpoint):
        self.PartitionId = checkpoint.PartitionId
        self.Offset = checkpoint.Offset
        self.SequenceNumber = checkpoint.SequenceNumber

    # Gets or sets the offset of the last processed
    def getOffset(self):
        return self.Offset

    def setOffest(self, offset):
        self.Offset = offset
        
    # Gets or sets the sequence number of the last processed 
    def getSequenceNumber(self):
        return self.SequenceNumber

    def setSequenceNumber(self, sequenceNumber):
        self.SequenceNumber = sequenceNumber
    
    # Gets the partition ID for the corresponding checkpoint.
    def getPartitionId(self):
        return self.PartitionId
