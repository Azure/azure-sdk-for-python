#The MIT License (MIT)
#Copyright (c) 2014 Microsoft Corporation

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

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


        




