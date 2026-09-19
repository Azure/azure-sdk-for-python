# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Unchanged legacy policy-replacement methods with isolated Rust setup."""

import uuid
import pytest
from azure.cosmos import PartitionKey, exceptions
from azure.cosmos import CosmosClient
from replace_container._legacy_setup import SyncReplacementCase

@pytest.mark.cosmosEmulator
class TestVectorPolicy(SyncReplacementCase):
    def _create_key_client(self):
        return CosmosClient(self.host, self.key, _backend="rust", read_timeout=30)

    def test_replace_vector_indexing_policy(self):
        """A vector embedding policy and its vector indexes survive a replace.

        Replaces a container carrying a vector embedding policy and matching
        vector indexes, then reads it back and checks both came through
        unchanged.

        These two settings have to agree with each other, and they live in
        different parts of the container definition -- the embedding policy at
        the top level, the indexes inside the indexing policy. A replace that
        rebuilds one and not the other leaves vector search broken.
        """
        # Source: tests/test_vector_policy.py::TestVectorPolicy.test_replace_vector_indexing_policy
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
        created_container = self.test_db.create_container(
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
            self.test_db.replace_container(
                created_container,
                PartitionKey(path="/id"),
                vector_embedding_policy=vector_embedding_policy,
                indexing_policy=new_indexing_policy)
            properties = created_container.read()
            assert properties["vectorEmbeddingPolicy"] == vector_embedding_policy
            assert properties["indexingPolicy"]["vectorIndexes"] == indexing_policy["vectorIndexes"]
        finally:
            self.test_db.delete_container(container_id)

    def test_fail_replace_vector_indexing_policy(self):
        """Three invalid vector replacements are each refused with their own message.

        First a vector index whose path does not match any path in the
        embedding policy. Then a replace that tries to change the paths of an
        existing vector index. Then one that tries to change the paths of the
        existing embedding policy.

        All three come back as 400s, and the test pins the wording of each,
        because the distinction between "these two do not agree" and "this
        cannot be changed after creation" is the only thing telling a customer
        whether to fix their input or recreate the container.
        """
        # Source: tests/test_vector_policy.py::TestVectorPolicy.test_fail_replace_vector_indexing_policy
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
        try:
            # don't provide vector embedding policy
            try:
                self.test_db.replace_container(
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
                self.test_db.replace_container(
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
                self.test_db.replace_container(
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
            self.test_db.delete_container(container_id)
