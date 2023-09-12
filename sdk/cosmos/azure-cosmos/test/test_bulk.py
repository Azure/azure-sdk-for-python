# The MIT License (MIT)
# Copyright (c) 2023 Microsoft Corporation

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
import pytest
import test_config

from azure.cosmos.http_constants import HttpHeaders, StatusCodes
from azure.cosmos.cosmos_client import CosmosClient
from azure.cosmos.partition_key import PartitionKey

pytestmark = pytest.mark.cosmosEmulator


@pytest.mark.usefixtures("teardown")
class BulkTests(unittest.TestCase):
    """Python Bulk Tests.
    """

    configs = test_config._test_config
    host = configs.host
    masterKey = configs.masterKey
    connectionPolicy = configs.connectionPolicy
    last_headers = []

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")
        cls.client = CosmosClient(cls.host, cls.masterKey, connection_policy=cls.connectionPolicy)
        cls.test_database = cls.configs.create_database_if_not_exist(cls.client)

    def test_bulk_batch_creation(self):
        container = self.test_database.create_container_if_not_exists(id="default_bulk_container",
                                                                      partition_key=PartitionKey(path="/id"))
        # Verify there is one batch/ 100 operations
        operations = []
        for i in range(201):
            operations.append({"operationType": "Create",
                               "resourceBody": {"id": "item-" + str(i), "name": str(uuid.uuid4())},
                               "partitionKey": "item-" + str(i)})
        bulk_result = container.bulk(operations=operations)
        self.assertEqual(len(bulk_result), 3)

        # Remove one operation and try request again - check there's only 2 batches
        operations.pop()
        bulk_result = container.bulk(operations=operations)
        self.assertEqual(len(bulk_result), 2)

    def test_bulk_throttle(self):
        # Try with default container (400 RUs)
        container = self.test_database.create_container_if_not_exists(id="default_bulk_container",
                                                                      partition_key=PartitionKey(path="/id"))
        operations = []
        for i in range(100):
            operations.append({"operationType": "Create",
                               "resourceBody": {"id": "item-" + str(i), "name": str(uuid.uuid4())},
                               "partitionKey": "item-" + str(i)})

        # check requests were throttled due to lack of RUs on default container
        bulk_result = container.bulk(operations=operations)
        self.assertEqual(len(bulk_result[0][0]), 100)
        batch_response_headers = bulk_result[0][1]
        self.assertTrue(batch_response_headers.get(HttpHeaders.ThrottleRetryCount) > 0)

        # create all 100 items with more RUs
        bulk_container = self.test_database.create_container_if_not_exists(id="throughput_bulk_container",
                                                                           partition_key=PartitionKey(path="/id"),
                                                                           offer_throughput=1000)
        bulk_result = bulk_container.bulk(operations=operations)
        self.assertEqual(len(bulk_result[0][0]), 100)
        batch_response_headers = bulk_result[0][1]
        self.assertTrue(batch_response_headers.get(HttpHeaders.ThrottleRetryCount) is None)

    def test_bulk_lsn(self):
        container = self.test_database.create_container_if_not_exists(id="lsn_bulk_container",
                                                                      partition_key=PartitionKey(path="/id"))
        # Create test items
        container.create_item({"id": "read_item", "name": str(uuid.uuid4())})
        container.create_item({"id": "replace_item", "value": 0})
        container.create_item({"id": "delete_item"})

        container.read_item(item="read_item", partition_key="read_item")
        lsn = container.client_connection.last_response_headers.get(HttpHeaders.LSN)

        operations = []

        operations.append({"operationType": "Create",
                           "resourceBody": {"id": "create_item", "name": str(uuid.uuid4())},
                           "partitionKey": "create_item"})
        operations.append({"operationType": "Replace",
                           "id": "replace_item",
                           "partitionKey": "replace_item",
                           "resourceBody": {"id": "replace_item", "message": "item was replaced"}})
        operations.append({"operationType": "Upsert",
                           "resourceBody": {"id": "upsert_item", "name": str(uuid.uuid4())},
                           "partitionKey": "upsert_item"})
        operations.append({"operationType": "Read",
                           "id": "read_item",
                           "partitionKey": "read_item"})
        operations.append({"operationType": "Delete",
                           "id": "delete_item",
                           "partitionKey": "delete_item"})

        bulk_result = container.bulk(operations=operations)
        batch_result = bulk_result[0]

        self.assertEqual(int(lsn), int(batch_result[1].get(HttpHeaders.LSN)) - 1)
        self.assertEqual(batch_result[1].get(HttpHeaders.ItemCount), "5")
        self.assertEqual(batch_result[0][0].get("statusCode"), StatusCodes.CREATED)
        self.assertEqual(batch_result[0][1].get("statusCode"), StatusCodes.OK)
        self.assertEqual(batch_result[0][2].get("statusCode"), StatusCodes.CREATED)
        self.assertEqual(batch_result[0][3].get("statusCode"), StatusCodes.OK)
        self.assertEqual(batch_result[0][4].get("statusCode"), StatusCodes.NO_CONTENT)

    def test_bulk_invalid_create(self):
        container = self.test_database.create_container_if_not_exists(id="errors_bulk_container",
                                                                      partition_key=PartitionKey(path="/pk"))
        operations = [{"operationType": "Create",
                       "resourceBody": {"id": "create_item", "name": str(uuid.uuid4())},
                       "partitionKey": "create_item"}]

        bulk_result = container.bulk(operations=operations)
        self.assertEqual(bulk_result[0][0][0].get("statusCode"), StatusCodes.BAD_REQUEST)

    def test_bulk_read_non_existent(self):
        container = self.test_database.create_container_if_not_exists(id="errors_bulk_container",
                                                                      partition_key=PartitionKey(path="/id"))
        operations = [{"operationType": "Read",
                       "id": "read_item",
                       "partitionKey": "read_item"}]

        bulk_result = container.bulk(operations=operations)
        self.assertEqual(bulk_result[0][0][0].get("statusCode"), StatusCodes.NOT_FOUND)

    def test_bulk_delete_non_existent(self):
        container = self.test_database.create_container_if_not_exists(id="errors_bulk_container",
                                                                      partition_key=PartitionKey(path="/id"))
        operations = [{"operationType": "Delete",
                       "id": "delete_item",
                       "partitionKey": "delete_item"}]

        bulk_result = container.bulk(operations=operations)
        self.assertEqual(bulk_result[0][0][0].get("statusCode"), StatusCodes.NOT_FOUND)

    def test_bulk_create_conflict(self):
        container = self.test_database.create_container_if_not_exists(id="errors_bulk_container",
                                                                      partition_key=PartitionKey(path="/id"))
        operations = [{"operationType": "Create",
                       "resourceBody": {"id": "create_item", "name": str(uuid.uuid4())},
                       "partitionKey": "create_item"},
                      {"operationType": "Create",
                       "resourceBody": {"id": "create_item", "name": str(uuid.uuid4())},
                       "partitionKey": "create_item"},
                      {"operationType": "Create",
                       "resourceBody": {"id": "create_item2", "name": str(uuid.uuid4())},
                       "partitionKey": "create_item"}]

        bulk_result = container.bulk(operations=operations)
        self.assertEqual(bulk_result[0][0][0].get("statusCode"), StatusCodes.CREATED)
        self.assertEqual(bulk_result[0][0][1].get("statusCode"), StatusCodes.CONFLICT)
        self.assertEqual(bulk_result[0][0][2].get("statusCode"), StatusCodes.CREATED)
