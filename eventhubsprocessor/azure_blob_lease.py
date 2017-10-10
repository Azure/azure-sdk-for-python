"""
Author: Aaron (Ari) Bornstien
"""
from eventhubsprocessor.lease import Lease
class AzureBlobLease(Lease):
    """
    Azure Blob Lease
    """

    def __init__(self):
        """
        Init Azure Blob Lease
        """
        super()
        Lease.__init__()
        self.blob = None
        self.offset = None

    def with_blob(self, partition_id, blob):
        """
        Init Azure Blob Lease with existing blob
        """
        self.with_partition_id(partition_id)
        self.blob = blob

    def with_source(self, azure_blob_lease):
        """
        Init Azure Blob Lease from existing
        """
        super(self, azure_blob_lease)
        self.offset = azure_blob_lease.offset
        self.sequence_number = azure_blob_lease.sequence_number
        self.blob = azure_blob_lease.blob
    
    def with_source_blob(self, azure_blob_lease, blob):
        """
        Init Azure Blob Lease from existing source with new blob
        """
        self.with_source(azure_blob_lease)
        self.offset = azure_blob_lease.offset
        self.sequence_number = azure_blob_lease.sequence_number
        self.blob = blob

    def is_expired(self):
        """
        Check and return azure blob lease state using storage api
        """
        pass
    