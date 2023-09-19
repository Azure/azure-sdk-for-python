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

import uuid
import pytest
import test_config

from azure.cosmos.http_constants import HttpHeaders, StatusCodes
from azure.cosmos.aio._cosmos_client import CosmosClient
from azure.cosmos.partition_key import PartitionKey

pytestmark = pytest.mark.cosmosEmulator

@pytest.mark.usefixtures("teardown")
class TestBulk:
    """Python Bulk Tests.
    """

    configs = test_config._test_config
    host = configs.host
    masterKey = configs.masterKey
    connectionPolicy = configs.connectionPolicy
    last_headers = []

    @classmethod
    async def _set_up(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")
        cls.client = CosmosClient(cls.host, cls.masterKey)
        cls.test_database = await cls.client.create_database_if_not_exists(cls.configs.TEST_DATABASE_ID)

    @pytest.mark.asyncio
    async def test_bulk_batch_creation_async(self):
        await self._set_up()
        container = await self.test_database.create_container_if_not_exists(id="default_bulk_container",
                                                                            partition_key=PartitionKey(path="/id"))
        # Verify there is one batch/ 100 operations
        operations = []
        for i in range(201):
            operations.append({"operationType": "Create",
                               "resourceBody": {"id": "item-" + str(i), "name": str(uuid.uuid4())},
                               "partitionKey": "item-" + str(i)})
        bulk_result = await container.bulk(operations=operations)
        assert len(bulk_result[1]) == 3

        # Remove one operation and try request again - check there's only 2 batches
        operations.pop()
        bulk_result = await container.bulk(operations=operations)
        assert len(bulk_result[1]) == 2

    @pytest.mark.asyncio
    async def test_bulk_throttle_async(self):
        await self._set_up()
        # Try with default container (400 RUs)
        container = await self.test_database.create_container_if_not_exists(id="default_bulk_container",
                                                                            partition_key=PartitionKey(path="/id"))
        operations = []
        for i in range(100):
            operations.append({"operationType": "Create",
                               "resourceBody": {"id": "item-" + str(i), "name": str(uuid.uuid4())},
                               "partitionKey": "item-" + str(i)})

        # check requests were throttled due to lack of RUs on default container
        bulk_result = await container.bulk(operations=operations)
        assert len(bulk_result[0][1]) == 100
        batch_response_headers = bulk_result[1][0]
        assert batch_response_headers.get(HttpHeaders.ThrottleRetryCount) > 0

        # create all 100 items with more RUs
        bulk_container = await self.test_database.create_container_if_not_exists(id="throughput_bulk_container",
                                                                                 partition_key=PartitionKey(path="/id"),
                                                                                 offer_throughput=1000)
        bulk_result = await bulk_container.bulk(operations=operations)
        assert len(bulk_result[0][1]) == 100
        batch_response_headers = bulk_result[1][0]
        assert batch_response_headers.get(HttpHeaders.ThrottleRetryCount) is None

    @pytest.mark.asyncio
    async def test_bulk_lsn_async(self):
        await self._set_up()
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

        assert int(lsn) == int(batch_result[1][0].get(HttpHeaders.LSN)) - 1
        assert batch_result[1][0].get(HttpHeaders.ItemCount) == "5"
        assert batch_result[0][1][0].get("statusCode") == StatusCodes.CREATED
        assert batch_result[0][1][1].get("statusCode") == StatusCodes.OK
        assert batch_result[0][1][2].get("statusCode") == StatusCodes.CREATED
        assert batch_result[0][1][3].get("statusCode") == StatusCodes.OK
        assert batch_result[0][1][4].get("statusCode") == StatusCodes.NO_CONTENT

    @pytest.mark.asyncio
    async def test_bulk_invalid_create_async(self):
        await self._set_up()
        container = await self.test_database.create_container_if_not_exists(id="errors_bulk_container",
                                                                            partition_key=PartitionKey(path="/pk"))
        operations = [{"operationType": "Create",
                       "resourceBody": {"id": "create_item", "name": str(uuid.uuid4())},
                       "partitionKey": "create_item"}]

        bulk_result = await container.bulk(operations=operations)
        assert bulk_result[0][1][0].get("statusCode") == StatusCodes.BAD_REQUEST

    @pytest.mark.asyncio
    async def test_bulk_read_non_existent_async(self):
        await self._set_up()
        container = await self.test_database.create_container_if_not_exists(id="errors_bulk_container",
                                                                            partition_key=PartitionKey(path="/pk"))
        operations = [{"operationType": "Read",
                       "id": "read_item",
                       "partitionKey": "read_item"}]

        bulk_result = await container.bulk(operations=operations)
        assert bulk_result[0][1][0].get("statusCode") == StatusCodes.NOT_FOUND

    @pytest.mark.asyncio
    async def test_bulk_delete_non_existent_async(self):
        await self._set_up()
        container = await self.test_database.create_container_if_not_exists(id="errors_bulk_container",
                                                                            partition_key=PartitionKey(path="/pk"))
        operations = [{"operationType": "Delete",
                       "id": "delete_item",
                       "partitionKey": "delete_item"}]

        bulk_result = await container.bulk(operations=operations)
        assert bulk_result[0][1][0].get("statusCode") == StatusCodes.NOT_FOUND

    @pytest.mark.asyncio
    async def test_bulk_create_conflict_async(self):
        await self._set_up()
        container = await self.test_database.create_container_if_not_exists(id="errors_bulk_container",
                                                                            partition_key=PartitionKey(path="/pk"))
        operations = [{"operationType": "Create",
                       "resourceBody": {"id": "create_item", "name": str(uuid.uuid4())},
                       "partitionKey": "create_item"},
                      {"operationType": "Create",
                       "resourceBody": {"id": "create_item", "name": str(uuid.uuid4())},
                       "partitionKey": "create_item"},
                      {"operationType": "Create",
                       "resourceBody": {"id": "create_item2", "name": str(uuid.uuid4())},
                       "partitionKey": "create_item"}]

        bulk_result = await container.bulk(operations=operations)
        assert bulk_result[0][1][0].get("statusCode") == StatusCodes.CREATED
        assert bulk_result[0][1][1].get("statusCode") == StatusCodes.CONFLICT
        assert bulk_result[0][1][2].get("statusCode") == StatusCodes.CREATED