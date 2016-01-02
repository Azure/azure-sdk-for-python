
"""Test Partition Resolver.
"""

class TestPartitionResolver(object):
    """This is a test PartitionResolver used for resolving the collection(s) based on the partitionKey.
    """

    def __init__(self, collection_links):
        """Initializes the TestPartitionResolver with the list of collections participating in partitioning

        :Parameters:
            - `collection_links`: list, Self Links or ID based Links for the collections participating in partitioning
        """
        self.collection_links = collection_links
    
    def ResolveForCreate(self, document):
        """Resolves the collection for creating the document based on the partition key

        :Parameters:
            - `document`: dict, document resource

        :Returns:
            str, collection Self link or Name based link which should handle the Create operation
        """
        # For this TestPartitionResolver, Id property of the document is the partition key
        partition_key = document['id']
        return self._GetDocumentCollection(self._GetHashCode(partition_key))

    def ResolveForRead(self, partition_key):
        """Resolves the collection for reading/querying the document based on the partition key

        :Parameters:
            - `partition_key`: str, partition key

        :Returns:
            str, collection Self link(s) or Name based link(s) which should handle the Read operation
        """
        # For Read operations, partitionKey can be None in which case we return all collection links
        if partition_key is None:
            return self.collection_links
        else:
            return [self._GetDocumentCollection(self._GetHashCode(partition_key))]

    # Calculates the hashCode from the partition key 
    def _GetHashCode(self, partition_key):
        return int(partition_key)

    # Gets the Document Collection from the hash code 
    def _GetDocumentCollection(self, hashCode):
        return self.collection_links[abs(hashCode) % len(self.collection_links)]


        




