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
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos import AutoScale, PartitionKey, http_constants
import pytest
import test_config

pytestmark = pytest.mark.cosmosEmulator


@pytest.mark.usefixtures("teardown")
class AutoScaleTest(unittest.TestCase):
    host = test_config._test_config.host
    masterKey = test_config._test_config.masterKey
    connectionPolicy = test_config._test_config.connectionPolicy

    def __AssertHTTPFailureWithStatus(self, status_code, func, *args, **kwargs):
        """Assert HTTP failure with status.

        :Parameters:
            - `status_code`: int
            - `func`: function
        """
        try:
            func(*args, **kwargs)
            self.assertFalse(True, 'function should fail.')
        except exceptions.CosmosHttpResponseError as inst:
            self.assertEqual(inst.status_code, status_code)

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey, consistency_level="Session",
                                                connection_policy=cls.connectionPolicy)
        cls.created_database = cls.client.create_database_if_not_exists(test_config._test_config.TEST_DATABASE_ID)
        cls.created_collection = cls.created_database.create_container_if_not_exists(
            test_config._test_config.TEST_COLLECTION_SINGLE_PARTITION_ID, PartitionKey(path="/id"))

    def test_auto_scale_max_throughput(self):
        created_container = self.created_database.create_container(
            id='container_with_auto_scale_setting',
            partition_key=PartitionKey(path="/id"),
            auto_scale_setting=AutoScale(5000,0)

        )
        created_container_properties = created_container.get_throughput()
        # Testing the input values of the max_throughput
        self.assertEqual(
            created_container_properties.properties['content']['offerAutopilotSettings']['maxThroughput'], 5000)

        self.created_database.delete_container(created_container)
        # Testing the incorrect passing of an input value of the max_throughput to verify negative behavior
        try:
            created_container = self.created_database.create_container(
                id='container_with_wrong_auto_scale_setting',
                partition_key=PartitionKey(path="/id"),
                auto_scale_setting=AutoScale(200, 0)

            )
        except exceptions.CosmosHttpResponseError as e:
            self.assertEqual(e.status_code, http_constants.StatusCodes.BAD_REQUEST)


    def test_auto_scale_increment_percentage(self):
        created_container = self.created_database.create_container(
            id='container_with_auto_scale_setting',
            partition_key=PartitionKey(path="/id"),
            auto_scale_setting=AutoScale(5000,1)

        )
        created_container_properties = created_container.get_throughput()
        # Testing the input values of the max_increment_percentage
        self.assertEqual(
            created_container_properties.properties['content']['offerAutopilotSettings']['autoUpgradePolicy']['throughputPolicy']['incrementPercent'], 1)

        self.created_database.delete_container(created_container)
        # Testing the incorrect passing of an input value of the max_increment_percentage to verify negative behavior
        try:
            created_container = self.created_database.create_container(
                id='container_with_wrong_auto_scale_setting',
                partition_key=PartitionKey(path="/id"),
                auto_scale_setting=AutoScale(5000, -25)

            )
            self.created_database.delete_container(created_container)
        except exceptions.CosmosHttpResponseError as e:
            self.assertEqual(e.status_code, http_constants.StatusCodes.BAD_REQUEST)


    def test_auto_scale_setting(self):
        # Testing for wrong attributes for the auto_scale_setting in the created container
        try:
            created_container = self.created_database.create_container(
                id='container_with_wrong_auto_scale_setting',
                partition_key=PartitionKey(path="/id"),
                auto_scale_setting="wrong setting"

            )
        except AttributeError:
            pass
