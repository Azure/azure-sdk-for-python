# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid

import pytest

import azure.cosmos.exceptions as exceptions
import test_config
from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient, DatabaseProxy


@pytest.mark.skip  # Skipping tests until emulator supports
class TestAutoScaleAsync(unittest.IsolatedAsyncioTestCase):
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy

    client: CosmosClient = None
    created_database: DatabaseProxy = None

    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID

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
        self.created_database = self.client.get_database_client(self.TEST_DATABASE_ID)

    async def tearDown(self):
        await self.client.close()

    async def test_create_vector_embedding_container(self):
        indexing_policy = {
            "vectorIndexes": [
                {"path": "/vector1", "type": "flat"},
                {"path": "/vector2", "type": "quantizedFlat"},
                {"path": "/vector3", "type": "diskANN"}
            ]
        }
        vector_embedding_policy = {
            "vectorEmbeddings": [
                {
                    "path": "/vector1",
                    "dataType": "float32",
                    "dimensions": 1000,
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
        created_container = await self.created_database.create_container(
            id=container_id,
            partition_key=PartitionKey(path="/id"),
            vector_embedding_policy=vector_embedding_policy,
            indexing_policy=indexing_policy
        )
        properties = await created_container.read()
        assert properties["vectorEmbeddingPolicy"] == vector_embedding_policy
        await self.created_database.delete_container(container_id)

    async def test_fail_create_vector_indexing_policy(self):
        vector_embedding_policy = {
            "vectorEmbeddings": [
                {
                    "path": "/vector1",
                    "dataType": "float32",
                    "dimensions": 1000,
                    "distanceFunction": "euclidean"
                }]}

        # Pass a vector indexing policy without embedding policy
        indexing_policy = {
            "vectorIndexes": [
                {"path": "/vector1", "type": "flat"}]
        }
        try:
            await self.created_database.create_container(
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
            await self.created_database.create_container(
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
                {"path": "/vector2", "type": "flat"}]
        }
        try:
            await self.created_database.create_container(
                id='vector_container',
                partition_key=PartitionKey(path="/id"),
                indexing_policy=indexing_policy,
                vector_embedding_policy=vector_embedding_policy
            )
            pytest.fail("Container creation should have failed for index mismatch.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "vector2 not matching in Embedding's path" in e.http_error_message

    async def test_fail_replace_vector_indexing_policy(self):
        vector_embedding_policy = {
            "vectorEmbeddings": [
                {
                    "path": "/vector1",
                    "dataType": "float32",
                    "dimensions": 1000,
                    "distanceFunction": "euclidean"
                }]}
        indexing_policy = {
            "vectorIndexes": [
                {"path": "/vector1", "type": "flat"}]
        }
        container_id = "vector_container" + str(uuid.uuid4())
        created_container = await self.created_database.create_container(
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
            await self.created_database.replace_container(
                created_container,
                PartitionKey(path="/id"),
                indexing_policy=new_indexing_policy)
            pytest.fail("Container replace should have failed for indexing policy.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "Vector Indexing Policy cannot be changed in Collection Replace" in e.http_error_message
        await self.created_database.delete_container(container_id)

    async def test_fail_create_vector_embedding_policy(self):
        # Using invalid data type
        vector_embedding_policy = {
            "vectorEmbeddings": [
                {
                    "path": "/vector1",
                    "dataType": "float33",
                    "dimensions": 1000,
                    "distanceFunction": "euclidean"
                }]}
        try:
            await self.created_database.create_container(
                id='vector_container',
                partition_key=PartitionKey(path="/id"),
                vector_embedding_policy=vector_embedding_policy
            )
            pytest.fail("Container creation should have failed but succeeded.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "Vector Embedding Policy has invalid DataType" in e.http_error_message

        # Using too many dimensions
        vector_embedding_policy = {
            "vectorEmbeddings": [
                {
                    "path": "/vector1",
                    "dataType": "float32",
                    "dimensions": 2000,
                    "distanceFunction": "euclidean"
                }]}
        try:
            await self.created_database.create_container(
                id='vector_container',
                partition_key=PartitionKey(path="/id"),
                vector_embedding_policy=vector_embedding_policy
            )
            pytest.fail("Container creation should have failed but succeeded.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "Vector Embedding Policy has Dimensions:2000 which is more than max:1536" in e.http_error_message

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
            await self.created_database.create_container(
                id='vector_container',
                partition_key=PartitionKey(path="/id"),
                vector_embedding_policy=vector_embedding_policy
            )
            pytest.fail("Container creation should have failed but succeeded.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "Vector Embedding Policy has invalid Dimensions:-1, it should be positive integer" in e.http_error_message

        # Using invalid distance function
        vector_embedding_policy = {
            "vectorEmbeddings": [
                {
                    "path": "/vector1",
                    "dataType": "float32",
                    "dimensions": 1000,
                    "distanceFunction": "handMeasured"
                }]}
        try:
            await self.created_database.create_container(
                id='vector_container',
                partition_key=PartitionKey(path="/id"),
                vector_embedding_policy=vector_embedding_policy
            )
            pytest.fail("Container creation should have failed but succeeded.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "Vector Embedding Policy has invalid DistanceFunction:handMeasured" in e.http_error_message


if __name__ == '__main__':
    unittest.main()
