# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Unchanged v4 policy-replacement methods with isolated Rust setup."""

import uuid
import pytest
from azure.cosmos import PartitionKey, exceptions
from azure.cosmos.aio import CosmosClient
from replace_container._legacy_setup import AsyncReplacementCase

class TestVectorPolicyAsync(AsyncReplacementCase):
    def _create_key_client(self):
        return CosmosClient(self.host, self.key, _backend="rust", read_timeout=30)

    async def test_replace_vector_indexing_policy_async(self):
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

    async def test_fail_replace_vector_indexing_policy_async(self):
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
            # using a new indexing policy
            new_indexing_policy = {
                "vectorIndexes": [
                    {"path": "/vector1", "type": "quantizedFlat"}]
            }
            try:
                await self.test_db.replace_container(
                    created_container,
                    PartitionKey(path="/id"),
                    vector_embedding_policy=vector_embedding_policy,
                    indexing_policy=new_indexing_policy)
                pytest.fail("Container replace should have failed for new indexing policy.")
            except exceptions.CosmosHttpResponseError as e:
                assert e.status_code == 400
                assert ("Paths in existing vector indexing policy cannot be modified in Collection Replace"
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
