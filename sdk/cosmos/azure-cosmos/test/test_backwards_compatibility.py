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
from azure.cosmos import cosmos_client, PartitionKey, Offer, http_constants
import test_config
from unittest.mock import MagicMock

# This class tests the backwards compatibility of features being deprecated to ensure users are not broken before
# properly removing the methods marked for deprecation.

pytestmark = pytest.mark.cosmosEmulator


@pytest.mark.usefixtures("teardown")
class TestBackwardsCompatibility(unittest.TestCase):

    configs = test_config._test_config
    host = configs.host
    masterKey = configs.masterKey

    populate_true = True

    @classmethod
    def setUpClass(cls):
        if cls.masterKey == '[YOUR_KEY_HERE]' or cls.host == '[YOUR_ENDPOINT_HERE]':
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")
        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey, consistency_level="Session")
        cls.databaseForTest = cls.client.create_database_if_not_exists("Offer_Test_DB",
                                                                       offer_throughput=500)
        cls.containerForTest = cls.databaseForTest.create_container_if_not_exists(
            cls.configs.TEST_COLLECTION_SINGLE_PARTITION_ID, PartitionKey(path="/id"), offer_throughput=400)

    def test_offer_methods(self):
        database_offer = self.databaseForTest.get_throughput()
        container_offer = self.containerForTest.get_throughput()

        self.assertTrue("ThroughputProperties" in str(type(database_offer)))
        self.assertTrue("ThroughputProperties" in str(type(container_offer)))

        self.assertTrue(isinstance(database_offer, Offer))
        self.assertTrue(isinstance(container_offer, Offer))

    def side_effect_populate_partition_key_range_statistics(self, *args, **kwargs):
        # Extract request headers from args
        self.assertTrue(args[2][http_constants.HttpHeaders.PopulatePartitionKeyRangeStatistics] is True)
        raise StopIteration

    def side_effect_populate_query_metrics(self, *args, **kwargs):
        # Extract request headers from args
        self.assertTrue(args[2][http_constants.HttpHeaders.PopulateQueryMetrics] is True)
        raise StopIteration

    def side_effect_populate_quota_info(self, *args, **kwargs):
        # Extract request headers from args
        self.assertTrue(args[2][http_constants.HttpHeaders.PopulateQuotaInfo] is True)
        raise StopIteration

    def test_populate_query_metrics(self):
        cosmos_client_connection = self.containerForTest.client_connection
        cosmos_client_connection._CosmosClientConnection__Get = MagicMock(
            side_effect=self.side_effect_populate_query_metrics)
        try:
            self.containerForTest.read(populate_query_metrics=True)
        except StopIteration:
            pass
        try:
            self.containerForTest.read(True)
        except StopIteration:
            pass

    def test_populate_quota_info(self):
        cosmos_client_connection = self.containerForTest.client_connection
        cosmos_client_connection._CosmosClientConnection__Get = MagicMock(
            side_effect=self.side_effect_populate_quota_info)
        try:
            self.containerForTest.read(populate_quota_info=True)
        except StopIteration:
            pass
        try:
            self.containerForTest.read(False, True)
        except StopIteration:
            pass

    def test_populate_partition_key_range_statistics(self):
        cosmos_client_connection = self.containerForTest.client_connection
        cosmos_client_connection._CosmosClientConnection__Get = MagicMock(
            side_effect=self.side_effect_populate_partition_key_range_statistics)
        try:
            self.containerForTest.read(populate_partition_key_range_statistics=True)
        except StopIteration:
            pass
        try:
            self.containerForTest.read(False, False, True)
        except StopIteration:
            pass


if __name__ == "__main__":
    unittest.main()
