"""
Author: Aaron (Ari) Bornstien
"""
class EventProcessorHost:
    """
    Represents a host for processing Event Hubs event data at scale.
    """
    def __init__(self, event_processor, eh_connection_string, consumer_group_name, eh_options=None):
        self.event_processor = event_processor
        self.eh_connection_string = eh_connection_string
        self.consumer_group_name = consumer_group_name
        self.eh_options = eh_options or EPHOptions()

class EPHOptions:
    """
    Class that contains default and overidable EPH option
    """
    def __init__(self):
        self.max_batch_size = 10
        self.prefetch_count = 300
        # self.ReceiveTimeout = TimeSpan.FromMinutes(1)
        # self.InitialOffsetProvider = partitionId => PartitionReceiver.StartOfStream
        