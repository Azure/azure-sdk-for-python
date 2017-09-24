class EPHOptions:

    def __init__(self):
        self.MaxBatchSize = 10
        self.PrefetchCount = 300
        self.ReceiveTimeout = TimeSpan.FromMinutes(1)
        self.InitialOffsetProvider = partitionId => PartitionReceiver.StartOfStream