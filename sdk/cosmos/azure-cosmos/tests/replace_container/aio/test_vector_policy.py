# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Unchanged legacy policy-replacement methods with isolated Rust setup."""

import uuid
import pytest
from azure.cosmos import PartitionKey, exceptions
from azure.cosmos.aio import CosmosClient
from replace_container._container_setup import AsyncReplacementCase

@pytest.mark.cosmosSearchQuery
class TestVectorPolicyAsync(AsyncReplacementCase):
    def _create_key_client(self):
        return CosmosClient(self.host, self.key, _backend="rust")

    async def test_replace_vector_indexing_policy_async_rust(self):
        """A vector embedding policy and its vector indexes survive a replace.

        Replaces a container carrying a vector embedding policy and matching
        vector indexes, then reads it back and checks both came through
        unchanged.

        These two settings have to agree with each other, and they live in
        different parts of the container definition -- the embedding policy at
        the top level, the indexes inside the indexing policy. A replace that
        rebuilds one and not the other leaves vector search broken.
        """
        # Source: tests/test_vector_policy_async.py::TestVectorPolicyAsync.test_replace_vector_indexing_policy_async
        # Replace should work so long as the new indexing policy doesn't change the vector indexes, and as long as
        # the previously defined vector embedding policy is also provided.
        vector_embedding_policy = {
            "vectorEmbeddings": [
                {
                    "path": "/vector1",
                    "dataType": "float32",
                    "dimensions": 256,
                    "distanceFunction": "euclidean"
                }
            ]
        }
        indexing_policy = {
            "indexingMode": "consistent",
            "automatic": True,
            "includedPaths": [
                {
                    "path": "/*"
                }
            ],
            "excludedPaths": [
                {
                    "path": "/vector1/*"
                },
                {
                    "path": "/\"_etag\"/?"
                }
            ],
            "fullTextIndexes": [],
            "vectorIndexes": [
                {
                    "path": "/vector1",
                    "type": "diskANN",
                    "quantizerType": "product",
                    "quantizationByteSize": 128,
                    "indexingSearchListSize": 100
                }
            ]
        }
        container_id = "vector_container" + str(uuid.uuid4())
        created_container = await self.test_db.create_container(
            id=container_id,
            partition_key=PartitionKey(path="/id"),
            indexing_policy=indexing_policy,
            vector_embedding_policy=vector_embedding_policy
        )
        new_indexing_policy = {
            "indexingMode": "consistent",
            "automatic": True,
            "includedPaths": [
                {"path": "/color/?"},
                {"path": "/description/?"},
                {"path": "/cost/?"}
            ],
            "excludedPaths": [
                {"path": "/*"},
                {"path": "/vector1/*"},
                {"path": "/\"_etag\"/?"}
            ],
            "fullTextIndexes": [],
            "vectorIndexes": [
                {
                    "path": "/vector1",
                    "type": "diskANN",
                    "quantizerType": "product",
                    "quantizationByteSize": 128,
                    "indexingSearchListSize": 100
                }]
        }

        try:
            await self.test_db.replace_container(
                created_container,
                PartitionKey(path="/id"),
                vector_embedding_policy=vector_embedding_policy,
                indexing_policy=new_indexing_policy)
            properties = await created_container.read()
            assert properties["vectorEmbeddingPolicy"] == vector_embedding_policy
            assert properties["indexingPolicy"]["vectorIndexes"] == indexing_policy["vectorIndexes"]
        finally:
            await self.test_db.delete_container(container_id)

    async def test_fail_replace_vector_indexing_policy_async_rust(self):
        """Preserve the two original rejection checks for missing or changed embeddings."""
        # Source: tests/test_vector_policy_async.py::TestVectorPolicyAsync.test_fail_replace_vector_indexing_policy_async
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
        try:
            # don't provide vector embedding policy
            try:
                await self.test_db.replace_container(
                    created_container,
                    PartitionKey(path="/id"),
                    indexing_policy=indexing_policy)
                pytest.fail("Container replace should have failed for missing embedding policy.")
            except exceptions.CosmosHttpResponseError as e:
                assert e.status_code == 400
                assert ("The Vector Indexing Policy's path::/vector1 not matching in Embedding's path."
                        in e.http_error_message)
            # using a new vector embedding policy
            new_embedding_policy = {
                "vectorEmbeddings": [
                    {
                        "path": "/vector1",
                        "dataType": "float32",
                        "dimensions": 384,
                        "distanceFunction": "euclidean"}]}
            try:
                await self.test_db.replace_container(
                    created_container,
                    PartitionKey(path="/id"),
                    vector_embedding_policy=new_embedding_policy,
                    indexing_policy=indexing_policy)
                pytest.fail("Container replace should have failed for new embedding policy.")
            except exceptions.CosmosHttpResponseError as e:
                assert e.status_code == 400
                assert ("Paths in existing embedding policy cannot be modified in Collection Replace"
                        in e.http_error_message)
        finally:
            await self.test_db.delete_container(container_id)

    async def test_replace_vector_index_type_async_rust(self):
        # Source: tests/test_vector_policy_async.py::TestVectorPolicyAsync.test_replace_vector_index_type_async
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
        new_indexing_policy = {
            "vectorIndexes": [
                {"path": "/vector1", "type": "quantizedFlat"}]
        }
        container_id = "vector_container" + str(uuid.uuid4())
        created_container = await self.test_db.create_container(
            id=container_id,
            partition_key=PartitionKey(path="/id"),
            indexing_policy=indexing_policy,
            vector_embedding_policy=vector_embedding_policy
        )
        try:
            await self.test_db.replace_container(
                created_container,
                PartitionKey(path="/id"),
                vector_embedding_policy=vector_embedding_policy,
                indexing_policy=new_indexing_policy)

            properties = await created_container.read()
            assert properties["vectorEmbeddingPolicy"] == vector_embedding_policy
            actual_indexes = properties["indexingPolicy"]["vectorIndexes"]
            expected_indexes = new_indexing_policy["vectorIndexes"]
            assert len(actual_indexes) == len(expected_indexes)
            for actual_index, expected_index in zip(actual_indexes, expected_indexes):
                for key, value in expected_index.items():
                    assert actual_index[key] == value
        finally:
            await self.test_db.delete_container(container_id)
