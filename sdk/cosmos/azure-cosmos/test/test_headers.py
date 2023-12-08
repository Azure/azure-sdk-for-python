# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation

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
import uuid
from unittest.mock import MagicMock

import pytest

import azure.cosmos.cosmos_client as cosmos_client
import test_config
from azure.cosmos import PartitionKey, DatabaseProxy


@pytest.mark.cosmosEmulator
class HeadersTest(unittest.TestCase):
    database: DatabaseProxy = None
    client: cosmos_client.CosmosClient = None
    configs = test_config._test_config
    host = configs.host
    masterKey = configs.masterKey

    dedicated_gateway_max_age_thousand = 1000
    dedicated_gateway_max_age_million = 1000000
    dedicated_gateway_max_age_negative = -1

    TEST_DATABASE_ID = "Python SDK Test Database " + str(uuid.uuid4())
    TEST_CONTAINER_ID = "Multi Partition Test Collection With Custom PK " + str(uuid.uuid4())

    @classmethod
    def setUpClass(cls):
        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey)
        cls.database = cls.client.create_database_if_not_exists(cls.TEST_DATABASE_ID)
        cls.container = cls.database.create_container_if_not_exists(
            id=cls.TEST_CONTAINER_ID,
            partition_key=PartitionKey(path="/id"),
            offer_throughput=cls.configs.THROUGHPUT_FOR_5_PARTITIONS)

    @classmethod
    def tearDownClass(cls):
        cls.client.delete_database(cls.TEST_DATABASE_ID)

    def side_effect_dedicated_gateway_max_age_thousand(self, *args, **kwargs):
        # Extract request headers from args
        assert args[2]["x-ms-dedicatedgateway-max-age"] == self.dedicated_gateway_max_age_thousand
        raise StopIteration

    def side_effect_dedicated_gateway_max_age_million(self, *args, **kwargs):
        # Extract request headers from args
        assert args[2]["x-ms-dedicatedgateway-max-age"] == self.dedicated_gateway_max_age_million
        raise StopIteration

    def test_max_integrated_cache_staleness(self):
        cosmos_client_connection = self.container.client_connection
        cosmos_client_connection._CosmosClientConnection__Get = MagicMock(
            side_effect=self.side_effect_dedicated_gateway_max_age_thousand)
        try:
            self.container.read_item(item="id-1", partition_key="pk-1",
                                     max_integrated_cache_staleness_in_ms=self.dedicated_gateway_max_age_thousand)
        except StopIteration:
            pass

        cosmos_client_connection._CosmosClientConnection__Get = MagicMock(
            side_effect=self.side_effect_dedicated_gateway_max_age_million)
        try:
            self.container.read_item(item="id-1", partition_key="pk-1",
                                     max_integrated_cache_staleness_in_ms=self.dedicated_gateway_max_age_million)
        except StopIteration:
            pass

    def test_negative_max_integrated_cache_staleness(self):
        try:
            self.container.read_item(item="id-1", partition_key="pk-1",
                                     max_integrated_cache_staleness_in_ms=self.dedicated_gateway_max_age_negative)
        except Exception as exception:
            assert isinstance(exception, ValueError)


if __name__ == "__main__":
    unittest.main()
