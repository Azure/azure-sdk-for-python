# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid

import pytest

import azure.cosmos.exceptions as exceptions
import test_config
from azure.cosmos import CosmosClient as CosmosSyncClient
from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient


@pytest.mark.cosmosSearchQuery
class TestVectorPolicyAsync(unittest.IsolatedAsyncioTestCase):
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy

    client: CosmosClient = None
    cosmos_sync_client: CosmosSyncClient = None

    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")
        cls.cosmos_sync_client = CosmosSyncClient(cls.host, cls.masterKey)
        cls.test_db = cls.cosmos_sync_client.create_database(str(uuid.uuid4()))

    @classmethod
    def tearDownClass(cls):
        cls.cosmos_sync_client.delete_database(cls.test_db.id)

    async def asyncSetUp(self):
        self.client = CosmosClient(self.host, self.masterKey)
        self.test_db = self.client.get_database_client(self.test_db.id)

    async def asyncTearDown(self):
        await self.client.close()

    async def test_create_vector_embedding_container_async(self):
        indexing_policy = {
            "vectorIndexes": [
                {"path": "/vector1", "type": "flat"},

                {"path": "/vector2", "type": "quantizedFlat", "quantizationByteSize": 64, "vectorIndexShardKey": ["/city"]},

                {"path": "/vector3", "type": "diskANN", "quantizationByteSize": 8, "indexingSearchListSize": 50}
            ]
        }
        vector_embedding_policy = {
            "vectorEmbeddings": [
                {
                    "path": "/vector1",
                    "dataType": "float32",
                    "dimensions": 256,
                    "distanceFunction": "euclidean"
                },
                {
                    "path": "/vector2",
                    "dataType": "int8",
                    "dimensions": 200,
                    "distanceFunction": "dotproduct"
                },
                {
                    "path": "/vector3",
                    "dataType": "uint8",
                    "dimensions": 400,
                    "distanceFunction": "cosine"
                }
            ]
        }
        container_id = "vector_container" + str(uuid.uuid4())
        created_container = await self.test_db.create_container(
            id=container_id,
            partition_key=PartitionKey(path="/id"),
            vector_embedding_policy=vector_embedding_policy,
            indexing_policy=indexing_policy
        )
        properties = await created_container.read()
        assert properties["vectorEmbeddingPolicy"] == vector_embedding_policy
        assert properties["indexingPolicy"]["vectorIndexes"] == indexing_policy["vectorIndexes"]
        await self.test_db.delete_container(container_id)

    async def test_fail_create_vector_indexing_policy_async(self):
        vector_embedding_policy = {
            "vectorEmbeddings": [
                {
                    "path": "/vector1",
                    "dataType": "float32",
                    "dimensions": 256,
                    "distanceFunction": "euclidean"
                },
                {
                    "path": "/vector2",
                    "dataType": "int8",
                    "dimensions": 200,
                    "distanceFunction": "dotproduct"
                }
            ]
        }

        # Pass a vector indexing policy without embedding policy
        indexing_policy = {
            "vectorIndexes": [
                {"path": "/vector1", "type": "flat"}]
        }
        try:
            await self.test_db.create_container(
                id='vector_container',
                partition_key=PartitionKey(path="/id"),
                indexing_policy=indexing_policy
            )
            pytest.fail("Container creation should have failed for lack of embedding policy.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "vector1 not matching in Embedding's path" in e.http_error_message

        # Pass a vector indexing policy with an invalid type
        indexing_policy = {
            "vectorIndexes": [
                {"path": "/vector1", "type": "notFlat"}]
        }
        try:
            await self.test_db.create_container(
                id='vector_container',
                partition_key=PartitionKey(path="/id"),
                indexing_policy=indexing_policy,
                vector_embedding_policy=vector_embedding_policy
            )
            pytest.fail("Container creation should have failed for wrong index type.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "Index Type::notFlat is invalid" in e.http_error_message

        # Pass a vector indexing policy with non-matching path
        indexing_policy = {
            "vectorIndexes": [
                {"path": "/vector3", "type": "flat"}]
        }
        try:
            await self.test_db.create_container(
                id='vector_container',
                partition_key=PartitionKey(path="/id"),
                indexing_policy=indexing_policy,
                vector_embedding_policy=vector_embedding_policy
            )
            pytest.fail("Container creation should have failed for index mismatch.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "vector3 not matching in Embedding's path" in e.http_error_message

        # Pass a vector indexing policy with wrong quantizationByteSize value
        indexing_policy = {
            "vectorIndexes": [
                {"path": "/vector1", "type": "quantizedFlat", "quantizationByteSize": 0}]
        }
        try:
            await self.test_db.create_container(
                id='vector_container',
                partition_key=PartitionKey(path="/id"),
                indexing_policy=indexing_policy,
                vector_embedding_policy=vector_embedding_policy
            )
            pytest.fail("Container creation should have failed for value mismatch.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "The Vector Indexing Policy parameter QuantizationByteSize value :: 0 is out of range. The allowed range is between 1 and 256." \
                   in e.http_error_message

        # Pass a vector indexing policy with wrong indexingSearchListSize value
        indexing_policy = {
            "vectorIndexes": [
                {"path": "/vector1", "type": "diskANN", "indexingSearchListSize": 5}]
        }
        try:
            await self.test_db.create_container(
                id='vector_container',
                partition_key=PartitionKey(path="/id"),
                indexing_policy=indexing_policy,
                vector_embedding_policy=vector_embedding_policy
            )
            pytest.fail("Container creation should have failed for value mismatch.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "IndexingSearchListSize value :: 5 is out of range. The allowed range is between 25 and 500." \
                   in e.http_error_message

        # Pass a vector indexing policy with wrong vectorIndexShardKey value
        indexing_policy = {
            "vectorIndexes": [
                {"path": "/vector2", "type": "diskANN", "vectorIndexShardKey": ["country"]}]
        }
        try:
            await self.test_db.create_container(
                id='vector_container',
                partition_key=PartitionKey(path="/id"),
                indexing_policy=indexing_policy,
                vector_embedding_policy=vector_embedding_policy
            )
            pytest.fail("Container creation should have failed for value mismatch.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "The Vector Indexing Policy has an invalid Shard Path: country." in e.http_error_message

        # Pass a vector indexing policy with too many shard paths
        indexing_policy = {
            "vectorIndexes": [
                {"path": "/vector2", "type": "diskANN", "vectorIndexShardKey": ["/country", "/city", "/zipcode"]}]
        }
        try:
            await self.test_db.create_container(
                id='vector_container',
                partition_key=PartitionKey(path="/id"),
                indexing_policy=indexing_policy,
                vector_embedding_policy=vector_embedding_policy
            )
            pytest.fail("Container creation should have failed for value mismatch.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "The number of shard paths defined in the Vector Indexing Policy: 3 exceeds the maximum: 1." \
                   in e.http_error_message

    async def test_fail_replace_vector_indexing_policy_async(self):
        vector_embedding_policy = {
            "vectorEmbeddings": [
                {
                    "path": "/vector1",
                    "dataType": "float32",
                    "dimensions": 256,
                    "distanceFunction": "euclidean"
                }]}
        indexing_policy = {
            "vectorIndexes": [
                {"path": "/vector1", "type": "flat"}]
        }
        container_id = "vector_container" + str(uuid.uuid4())
        created_container = await self.test_db.create_container(
            id=container_id,
            partition_key=PartitionKey(path="/id"),
            indexing_policy=indexing_policy,
            vector_embedding_policy=vector_embedding_policy
        )
        new_indexing_policy = {
            "vectorIndexes": [
                {"path": "/vector1", "type": "quantizedFlat"}]
        }
        try:
            await self.test_db.replace_container(
                created_container,
                PartitionKey(path="/id"),
                indexing_policy=new_indexing_policy)
            pytest.fail("Container replace should have failed for indexing policy.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert ("The Vector Indexing Policy's path::/vector1 not matching in Embedding's path."
                    in e.http_error_message)
        await self.test_db.delete_container(container_id)

    async def test_fail_create_vector_embedding_policy_async(self):
        # Using invalid data type
        vector_embedding_policy = {
            "vectorEmbeddings": [
                {
                    "path": "/vector1",
                    "dataType": "float33",
                    "dimensions": 256,
                    "distanceFunction": "euclidean"
                }]}
        try:
            await self.test_db.create_container(
                id='vector_container',
                partition_key=PartitionKey(path="/id"),
                vector_embedding_policy=vector_embedding_policy)
            pytest.fail("Container creation should have failed but succeeded.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "Vector Embedding Policy has an invalid DataType" in e.http_error_message

        # Using too many dimensions
        vector_embedding_policy = {
            "vectorEmbeddings": [
                {
                    "path": "/vector1",
                    "dataType": "float32",
                    "dimensions": 8000,
                    "distanceFunction": "euclidean"
                }]}
        try:
            await self.test_db.create_container(
                id='vector_container',
                partition_key=PartitionKey(path="/id"),
                vector_embedding_policy=vector_embedding_policy)
            pytest.fail("Container creation should have failed but succeeded.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "Vector Embedding Policy has Dimensions:8000 which is more than the maximum" \
                   " supported value" in e.http_error_message

        # Using negative dimensions
        vector_embedding_policy = {
            "vectorEmbeddings": [
                {
                    "path": "/vector1",
                    "dataType": "float32",
                    "dimensions": -1,
                    "distanceFunction": "euclidean"
                }]}
        try:
            await self.test_db.create_container(
                id='vector_container',
                partition_key=PartitionKey(path="/id"),
                vector_embedding_policy=vector_embedding_policy)
            pytest.fail("Container creation should have failed but succeeded.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "The Vector Embedding Policy has Dimensions:-1" in e.http_error_message

        # Using invalid distance function
        vector_embedding_policy = {
            "vectorEmbeddings": [
                {
                    "path": "/vector1",
                    "dataType": "float32",
                    "dimensions": 256,
                    "distanceFunction": "handMeasured"
                }]}
        try:
            await self.test_db.create_container(
                id='vector_container',
                partition_key=PartitionKey(path="/id"),
                vector_embedding_policy=vector_embedding_policy
            )
            pytest.fail("Container creation should have failed but succeeded.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "The Vector Embedding Policy has an invalid DistanceFunction:handMeasured" in e.http_error_message


if __name__ == '__main__':
    unittest.main()
