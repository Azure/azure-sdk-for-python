class Lease:
    def __init__(self):
        pass

    def withPartitionId(self, partitionId):
        self.PartitionId = partitionId
        self.Owner = ""
        self.Token = ""

    def withSource(self, lease):
        self.PartitionId = lease.PartitionId
        self.Epoch = lease.Epoch
        self.Owner = lease.Owner
        self.Token = lease.Token

    # Gets or sets the current value for the offset in the stream.
    def setOffset(self, offset):
        self.Offset = offset

    def getOffest(self):
        return self.Offset
    
    # Gets or sets the last checkpointed sequence number in the stream.
    def setSequenceNumber(self, sequenceNumber):
        self.SequenceNumber = sequenceNumber

    def getSequenceNumber(self):
        return self.SequenceNumber

    # Gets the ID of the partition to which this lease belongs.
    def setPartitionId(self, partitionId):
        self.PartitionId = partitionId

    def getPartitionId(self):
        return self.PartitionId

    # Gets or sets the host owner for the partition.
    def setOwner(self, owner):
        self.Owner = owner

    def getOwner(self):
        return self.Owner

    # Gets or sets the lease token that manages concurrency between hosts. You can use this token to guarantee single access to any resource needed by the <see cref="IEventProcessor"/> object.
    def setToken(self, token):
        self.Token = token

    def getToken(self)
        return self.Token

    # Gets or sets the epoch year of the lease, which is a value you can use to determine the most recent owner of a partition between competing nodes.
    def setEpoch(self, epoch):
        self.Epoch = epoch

    def getEpoch(self):
        return self.Epoch

    # Determines whether the lease is expired. By default lease never expires. Deriving class implements the lease expiry logic
    def IsExpired():
        return False

    def incrementEpoch(self):
        self.Epoch += 1
        return self.Epoch
    
}