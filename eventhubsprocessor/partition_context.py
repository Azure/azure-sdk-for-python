"""
Author: Aaron (Ari) Bornstien
"""

class PartitionContext:
    """
    Encapsulates information related to an Event Hubs partition used by AbstractEventProcessor
    """
    def __init__(self, host, partition_id, eh_path, consumer_group_name):
        self.host = host
        self.partition_id = partition_id
        self.eh_path = eh_path
        self.consumer_group_name = consumer_group_name
        self.offset = "-1" # Hardcoded for now get from partition reciever
        self.sequence_number = 0
        # self.ThisLock = #new object(self);

    def set_offset_and_sequence_number(self, event_data):
        """
        Updates offset based on event
        """
        # Migrate from C# to python
        # if (eventData == null):
        #     #throw new ArgumentNullException(nameof(eventData));
        # lock (this.ThisLock):
        #     self.Offset = eventData.SystemProperties.Offset
        #     self.SequenceNumber = eventData.SystemProperties.SequenceNumber
        return "TBI"
    
    async def get_initial_offset_async(self): # throws InterruptedException, ExecutionException
        """
        Returns the initial offset for processing the partition.
        """
        return "-1" #TBI with check pointing for now hard code to begining of partition

    async def checkpoint_async(self):
        """
        Writes the current offset and sequenceNumber to the checkpoint store
        via the checkpoint manager.
        """
        return "TBI"

    async def checkpoint_async_event_data(self, event_data):
        """
        Stores the offset and sequenceNumber from the provided received EventData instance,
        then writes those values to the checkpoint store via the checkpoint manager.
        (Params) eventData :A received EventData with valid offset and sequenceNumber
        Throws ArgumentNullException If suplied eventData is null
        Throws ArgumentOutOfRangeException If the sequenceNumber is less than the
        last checkpointed value
        """
        return "TBI"

    def to_string(self):
        """
        Returns the parition context in the following format:
        "PartitionContext({EventHubPath}{ConsumerGroupName}{PartitionId}{SequenceNumber})"
        """
        return "TBI"

    async def persist_checkpoint_async(self, checkpoint):
        """
        Persists the checkpoint
        """
        pass
