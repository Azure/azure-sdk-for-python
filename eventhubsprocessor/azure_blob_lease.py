from lease import Lease
class AzureBlobLease(Lease):

    def __init__(self):
        pass

    def withBlob(self, partitionId, blob):
        Lease.__init__().withPartitionId(partitionId)
        self.Blob = blob

    def withSource(self, azure_blob_lease):
        Lease.__init__().withSource(azure_blob_lease)
        self.Offset = azure_blob_lease.Offset
        self.SequenceNumber = azure_blob_lease.SequenceNumber
        self.Blob = azure_blob_lease.Blob
    
    def withSourceBlob(self, azure_blob_lease, blob):
        Lease.__init__().withSource(azure_blob_lease)
		self.Offset = azure_blob_lease.Offset
		self.SequenceNumber = azure_blob_lease.SequenceNumber
		self.Blob = blob
		
	# do not serialize
    def getBlob(self):
        returnself.Blob

    # Check and return azure blob lease state using storage api
    def IsExpired():
        