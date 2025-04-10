# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid

import pytest

import azure.cosmos.exceptions as exceptions
import test_config
from azure.cosmos import CosmosClient, PartitionKey


@pytest.mark.cosmosSearchQuery
class TestVectorPolicy(unittest.TestCase):
    client: CosmosClient = None
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

        cls.client = CosmosClient(cls.host, cls.masterKey)
        cls.created_database = cls.client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)
        cls.test_db = cls.client.create_database(str(uuid.uuid4()))

    @classmethod
    def tearDownClass(cls):
        test_config.TestConfig.try_delete_database_with_id(cls.client, cls.test_db.id)

    def test_create_vector_embedding_container(self):
        indexing_policy = {
            "vectorIndexes": [
                {"path": "/vector1", "type": "flat"},
                {"path": "/vector2", "type": "quantizedFlat", "quantizationByteSize": 8},
                {"path": "/vector3", "type": "diskANN", "quantizationByteSize": 8, "vectorIndexShardKey": ["/city"], "indexingSearchListSize": 50}
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
        created_container = self.test_db.create_container(
            id=container_id,
            partition_key=PartitionKey(path="/id"),
            vector_embedding_policy=vector_embedding_policy,
            indexing_policy=indexing_policy
        )
        properties = created_container.read()
        assert properties["vectorEmbeddingPolicy"] == vector_embedding_policy
        assert properties["indexingPolicy"]["vectorIndexes"] == indexing_policy["vectorIndexes"]
        self.test_db.delete_container(container_id)

        # Pass a vector indexing policy with hierarchical vectorIndexShardKey value
        indexing_policy = {
            "vectorIndexes": [
                {"path": "/vector2", "type": "diskANN", 'quantizationByteSize': 64, 'indexingSearchListSize': 100, "vectorIndexShardKey": ["/country/city"]}]
        }
        container_id = "vector_container" + str(uuid.uuid4())
        created_container = self.test_db.create_container(
            id=container_id,
            partition_key=PartitionKey(path="/id"),
            indexing_policy=indexing_policy,
            vector_embedding_policy=vector_embedding_policy
        )
        properties = created_container.read()
        assert properties["vectorEmbeddingPolicy"] == vector_embedding_policy
        assert properties["indexingPolicy"]["vectorIndexes"] == indexing_policy["vectorIndexes"]
        self.test_db.delete_container(container_id)

    def test_fail_create_vector_indexing_policy(self):
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
            self.test_db.create_container(
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
            self.test_db.create_container(
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
            self.test_db.create_container(
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
            self.test_db.create_container(
                id='vector_container',
                partition_key=PartitionKey(path="/id"),
                indexing_policy=indexing_policy,
                vector_embedding_policy=vector_embedding_policy
            )
            pytest.fail("Container creation should have failed for value mismatch.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "The Vector Indexing Policy parameter QuantizationByteSize value :: 0 is out of range. The allowed range is between 1 and 256."\
                   in e.http_error_message

        # Pass a vector indexing policy with wrong indexingSearchListSize value
        indexing_policy = {
            "vectorIndexes": [
                {"path": "/vector1", "type": "diskANN", "indexingSearchListSize": 5}]
        }
        try:
            self.test_db.create_container(
                id='vector_container',
                partition_key=PartitionKey(path="/id"),
                indexing_policy=indexing_policy,
                vector_embedding_policy=vector_embedding_policy
            )
            pytest.fail("Container creation should have failed for value mismatch.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "IndexingSearchListSize value :: 5 is out of range. The allowed range is between 25 and 500."\
                   in e.http_error_message

        # Pass a vector indexing policy with wrong vectorIndexShardKey value
        indexing_policy = {
            "vectorIndexes": [
                {"path": "/vector2", "type": "diskANN", "vectorIndexShardKey": ["country"]}]
        }
        try:
            self.test_db.create_container(
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
            self.test_db.create_container(
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

        # Pass a vector indexing policy with an invalid type for vectorIndexShardKey
        indexing_policy = {
            "vectorIndexes": [
                {"path": "/vector2", "type": "diskANN", "vectorIndexShardKey": "/country"}]
        }
        try:
            self.test_db.create_container(
                id='vector_container',
                partition_key=PartitionKey(path="/id"),
                indexing_policy=indexing_policy,
                vector_embedding_policy=vector_embedding_policy
            )
            pytest.fail("Container creation should have failed for value mismatch.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "One of the specified inputs is invalid" \
                   in e.http_error_message

        # Pass a vector indexing policy with dimensions above 512 to test the max range of  "quantizationByteSize"
        vector_embedding_policy = {
            "vectorEmbeddings": [
                {
                    "path": "/vector1",
                    "dataType": "float32",
                    "dimensions": 550,
                    "distanceFunction": "euclidean"
                }]}
        indexing_policy = {
            "vectorIndexes": [
                {"path": "/vector1", "type": "quantizedFlat", "quantizationByteSize": 513 }]
        }
        try:
            self.test_db.create_container(
                id='vector_container',
                partition_key=PartitionKey(path="/id"),
                indexing_policy=indexing_policy,
                vector_embedding_policy=vector_embedding_policy
            )
            pytest.fail("Container creation should have failed for value mismatch.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "The Vector Indexing Policy parameter QuantizationByteSize value :: 513 is out of range." \
                   in e.http_error_message

    def test_fail_replace_vector_indexing_policy(self):
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
        created_container = self.test_db.create_container(
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
            self.test_db.replace_container(
                created_container,
                PartitionKey(path="/id"),
                indexing_policy=new_indexing_policy)
            pytest.fail("Container replace should have failed for indexing policy.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert ("The Vector Indexing Policy's path::/vector1 not matching in Embedding's path."
                    in e.http_error_message)
        self.test_db.delete_container(container_id)

    def test_fail_create_vector_embedding_policy(self):
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
            self.test_db.create_container(
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
            self.test_db.create_container(
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
            self.test_db.create_container(
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
            self.test_db.create_container(
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
