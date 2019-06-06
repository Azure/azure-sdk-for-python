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

import unittest
import pytest
import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
from azure.cosmos.routing.routing_map_provider import _PartitionKeyRangeCache
from azure.cosmos.routing import routing_range as routing_range
import test_config

pytestmark = pytest.mark.cosmosEmulator

#IMPORTANT NOTES:
  
#      Most test cases in this file create collections in your Azure Cosmos account.
#      Collections are billing entities.  By running these test cases, you may incur monetary costs on your account.
  
#      To Run the test, replace the two member fields (masterKey and host) with values 
#   associated with your Azure Cosmos account.

@pytest.mark.usefixtures("teardown")
class RoutingMapEndToEndTests(unittest.TestCase):
    """Routing Map Functionalities end to end Tests.
    """

    host = test_config._test_config.host
    masterKey = test_config._test_config.masterKey
    connectionPolicy = test_config._test_config.connectionPolicy

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")
        
        cls.client = cosmos_client.CosmosClient(cls.host, {'masterKey': cls.masterKey}, cls.connectionPolicy)
        cls.collection_link = test_config._test_config.create_multi_partition_collection_with_custom_pk_if_not_exist(cls.client)['_self']

    def test_read_partition_key_ranges(self):
        partition_key_ranges = list(self.client._ReadPartitionKeyRanges(self.collection_link))
        #"the number of expected partition ranges returned from the emulator is 5."
        self.assertEqual(5, len(partition_key_ranges))
        
    def test_routing_map_provider(self):
        partition_key_ranges = list(self.client._ReadPartitionKeyRanges(self.collection_link))

        routing_mp = _PartitionKeyRangeCache(self.client)
        overlapping_partition_key_ranges = routing_mp.get_overlapping_ranges(self.collection_link, routing_range._Range("", "FF", True, False))
        self.assertEqual(len(overlapping_partition_key_ranges), len(partition_key_ranges))
        self.assertEqual(overlapping_partition_key_ranges, partition_key_ranges)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()