"""
Author: Aaron (Ari) Bornstien
"""
import uuid
from eventhubsprocessor.partition_manager import PartitionManager
class EventProcessorHost:
    """
    Represents a host for processing Event Hubs event data at scale.
    """
    def __init__(self, event_processor, eh_connection_string, consumer_group_name,
                 lease_manager=None, eh_options=None):
        self.event_processor = event_processor
        self.eh_connection_string = eh_connection_string
        self.consumer_group_name = consumer_group_name
        self.lease_manager = lease_manager
        self.guid = str(uuid.uuid4())
        self.host_name = "default"
        self.eh_options = eh_options or EPHOptions()
        self.partition_manager = PartitionManager(self)


class EPHOptions:
    """
    Class that contains default and overidable EPH option
    """
    def __init__(self):
        self.max_batch_size = 10
        self.prefetch_count = 300
        self.receive_timeout = 60
        # self.InitialOffsetProvider = partitionId => PartitionReceiver.StartOfStream
        