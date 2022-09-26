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
from azure.cosmos.aio import CosmosClient
import azure.cosmos.exceptions as exceptions
from azure.cosmos import ThroughputProperties, PartitionKey, http_constants
import pytest
import test_config

pytestmark = pytest.mark.cosmosEmulator


@pytest.mark.usefixtures("teardown")
class AutoScaleTest(unittest.TestCase):
    host = test_config._test_config.host
    masterKey = test_config._test_config.masterKey
    connectionPolicy = test_config._test_config.connectionPolicy

    @classmethod
    async def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

        cls.client = CosmosClient(cls.host, cls.masterKey, consistency_level="Session",
                                  connection_policy=cls.connectionPolicy)
        cls.created_database = await cls.client.create_database_if_not_exists(test_config._test_config.TEST_DATABASE_ID)

    async def test_auto_scale(self):
        created_container = await self.created_database.create_container(
            id='container_with_auto_scale_settings',
            partition_key=PartitionKey(path="/id"),
            offer_throughput=ThroughputProperties(auto_scale_max_throughput=5000, auto_scale_increment_percent=0)

        )
        created_container_properties = await created_container.get_throughput()
        # Testing the input value of the max_throughput
        self.assertEqual(
            created_container_properties.auto_scale_max_throughput, 5000)
        self.assertEqual(created_container_properties.auto_scale_increment_percent, 0)
        self.assertEqual(created_container_properties.offer_throughput, None)

        await self.created_database.delete_container(created_container)

        # Testing the incorrect passing of an input value of the max_throughput to verify negative behavior
        with pytest.raises(exceptions.CosmosHttpResponseError) as e:
            created_container = await self.created_database.create_container(
                id='container_with_wrong_auto_scale_settings',
                partition_key=PartitionKey(path="/id"),
                offer_throughput=ThroughputProperties(auto_scale_max_throughput=-200, auto_scale_increment_percent=0))
        assert "Requested throughput -200 is less than required minimum throughput 1000" in str(e.value)

    async def test_create_container_if_not_exist(self):
        # Testing auto_scale_settings for the create_container_if_not_exists method
        created_container = await self.created_database.create_container_if_not_exists(
            id='container_with_auto_scale_settings',
            partition_key=PartitionKey(path="/id"),
            offer_throughput=ThroughputProperties(auto_scale_max_throughput=1000, auto_scale_increment_percent=0)
        )
        created_container_properties = await created_container.get_throughput()
        # Testing the incorrect input value of the max_throughput
        self.assertNotEqual(
            created_container_properties.auto_scale_max_throughput, 2000)

        await self.created_database.delete_container(created_container)

        created_container = await self.created_database.create_container_if_not_exists(
            id='container_with_auto_scale_settings',
            partition_key=PartitionKey(path="/id"),
            offer_throughput=ThroughputProperties(auto_scale_max_throughput=5000, auto_scale_increment_percent=2)

        )
        created_container_properties = await created_container.get_throughput()
        # Testing the incorrect input value of the max_increment_percentage
        self.assertNotEqual(
            created_container_properties.auto_scale_increment_percent, 3)

        await self.created_database.delete_container(created_container)

    async def test_create_database(self):
        # Testing auto_scale_settings for the create_database method
        created_database = await self.client.create_database("db1", offer_throughput=ThroughputProperties(
            auto_scale_max_throughput=5000,
            auto_scale_increment_percent=0))
        created_db_properties = await created_database.get_throughput()
        # Testing the input value of the max_throughput
        self.assertEqual(
            created_db_properties.auto_scale_max_throughput, 5000)
        # Testing the input value of the increment_percentage
        self.assertEqual(
            created_db_properties.auto_scale_increment_percent, 0)

        await self.client.delete_database("db1")

    async def test_create_database_if_not_exists(self):
        # Testing auto_scale_settings for the create_database_if_not_exists method
        created_database = await self.client.create_database_if_not_exists("db2", offer_throughput=ThroughputProperties(
            auto_scale_max_throughput=9000,
            auto_scale_increment_percent=11))
        created_db_properties = await created_database.get_throughput()
        # Testing the input value of the max_throughput
        self.assertNotEqual(
            created_db_properties.auto_scale_max_throughput, 8000)
        # Testing the input value of the increment_percentage
        self.assertEqual(
            created_db_properties.auto_scale_increment_percent, 11)

        await self.client.delete_database("db2")

    async def test_replace_throughput(self):
        created_container = await self.created_database.create_container(
            id='container_with_auto_scale_settings',
            partition_key=PartitionKey(path="/id"),
            offer_throughput=ThroughputProperties(auto_scale_max_throughput=5000, auto_scale_increment_percent=0)

        )
        new_throughput = await created_container.replace_throughput(
            throughput=ThroughputProperties(auto_scale_max_throughput=7000, auto_scale_increment_percent=20))
        created_container_properties = await created_container.get_throughput()
        # Testing the input value of the replaced auto_scale settings
        self.assertEqual(
            created_container_properties.auto_scale_max_throughput, 7000)
        self.assertEqual(
            created_container_properties.auto_scale_increment_percent, 20)

        await self.client.delete_database(test_config._test_config.TEST_DATABASE_ID)
