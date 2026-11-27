# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Copied legacy container lifecycle assertions with _backend="rust".

This aio copy retains the source assertions and owns its setup database.
Method-level Source comments identify the originals. Cleanup is registered
for the owned resources, but service failures can still prevent deletion.

The listing assertion checks a count increase after creation; the filtered
query assertion checks that results are nonempty. Neither is exhaustive
paging coverage or proof of each internal routing step. Lazy results are
consumed before assertions.

Separate parity tests compare backends. This file runs its copied
assertions with a Rust-selected client only.
"""
import os
import unittest
import uuid
from typing import Mapping

import pytest

import azure.cosmos.exceptions as exceptions
from azure.cosmos.aio import CosmosClient
from azure.cosmos.diagnostics import RecordDiagnostics  # pylint: disable=no-name-in-module
from azure.cosmos.http_constants import StatusCodes
from azure.cosmos.partition_key import PartitionKey
from common._rust_checks import run_on_rust_async


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
        self._database_id = "query_containers_legacy_async_" + str(uuid.uuid4())
        self.addAsyncCleanup(self._delete_owned_database)
        self.database_for_test = await self.key_client.create_database(self._database_id)

    async def _delete_owned_database(self) -> None:
        try:
            await self.key_client.delete_database(self._database_id)
        except exceptions.CosmosResourceNotFoundError:
            pass

    async def __assert_http_failure_with_status(self, status_code, func, *args, **kwargs):
        try:
            await func(*args, **kwargs)
            self.fail('function should fail.')
        except exceptions.CosmosHttpResponseError as inst:
            assert inst.status_code == status_code

    async def test_collection_crud_async_rust(self):
        """Container creation updates listing counts and yields a nonempty id-filtered query.

        This full legacy lifecycle checks the listing count before and after
        creation, reads the stored settings, queries by id, and verifies a 404
        when reading after deletion. It retains the listing checks formerly
        repeated in the async list_containers copy.

        The read_container copy keeps the same scenario with separate setup
        that guards container reads against legacy fallback and requires Rust
        binding execution.
        """
        # Source: tests/test_crud_container_async.py::TestCRUDContainerOperationsAsync.test_collection_crud_async
        created_db = self.database_for_test
        collections = [collection async for collection in created_db.list_containers()]
        # create a collection
        before_create_collections_count = len(collections)
        collection_id = 'test_collection_crud ' + str(uuid.uuid4())
        collection_indexing_policy = {'indexingMode': 'consistent'}
        created_collection = await created_db.create_container(id=collection_id,
                                                               indexing_policy=collection_indexing_policy,
                                                               partition_key=PartitionKey(path="/pk", kind="Hash"))
        assert collection_id == created_collection.id

        created_properties = await created_collection.read()
        assert 'consistent' == created_properties['indexingPolicy']['indexingMode']
        assert PartitionKey(path='/pk', kind='Hash') == created_properties['partitionKey']

        # read collections after creation
        collections = [collection async for collection in created_db.list_containers()]
        assert len(collections) == before_create_collections_count + 1
        # query collections
        collections = [collection async for collection in created_db.query_containers(

            query='SELECT * FROM root r WHERE r.id=@id',
            parameters=[
                {'name': '@id', 'value': collection_id}
            ]
        )]

        assert len(collections) > 0
        # delete collection
        await created_db.delete_container(created_collection.id)
        # read collection after deletion
        created_container = created_db.get_container_client(created_collection.id)
        await self.__assert_http_failure_with_status(StatusCodes.NOT_FOUND,
                                                     created_container.read)

    async def test_collection_crud_with_write_payload_disabled_async_rust(self):
        """Disabling write response bodies must not suppress queried container properties."""
        # Source: tests/test_crud_response_payload_on_write_disabled_async.py::TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.test_collection_crud_async
        client = CosmosClient(HOST, KEY, _backend="rust", no_response_on_write=True)
        self.addAsyncCleanup(client.close)
        await client.__aenter__()
        created_db = client.get_database_client(self._database_id)
        collections = [collection async for collection in created_db.list_containers()]
        before_create_collections_count = len(collections)
        collection_id = 'test_collection_crud ' + str(uuid.uuid4())
        partition_key = PartitionKey(path="/pk", kind="Hash")
        created_collection = await created_db.create_container(
            id=collection_id,
            indexing_policy={'indexingMode': 'consistent'},
            partition_key=partition_key,
        )
        assert collection_id == created_collection.id

        created_properties = await created_collection.read()
        assert 'consistent' == created_properties['indexingPolicy']['indexingMode']
        assert partition_key == created_properties['partitionKey']
        collections = [collection async for collection in created_db.list_containers()]
        assert len(collections) == before_create_collections_count + 1

        async def query():
            return [collection async for collection in created_db.query_containers(
                query='SELECT * FROM root r WHERE r.id=@id',
                parameters=[{'name': '@id', 'value': collection_id}],
            )]

        collections = await run_on_rust_async(client, query)
        assert len(collections) > 0
        assert [collection['id'] for collection in collections] == [collection_id]
        assert partition_key == collections[0]['partitionKey']

        await created_db.delete_container(created_collection.id)
        created_container = created_db.get_container_client(created_collection.id)
        await self.__assert_http_failure_with_status(StatusCodes.NOT_FOUND, created_container.read)

    async def test_collection_crud_subpartition_async_rust(self):
        """Query a hierarchical container without requiring an excluded creation header.

        Gap 12 accepts the missing generic success-header map. Retain the other
        original lifecycle checks and verify the query returns this container.
        """
        # Source: tests/test_crud_subpartition_async.py::TestSubpartitionCrudAsync.test_collection_crud_subpartition_async
        created_db = self.database_for_test
        collections = [collection async for collection in created_db.list_containers()]
        before_create_collections_count = len(collections)
        collection_id = 'test_collection_crud ' + str(uuid.uuid4())
        partition_key = PartitionKey(path=["/pk1", "/pk2"], kind="MultiHash")
        created_recorder = RecordDiagnostics()
        created_collection = await created_db.create_container(
            id=collection_id,
            indexing_policy={'indexingMode': 'consistent'},
            partition_key=partition_key,
            response_hook=created_recorder,
        )
        assert collection_id == created_collection.id
        assert isinstance(created_recorder.headers, Mapping)
        # Gap 12: Content-Type is not required in the modeled success headers.
        assert isinstance(created_recorder.body, Mapping)
        assert 'id' in created_recorder.body

        created_properties = await created_collection.read()
        assert 'consistent' == created_properties['indexingPolicy']['indexingMode']
        collections = [collection async for collection in created_db.list_containers()]
        assert len(collections) == before_create_collections_count + 1

        async def query():
            return [collection async for collection in created_db.query_containers(
                query='SELECT * FROM root r WHERE r.id=@id',
                parameters=[{'name': '@id', 'value': collection_id}],
            )]

        collections = await run_on_rust_async(self.key_client, query)
        assert collections is not None
        assert [collection['id'] for collection in collections] == [collection_id]
        assert partition_key == collections[0]['partitionKey']

        await created_db.delete_container(created_collection.id)
        created_container = created_db.get_container_client(created_collection.id)
        await self.__assert_http_failure_with_status(StatusCodes.NOT_FOUND, created_container.read)

        recreated_partition_key = PartitionKey(path=["/id1", "/id2", "/id3"], kind="MultiHash")
        container_proxy = await created_db.create_container(
            id=created_collection.id, partition_key=recreated_partition_key,
        )
        assert created_collection.id == container_proxy.id
        container_proxy_properties = await container_proxy._get_properties()
        assert recreated_partition_key == container_proxy_properties['partitionKey']
        await created_db.delete_container(created_collection.id)


if __name__ == "__main__":
    unittest.main()
