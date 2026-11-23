# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Creation assertions copied from main e1c0306c77b2: test_vector_policy.py."""

import uuid
import pytest
from azure.cosmos import PartitionKey
from azure.cosmos import exceptions
from create_container._setup import SyncCreationCase


@pytest.mark.cosmosSearchQuery
class TestVectorPolicy(SyncCreationCase):

    def test_create_valid_vector_embedding_policy_rust(self):
        data_types = ["float32", "float16", "int8", "uint8"]
        for data_type in data_types:
            vector_embedding_policy = {
                "vectorEmbeddings": [
                    {
                        "path": "/vector1",
                        "dataType": data_type,
                        "dimensions": 256,
                        "distanceFunction": "euclidean",
                    }
                ]
            }
            container_id = "vector_container_" + data_type
            created_container = self.test_db.create_container(
                id=container_id,
                partition_key=PartitionKey(path="/id"),
                vector_embedding_policy=vector_embedding_policy,
            )
            try:
                properties = created_container.read()
                assert (
                    properties["vectorEmbeddingPolicy"]["vectorEmbeddings"][0][
                        "dataType"
                    ]
                    == data_type
                )
            finally:
                self.test_db.delete_container(container_id)

    def test_create_vector_embedding_container_rust(self):
        indexing_policy = {
            "vectorIndexes": [
                {"path": "/vector1", "type": "flat"},
                {
                    "path": "/vector2",
                    "type": "quantizedFlat",
                    "quantizerType": "product",
                    "quantizationByteSize": 8,
                },
                {
                    "path": "/vector3",
                    "type": "diskANN",
                    "quantizerType": "product",
                    "quantizationByteSize": 8,
                    "vectorIndexShardKey": ["/city"],
                    "indexingSearchListSize": 50,
                },
            ]
        }
        vector_embedding_policy = {
            "vectorEmbeddings": [
                {
                    "path": "/vector1",
                    "dataType": "float32",
                    "dimensions": 256,
                    "distanceFunction": "euclidean",
                },
                {
                    "path": "/vector2",
                    "dataType": "int8",
                    "dimensions": 200,
                    "distanceFunction": "dotproduct",
                },
                {
                    "path": "/vector3",
                    "dataType": "uint8",
                    "dimensions": 400,
                    "distanceFunction": "cosine",
                },
            ]
        }
        container_id = "vector_container" + str(uuid.uuid4())
        created_container = self.test_db.create_container(
            id=container_id,
            partition_key=PartitionKey(path="/id"),
            vector_embedding_policy=vector_embedding_policy,
            indexing_policy=indexing_policy,
        )
        try:
            properties = created_container.read()
            assert properties["vectorEmbeddingPolicy"] == vector_embedding_policy
            assert (
                properties["indexingPolicy"]["vectorIndexes"]
                == indexing_policy["vectorIndexes"]
            )
        finally:
            self.test_db.delete_container(container_id)
        indexing_policy = {
            "vectorIndexes": [
                {
                    "path": "/vector2",
                    "type": "diskANN",
                    "quantizerType": "product",
                    "quantizationByteSize": 64,
                    "indexingSearchListSize": 100,
                    "vectorIndexShardKey": ["/country/city"],
                }
            ]
        }
        container_id = "vector_container" + str(uuid.uuid4())
        created_container = self.test_db.create_container(
            id=container_id,
            partition_key=PartitionKey(path="/id"),
            indexing_policy=indexing_policy,
            vector_embedding_policy=vector_embedding_policy,
        )
        try:
            properties = created_container.read()
            assert properties["vectorEmbeddingPolicy"] == vector_embedding_policy
            assert (
                properties["indexingPolicy"]["vectorIndexes"]
                == indexing_policy["vectorIndexes"]
            )
        finally:
            self.test_db.delete_container(container_id)

    def test_fail_create_vector_indexing_policy_rust(self):
        vector_embedding_policy = {
            "vectorEmbeddings": [
                {
                    "path": "/vector1",
                    "dataType": "float32",
                    "dimensions": 256,
                    "distanceFunction": "euclidean",
                },
                {
                    "path": "/vector2",
                    "dataType": "int8",
                    "dimensions": 200,
                    "distanceFunction": "dotproduct",
                },
            ]
        }
        indexing_policy = {"vectorIndexes": [{"path": "/vector1", "type": "flat"}]}
        try:
            self.test_db.create_container(
                id="vector_container",
                partition_key=PartitionKey(path="/id"),
                indexing_policy=indexing_policy,
            )
            pytest.fail(
                "Container creation should have failed for lack of embedding policy."
            )
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "vector1 not matching in Embedding's path" in e.http_error_message
        indexing_policy = {"vectorIndexes": [{"path": "/vector1", "type": "notFlat"}]}
        try:
            self.test_db.create_container(
                id="vector_container",
                partition_key=PartitionKey(path="/id"),
                indexing_policy=indexing_policy,
                vector_embedding_policy=vector_embedding_policy,
            )
            pytest.fail("Container creation should have failed for wrong index type.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "Index Type::notFlat is invalid" in e.http_error_message
        indexing_policy = {"vectorIndexes": [{"path": "/vector3", "type": "flat"}]}
        try:
            self.test_db.create_container(
                id="vector_container",
                partition_key=PartitionKey(path="/id"),
                indexing_policy=indexing_policy,
                vector_embedding_policy=vector_embedding_policy,
            )
            pytest.fail("Container creation should have failed for index mismatch.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "vector3 not matching in Embedding's path" in e.http_error_message
        indexing_policy = {
            "vectorIndexes": [
                {"path": "/vector1", "type": "quantizedFlat", "quantizationByteSize": 0}
            ]
        }
        try:
            self.test_db.create_container(
                id="vector_container",
                partition_key=PartitionKey(path="/id"),
                indexing_policy=indexing_policy,
                vector_embedding_policy=vector_embedding_policy,
            )
            pytest.fail("Container creation should have failed for value mismatch.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert (
                "The Vector Indexing Policy parameter QuantizationByteSize value :: 0 is out of range. The allowed range is between 1 and 256."
                in e.http_error_message
            )
        indexing_policy = {
            "vectorIndexes": [
                {"path": "/vector1", "type": "diskANN", "indexingSearchListSize": 5}
            ]
        }
        try:
            self.test_db.create_container(
                id="vector_container",
                partition_key=PartitionKey(path="/id"),
                indexing_policy=indexing_policy,
                vector_embedding_policy=vector_embedding_policy,
            )
            pytest.fail("Container creation should have failed for value mismatch.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert (
                "IndexingSearchListSize value :: 5 is out of range. The allowed range is between 25 and 500."
                in e.http_error_message
            )
        indexing_policy = {
            "vectorIndexes": [
                {
                    "path": "/vector2",
                    "type": "diskANN",
                    "vectorIndexShardKey": ["country"],
                }
            ]
        }
        try:
            self.test_db.create_container(
                id="vector_container",
                partition_key=PartitionKey(path="/id"),
                indexing_policy=indexing_policy,
                vector_embedding_policy=vector_embedding_policy,
            )
            pytest.fail("Container creation should have failed for value mismatch.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert (
                "The Vector Indexing Policy has an invalid Shard Path: country."
                in e.http_error_message
            )
        indexing_policy = {
            "vectorIndexes": [
                {
                    "path": "/vector2",
                    "type": "diskANN",
                    "vectorIndexShardKey": ["/country", "/city", "/zipcode"],
                }
            ]
        }
        try:
            self.test_db.create_container(
                id="vector_container",
                partition_key=PartitionKey(path="/id"),
                indexing_policy=indexing_policy,
                vector_embedding_policy=vector_embedding_policy,
            )
            pytest.fail("Container creation should have failed for value mismatch.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert (
                "The number of shard paths defined in the Vector Indexing Policy: 3 exceeds the maximum: 1."
                in e.http_error_message
            )
        indexing_policy = {
            "vectorIndexes": [
                {
                    "path": "/vector2",
                    "type": "diskANN",
                    "vectorIndexShardKey": "/country",
                }
            ]
        }
        try:
            self.test_db.create_container(
                id="vector_container",
                partition_key=PartitionKey(path="/id"),
                indexing_policy=indexing_policy,
                vector_embedding_policy=vector_embedding_policy,
            )
            pytest.fail("Container creation should have failed for value mismatch.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "One of the specified inputs is invalid" in e.http_error_message
        vector_embedding_policy = {
            "vectorEmbeddings": [
                {
                    "path": "/vector1",
                    "dataType": "float32",
                    "dimensions": 550,
                    "distanceFunction": "euclidean",
                }
            ]
        }
        indexing_policy = {
            "vectorIndexes": [
                {
                    "path": "/vector1",
                    "type": "quantizedFlat",
                    "quantizationByteSize": 513,
                }
            ]
        }
        try:
            self.test_db.create_container(
                id="vector_container",
                partition_key=PartitionKey(path="/id"),
                indexing_policy=indexing_policy,
                vector_embedding_policy=vector_embedding_policy,
            )
            pytest.fail("Container creation should have failed for value mismatch.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert (
                "The Vector Indexing Policy parameter QuantizationByteSize value :: 513 is out of range."
                in e.http_error_message
            )

    def test_fail_create_vector_embedding_policy_rust(self):
        vector_embedding_policy = {
            "vectorEmbeddings": [
                {
                    "path": "/vector1",
                    "dataType": "float33",
                    "dimensions": 256,
                    "distanceFunction": "euclidean",
                }
            ]
        }
        try:
            self.test_db.create_container(
                id="vector_container",
                partition_key=PartitionKey(path="/id"),
                vector_embedding_policy=vector_embedding_policy,
            )
            pytest.fail("Container creation should have failed but succeeded.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert (
                "Vector Embedding Policy has an invalid DataType"
                in e.http_error_message
            )
        vector_embedding_policy = {
            "vectorEmbeddings": [
                {
                    "path": "/vector1",
                    "dataType": "float32",
                    "dimensions": 8000,
                    "distanceFunction": "euclidean",
                }
            ]
        }
        try:
            self.test_db.create_container(
                id="vector_container",
                partition_key=PartitionKey(path="/id"),
                vector_embedding_policy=vector_embedding_policy,
            )
            pytest.fail("Container creation should have failed but succeeded.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert (
                "Vector Embedding Policy has Dimensions:8000 which is more than the maximum supported value"
                in e.http_error_message
            )
        vector_embedding_policy = {
            "vectorEmbeddings": [
                {
                    "path": "/vector1",
                    "dataType": "float32",
                    "dimensions": -1,
                    "distanceFunction": "euclidean",
                }
            ]
        }
        try:
            self.test_db.create_container(
                id="vector_container",
                partition_key=PartitionKey(path="/id"),
                vector_embedding_policy=vector_embedding_policy,
            )
            pytest.fail("Container creation should have failed but succeeded.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert (
                "The Vector Embedding Policy has Dimensions:-1" in e.http_error_message
            )
        vector_embedding_policy = {
            "vectorEmbeddings": [
                {
                    "path": "/vector1",
                    "dataType": "float32",
                    "dimensions": 256,
                    "distanceFunction": "handMeasured",
                }
            ]
        }
        try:
            self.test_db.create_container(
                id="vector_container",
                partition_key=PartitionKey(path="/id"),
                vector_embedding_policy=vector_embedding_policy,
            )
            pytest.fail("Container creation should have failed but succeeded.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert (
                "The Vector Embedding Policy has an invalid DistanceFunction:handMeasured"
                in e.http_error_message
            )
