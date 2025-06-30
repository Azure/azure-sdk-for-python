# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest

import pytest
import uuid


import test_config
from azure.cosmos import http_constants
import azure.cosmos.exceptions as exceptions
from azure.cosmos.aio import CosmosClient, _retry_utility_async, DatabaseProxy
from azure.cosmos.partition_key import PartitionKey

client_throughput_bucket_number = 2
request_throughput_bucket_number = 3
async def client_raw_response_hook(response):
    assert (response.http_request.headers[http_constants.HttpHeaders.ThroughputBucket]
            == str(client_throughput_bucket_number))

async def request_raw_response_hook(response):
    assert (response.http_request.headers[http_constants.HttpHeaders.ThroughputBucket]
            == str(request_throughput_bucket_number))

@pytest.mark.cosmosEmulator
class TestHeadersAsync(unittest.IsolatedAsyncioTestCase):
    client: CosmosClient = None
    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    database: DatabaseProxy = None

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

    async def asyncSetUp(self):
        self.client = CosmosClient(self.host, self.masterKey)
        self.database = self.client.get_database_client(self.configs.TEST_DATABASE_ID)
        self.container = self.database.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

    async def test_client_level_throughput_bucket_async(self):
        CosmosClient(self.host, self.masterKey,
            throughput_bucket=client_throughput_bucket_number,
            raw_response_hook=client_raw_response_hook)

    async def test_request_precedence_throughput_bucket_async(self):
        client = CosmosClient(self.host, self.masterKey,
                                   throughput_bucket=client_throughput_bucket_number)
        database = client.get_database_client(self.configs.TEST_DATABASE_ID)
        created_container = await database.create_container(
            str(uuid.uuid4()),
            PartitionKey(path="/pk"))
        await created_container.create_item(
            body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'},
            throughput_bucket=request_throughput_bucket_number,
            raw_response_hook=request_raw_response_hook)
        await database.delete_container(created_container.id)

    async def test_container_read_item_throughput_bucket_async(self):
        created_document = await self.container.create_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})
        await self.container.read_item(
             item=created_document['id'],
             partition_key="mypk",
             throughput_bucket=request_throughput_bucket_number,
             raw_response_hook=request_raw_response_hook)

    async def test_container_read_all_items_throughput_bucket_async(self):
        for i in range(10):
            await self.container.create_item(body={'id': ''.format(i) + str(uuid.uuid4()), 'pk': 'mypk'})

        async for item in self.container.read_all_items(throughput_bucket=request_throughput_bucket_number,
            raw_response_hook=request_raw_response_hook):
            pass

    async def test_container_query_items_throughput_bucket_async(self):
        doc_id = 'MyId' + str(uuid.uuid4())
        document_definition = {'pk': 'pk', 'id': doc_id}
        await self.container.create_item(body=document_definition)

        query = 'SELECT * from c'
        query_results = [item async for item in self.container.query_items(
            query=query,
            partition_key='pk',
            throughput_bucket=request_throughput_bucket_number,
            raw_response_hook=request_raw_response_hook)]

    async def test_container_replace_item_throughput_bucket_async(self):
        created_document = await self.container.create_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})
        await self.container.replace_item(
            item=created_document['id'],
            body={'id': '2' + str(uuid.uuid4()), 'pk': 'mypk'},
            throughput_bucket=request_throughput_bucket_number,
            raw_response_hook=request_raw_response_hook)

    async def test_container_upsert_item_throughput_bucket_async(self):
       await self.container.upsert_item(
            body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'},
            throughput_bucket=request_throughput_bucket_number,
            raw_response_hook=request_raw_response_hook)

    async def test_container_create_item_throughput_bucket_async(self):
        await self.container.create_item(
            body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'},
            throughput_bucket=request_throughput_bucket_number,
            raw_response_hook=request_raw_response_hook)

    async def test_container_patch_item_throughput_bucket_async(self):
        pkValue = "patch_item_pk" + str(uuid.uuid4())
        # Create item to patch
        item = {
            "id": "patch_item",
            "pk": pkValue,
            "prop": "prop1",
            "address": {
                "city": "Redmond"
            },
            "company": "Microsoft",
            "number": 3}
        await self.container.create_item(item)
        # Define and run patch operations
        operations = [
            {"op": "add", "path": "/color", "value": "yellow"},
            {"op": "remove", "path": "/prop"},
            {"op": "replace", "path": "/company", "value": "CosmosDB"},
            {"op": "set", "path": "/address/new_city", "value": "Atlanta"},
            {"op": "incr", "path": "/number", "value": 7},
            {"op": "move", "from": "/color", "path": "/favorite_color"}
        ]
        await self.container.patch_item(
            item="patch_item",
            partition_key=pkValue,
            patch_operations=operations,
            throughput_bucket=request_throughput_bucket_number,
            raw_response_hook=request_raw_response_hook)

    async def test_container_execute_item_batch_throughput_bucket_async(self):
        created_collection = await self.database.create_container(
            id='test_execute_item ' + str(uuid.uuid4()),
            partition_key=PartitionKey(path='/company'))
        batch = []
        for i in range(100):
            batch.append(("create", ({"id": "item" + str(i), "company": "Microsoft"},)))

        await created_collection.execute_item_batch(
            batch_operations=batch,
            partition_key="Microsoft",
            throughput_bucket=request_throughput_bucket_number,
            raw_response_hook=request_raw_response_hook)

        await self.database.delete_container(created_collection)

    async def test_container_delete_item_throughput_bucket_async(self):
        created_item = await self.container.create_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})

        await self.container.delete_item(
            created_item['id'],
            partition_key='mypk',
            throughput_bucket=request_throughput_bucket_number,
            raw_response_hook=request_raw_response_hook)

    async def test_container_delete_all_items_by_partition_key_throughput_bucket_async(self):
        created_collection = await self.database.create_container(
            id='test_delete_all_items_by_partition_key ' + str(uuid.uuid4()),
            partition_key=PartitionKey(path='/pk', kind='Hash'))

        # Create two partition keys
        partition_key1 = "{}-{}".format("Partition Key 1", str(uuid.uuid4()))
        partition_key2 = "{}-{}".format("Partition Key 2", str(uuid.uuid4()))

        # add items for partition key 1
        for i in range(1, 3):
            await created_collection.upsert_item(
                dict(id="item{}".format(i), pk=partition_key1))

        # add items for partition key 2
        pk2_item = await created_collection.upsert_item(dict(id="item{}".format(3), pk=partition_key2))

        # delete all items for partition key 1
        await created_collection.delete_all_items_by_partition_key(
            partition_key1,
            throughput_bucket=request_throughput_bucket_number,
            raw_response_hook=request_raw_response_hook)

        await self.database.delete_container(created_collection)

    # TODO Re-enable once Throughput Bucket Validation Changes are rolled out
    """
    async def test_container_read_item_negative_throughput_bucket_async(self):
        # Creates an item and then tries to read item with an invalid throughput bucket
        created_document = await self.container.create_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})
        try:
            await self.container.read_item(
                 item=created_document['id'],
                 partition_key="mypk",
                 throughput_bucket=256)
            pytest.fail("Read Item should have failed invalid throughput bucket.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "specified for the header 'x-ms-cosmos-throughput-bucket' is invalid." in e.http_error_message
    """

if __name__ == "__main__":
    unittest.main()
