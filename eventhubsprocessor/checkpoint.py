"""
Author: Aaron (Ari) Bornstien
"""
class Checkpoint:
    """
    Contains checkpoint metadata
    """
    def __init__(self):
        self.partition_id = None
        self.offset = None
        self.sequence_number = None

    def with_defaults(self, partition_id):
        """
        Creates a new Checkpoint for a particular partition id.
        """
        # self.custom(partition_id, PartitionReceiver.StartOfStream, 0)

    def custom(self, partition_id, offset, sequence_number):
        """
        Creates a new Checkpoint for a particular partition ID, with the offset and sequence number.
        """
        self.partition_id = partition_id
        self.offset = offset
        self.sequence_number = sequence_number

    def from_source(self, checkpoint):
        """
        Creates a new Checkpoint from an existing checkpoint.
        """
        self.partition_id = checkpoint.partition_id
        self.offset = checkpoint.offset
        self.sequence_number = checkpoint.sequence_number
