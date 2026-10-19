# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original async hierarchical-container throughput assertions."""

import os
import unittest
import uuid

from azure.cosmos import documents, exceptions
from azure.cosmos.aio import CosmosClient
from azure.cosmos.http_constants import StatusCodes


class TestCRUDOperationsSubPartitionAsync(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
        self.addAsyncCleanup(self.client.close)
        self.database = await self.client.create_database("throughput_hpk_" + uuid.uuid4().hex)
        self.addAsyncCleanup(self.client.delete_database, self.database.id)

    async def test_partitioned_collection_subpartition_async_rust(self):
        # Source: tests/test_crud_subpartition_async.py::TestSubpartitionCrudAsync.test_partitioned_collection_subpartition_async
        created_db = self.database
        collection_definition = {
            "id": "hierarchical",
            "partitionKey": {"paths": ["/id", "/pk"], "kind": documents.PartitionKind.MultiHash, "version": 2},
        }
        offer_throughput = 10100
        created_collection = await created_db.create_container(
            id=collection_definition["id"], partition_key=collection_definition["partitionKey"],
            offer_throughput=offer_throughput,
        )
        assert collection_definition.get('id') == created_collection.id
        created_collection_properties = await created_collection.read()
        assert collection_definition.get('partitionKey').get('paths') == created_collection_properties['partitionKey']['paths']
        assert collection_definition.get('partitionKey').get('kind') == created_collection_properties['partitionKey']['kind']
        expected_offer = await created_collection.get_throughput()
        assert expected_offer is not None
        assert expected_offer.offer_throughput == offer_throughput
        collection_definition2 = {
            "partitionKey": {
                "paths": ["/id", "/pk", "/id2", "/pk2"], "kind": documents.PartitionKind.MultiHash, "version": 2,
            },
        }
        try:
            await created_db.create_container(
                id=collection_definition["id"], partition_key=collection_definition2["partitionKey"],
                offer_throughput=offer_throughput,
            )
        except exceptions.CosmosHttpResponseError as error:
            assert error.status_code == StatusCodes.BAD_REQUEST
            assert "Too many partition key paths" in error.message
        else:
            self.fail("Four hierarchical partition-key paths must be rejected")
        collection_definition3 = {
            "partitionKey": {
                "paths": ["/id", "/pk", "/id2", "/pk2"], "kind": documents.PartitionKind.Hash, "version": 2,
            },
        }
        try:
            await created_db.create_container(
                id=collection_definition["id"], partition_key=collection_definition3["partitionKey"],
                offer_throughput=offer_throughput,
            )
        except exceptions.CosmosHttpResponseError as error:
            assert error.status_code == StatusCodes.BAD_REQUEST
            assert "Too many partition key paths" in error.message
        else:
            self.fail("Four hash partition-key paths must be rejected")
        await created_db.delete_container(created_collection.id)
