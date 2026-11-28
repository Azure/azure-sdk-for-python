# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Copied legacy container-listing assertions with _backend="rust".

This aio copy retains the source assertions and owns its setup database.
Method-level Source comments identify the originals. Cleanup is registered
for the owned resources, but service failures can still prevent deletion.

The write-payload-disabled and hierarchical-partition cases check a count
increase after creation and the listed id or partition key. These are not
exhaustive paging checks. Lazy results are consumed before assertions.
The standard listing/query lifecycle remains in query_containers.

Separate parity tests compare backends. This file runs its copied
assertions with a Rust-selected client only.
"""
import os
import unittest
import uuid

import pytest

import azure.cosmos.exceptions as exceptions
from azure.cosmos.aio import CosmosClient
from azure.cosmos.partition_key import PartitionKey


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


@pytest.mark.cosmosAADLong
@pytest.mark.cosmosLong
class TestCRUDContainerOperationsAsync(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        self.key_client = CosmosClient(HOST, KEY, _backend="rust")
        self.addAsyncCleanup(self.key_client.close)
        self._database_id = "list_containers_legacy_async_" + str(uuid.uuid4())
        self.addAsyncCleanup(self._delete_owned_database)
        self.database_for_test = await self.key_client.create_database(self._database_id)

    async def _delete_owned_database(self) -> None:
        try:
            await self.key_client.delete_database(self._database_id)
        except exceptions.CosmosResourceNotFoundError:
            pass

    async def test_collection_listing_with_write_payload_disabled_async_rust(self):
        """Disabling write payloads must not suppress listed container properties.

        Retain the original before/after listing assertion with its client setting.
        """
        # Source: tests/test_crud_response_payload_on_write_disabled_async.py::TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.test_collection_crud_async
        client = CosmosClient(HOST, KEY, _backend="rust", no_response_on_write=True)
        self.addAsyncCleanup(client.close)
        created_db = client.get_database_client(self._database_id)
        collections = [collection async for collection in created_db.list_containers()]
        before_create_collections_count = len(collections)
        collection_id = 'test_collection_crud ' + str(uuid.uuid4())
        await created_db.create_container(
            id=collection_id,
            indexing_policy={'indexingMode': 'consistent'},
            partition_key=PartitionKey(path="/pk", kind="Hash"),
        )

        collections = [collection async for collection in created_db.list_containers()]
        assert len(collections) == before_create_collections_count + 1
        assert collection_id in [collection["id"] for collection in collections]

    async def test_collection_listing_with_subpartitions_async_rust(self):
        """Retain the original listing count check for a two-level partition key.

        Creation-hook header assertions are separate from this listing check.
        """
        # Source: tests/test_crud_subpartition_async.py::TestSubpartitionCrudAsync.test_collection_crud_subpartition_async
        created_db = self.database_for_test
        collections = [collection async for collection in created_db.list_containers()]
        before_create_collections_count = len(collections)
        collection_id = 'test_collection_crud ' + str(uuid.uuid4())
        partition_key = PartitionKey(path=["/pk1", "/pk2"], kind="MultiHash")
        await created_db.create_container(
            id=collection_id,
            indexing_policy={'indexingMode': 'consistent'},
            partition_key=partition_key,
        )

        collections = [collection async for collection in created_db.list_containers()]
        assert len(collections) == before_create_collections_count + 1
        listed = {collection["id"]: collection for collection in collections}
        assert partition_key == listed[collection_id]["partitionKey"]


if __name__ == "__main__":
    unittest.main()
