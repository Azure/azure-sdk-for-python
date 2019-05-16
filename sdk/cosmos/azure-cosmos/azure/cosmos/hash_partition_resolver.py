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

"""Hash partition resolver implementation in the Azure Cosmos database service.
"""

import azure.cosmos.murmur_hash as murmur_hash
import azure.cosmos.consistent_hash_ring as consistent_hash_ring

class HashPartitionResolver(object):
    """HashPartitionResolver implements partitioning based on the value of a hash function, allowing you to evenly
    distribute requests and data across a number of partitions.
    """
    def __init__(self, partition_key_extractor, collection_links, default_number_of_virtual_nodes_per_collection = 128, hash_generator = None):
        """
        :param lambda partition_key_extractor:
            Returning the partition key from the document passed.
        :param list collection_links:
            The links of collections participating in partitioning.
        :param int default_number_of_virtual_nodes_per_collection:
            Number of virtual nodes per collection.
        :param HashGenerator hash_generator:
            The hash generator to be used for hashing algorithm.
        """
        if partition_key_extractor is None:
            raise ValueError("partition_key_extractor is None.")
        if collection_links is None:
            raise ValueError("collection_links is None.")
        if default_number_of_virtual_nodes_per_collection <= 0:
            raise ValueError("The number of virtual nodes per collection must greater than 0.")
        
        self.partition_key_extractor = partition_key_extractor
        self.collection_links = collection_links

        if hash_generator is None:
            hash_generator = murmur_hash._MurmurHash()

        self.consistent_hash_ring = consistent_hash_ring._ConsistentHashRing(self.collection_links, default_number_of_virtual_nodes_per_collection, hash_generator)

    def ResolveForCreate(self, document):
        """Resolves the collection for creating the document based on the partition key.
        
        :param dict document:
            The document to be created.

        :return:
            Collection Self link or Name based link which should handle the Create operation.
        :rtype:
            str
        """
        if document is None:
            raise ValueError("document is None.")

        partition_key = self.partition_key_extractor(document)
        return self.consistent_hash_ring.GetCollectionNode(partition_key)

    def ResolveForRead(self, partition_key):
        """Resolves the collection for reading/querying the documents based on the partition key.

        :param dict document:
            The document to be read/queried.

        :return:
            Collection Self link(s) or Name based link(s) which should handle the Read operation.
        :rtype:
            list
        """
        if partition_key is None:
            return self.collection_links
        else:
            return [self.consistent_hash_ring.GetCollectionNode(partition_key)]
