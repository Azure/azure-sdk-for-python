"""
Author: Aaron (Ari) Bornstien
"""
class Checkpoint:
    """
    Contains checkpoint metadata
    """
    def __init__(self, partition_id, offset="-1", sequence_number="0"):
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
