# The MIT License (MIT)
# Copyright (c) 2022 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import unittest
import pytest
from azure.cosmos import cosmos_client, PartitionKey, Offer
import test_config

# This class tests the backwards compatibility of features being deprecated to ensure users are not broken before
# properly removing the methods marked for deprecation.

pytestmark = pytest.mark.cosmosEmulator


@pytest.mark.usefixtures("teardown")
class TestBackwardsCompatibility(unittest.TestCase):

    configs = test_config._test_config
    host = configs.host
    masterKey = configs.masterKey

    @classmethod
    def setUpClass(cls):
        if cls.masterKey == '[YOUR_KEY_HERE]' or cls.host == '[YOUR_ENDPOINT_HERE]':
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")
        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey, consistency_level="Session")
        cls.databaseForTest = cls.client.create_database_if_not_exists(cls.configs.TEST_DATABASE_ID,
                                                                       offer_throughput=500)
        cls.containerForTest = cls.databaseForTest.create_container_if_not_exists(
            cls.configs.TEST_COLLECTION_SINGLE_PARTITION_ID, PartitionKey(path="/id"), offer_throughput=400)

    def test_offer_methods(self):
        database_offer = self.databaseForTest.read_offer()
        container_offer = self.containerForTest.read_offer()

        self.assertTrue("ThroughputProperties" in str(type(database_offer)))
        self.assertTrue("ThroughputProperties" in str(type(container_offer)))

        self.assertTrue(isinstance(database_offer, Offer))
        self.assertTrue(isinstance(container_offer, Offer))


if __name__ == "__main__":
    unittest.main()
