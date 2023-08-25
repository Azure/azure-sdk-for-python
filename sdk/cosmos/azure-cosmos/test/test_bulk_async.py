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
from azure.cosmos.aio._cosmos_client import CosmosClient
from azure.cosmos.partition_key import PartitionKey


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
    async def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")
        cls.client = CosmosClient(cls.host, cls.masterKey, connection_policy=cls.connectionPolicy)
        cls.test_database = await cls.configs.create_database_if_not_exist(cls.client)

    async def test_bulk_create_volume(self):
        # Try with default container (400 RUs)
        container = await self.test_database.create_container_if_not_exists(id="default_bulk_container",
                                                                            partition_key=PartitionKey(path="/id"))

        # Negative test - try to run more than 100 operations for a partition
        operations = []
        for i in range(101):
            operations.append({"operationType": "Create",
                               "resourceBody": {"id": "item-" + str(i), "name": str(uuid.uuid4())},
                               "partitionKey": "item-" + str(i)})
        try:
            await container.bulk(operations=operations)
            self.fail("Bulk operation should have failed due to too many operations per partition.")
        except ValueError as e:
            self.assertEqual(str(e), 'Cannot run bulk request with more than 100 operations per partition.')

        # Remove one operation and try request again
        operations.pop()

        # Negative test - see how many requests were throttled due to lack of RUs on default container
        bulk_result = await container.bulk(operations=operations)
        # Get results from first batch of operations
        batch_result = bulk_result[0]
        throttle_count = 0
        # Batch results are returned as a tuple, index 0 is the result and index 1 are the response headers
        for operation in batch_result[0]:
            if operation.get("statusCode") == 429:
                throttle_count = throttle_count + 1
        self.assertTrue(throttle_count > 10)
        self.assertEqual(len(batch_result[0]), 100)

        # Positive test - create all 100 items with more RUs
        bulk_container = await self.test_database.create_container_if_not_exists(id="throughput_bulk_container",
                                                                                 partition_key=PartitionKey(path="/id"),
                                                                                 offer_throughput=1500)
        bulk_result = await bulk_container.bulk(operations=operations)
        batch_result = bulk_result[0]
        throttle_count = 0
        for operation in batch_result[0]:
            if operation.get("statusCode") == 429:
                throttle_count = throttle_count + 1
        self.assertEqual(throttle_count, 0)
        self.assertEqual(len(batch_result[0]), 100)

    def test_bulk_lsn(self):
        container = await self.test_database.create_container_if_not_exists(id="lsn_bulk_container",
                                                                            partition_key=PartitionKey(path="/id"))
        # Create test items
        await container.create_item({"id": "read_item", "name": str(uuid.uuid4())})
        await container.create_item({"id": "replace_item", "value": 0})
        await container.create_item({"id": "delete_item"})

        await container.read_item(item="read_item", partition_key="read_item")
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

        bulk_result = await container.bulk(operations=operations)
        batch_result = bulk_result[0]

        self.assertEqual(int(lsn), int(batch_result[1].get(HttpHeaders.LSN)) - 1)
        self.assertEqual(batch_result[1].get(HttpHeaders.ItemCount), "5")
        self.assertEqual(batch_result[0][0].get("statusCode"), StatusCodes.CREATED)
        self.assertEqual(batch_result[0][1].get("statusCode"), StatusCodes.OK)
        self.assertEqual(batch_result[0][2].get("statusCode"), StatusCodes.CREATED)
        self.assertEqual(batch_result[0][3].get("statusCode"), StatusCodes.OK)
        self.assertEqual(batch_result[0][4].get("statusCode"), StatusCodes.NO_CONTENT)

    async def test_bulk_invalid_create(self):
        container = await self.test_database.create_container_if_not_exists(id="errors_bulk_container",
                                                                            partition_key=PartitionKey(path="/pk"))
        operations = [{"operationType": "Create",
                       "resourceBody": {"id": "create_item", "name": str(uuid.uuid4())},
                       "partitionKey": "create_item"}]

        bulk_result = await container.bulk(operations=operations)
        self.assertEqual(bulk_result[0][0][0].get("statusCode"), StatusCodes.BAD_REQUEST)

    async def test_bulk_read_non_existent(self):
        container = await self.test_database.create_container_if_not_exists(id="errors_bulk_container",
                                                                            partition_key=PartitionKey(path="/pk"))
        operations = [{"operationType": "Read",
                       "id": "read_item",
                       "partitionKey": "read_item"}]

        bulk_result = await container.bulk(operations=operations)
        self.assertEqual(bulk_result[0][0][0].get("statusCode"), StatusCodes.NOT_FOUND)

    async def test_bulk_delete_non_existent(self):
        container = await self.test_database.create_container_if_not_exists(id="errors_bulk_container",
                                                                            partition_key=PartitionKey(path="/pk"))
        operations = [{"operationType": "Delete",
                       "id": "delete_item",
                       "partitionKey": "delete_item"}]

        bulk_result = await container.bulk(operations=operations)
        self.assertEqual(bulk_result[0][0][0].get("statusCode"), StatusCodes.NOT_FOUND)

    async def test_bulk_create_conflict(self):
        container = await self.test_database.create_container_if_not_exists(id="errors_bulk_container",
                                                                            partition_key=PartitionKey(path="/pk"))
        operations = [{"operationType": "Create",
                       "resourceBody": {"id": "create_item", "name": str(uuid.uuid4())},
                       "partitionKey": "create_item"},
                      {"operationType": "Create",
                       "resourceBody": {"id": "create_item", "name": str(uuid.uuid4())},
                       "partitionKey": "create_item"}]

        bulk_result = await container.bulk(operations=operations)
        self.assertEqual(bulk_result[0][0][1].get("statusCode"), StatusCodes.CONFLICT)
