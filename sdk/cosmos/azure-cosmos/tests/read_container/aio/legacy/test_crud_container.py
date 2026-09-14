# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""The existing v4 async container-read checks, re-run on the rust engine.

Why this file exists: the async client is a separate code path from the sync
client, so it has to be proved separately. ``ContainerProxy.read`` returns the
container's stored settings -- its id, its partition key, its indexing policy,
and on request its storage usage. If rust returned a different partition key
path on the async path only, async applications would break while sync ones
kept working.

What it does: three original v4 tests copied from
``tests/test_crud_container_async.py``, changed in one place -- the client is
built with ``_backend="rust"``. ``test_collection_crud_async`` creates a
container, reads it back and checks the indexing mode and partition key
survived the round trip. ``test_partitioned_collection_async`` checks the
partition key on a container created with throughput.

``test_partitioned_collection_quota_async`` also verifies partition statistics
and quota usage through Rust. Every container read is guarded by a binding-operation
counter and a zero-fallback assertion.

This is NOT the side-by-side comparison. The comparison tests
(``read_container/aio/test_read_container_parity_async.py``) run the same call
on both engines and diff the results. This file runs on rust only and reuses
assertions the team already trusts.

Self-contained: it creates and deletes its own database, so it shares no state
with any other test. The originals read a shared container named by
``test_config.TestConfig``; this copy creates that container itself. The class
name and method names match the source, so the two test IDs differ only by
path. The file name drops the ``_async`` suffix because the audit reporter
pairs sync and async copies by stripping it.

Run with::

    pytest --noconftest tests/read_container/aio/legacy/test_crud_container.py -v
"""
import os
import unittest
import uuid
from functools import wraps
from types import SimpleNamespace
from unittest.mock import patch

import pytest

import azure.cosmos.documents as documents
import azure.cosmos.exceptions as exceptions
from azure.cosmos.aio import CosmosClient, ContainerProxy
from common._parity_helpers import run_target_operation_async
from azure.cosmos.http_constants import StatusCodes
from azure.cosmos.partition_key import PartitionKey


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


@pytest.mark.cosmosEmulator
class TestCRUDContainerOperationsAsync(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        self.key_client = CosmosClient(HOST, KEY, _backend="rust")
        self.addAsyncCleanup(self.key_client.close)
        self._database_id = "read_container_legacy_async_" + str(uuid.uuid4())
        self.addAsyncCleanup(self._delete_owned_database)
        self.database_for_test = await self.key_client.create_database(self._database_id)
        self.configs = SimpleNamespace(TEST_MULTI_PARTITION_CONTAINER_ID="quota_target")
        if self._testMethodName == "test_partitioned_collection_quota_async":
            await self.database_for_test.create_container(
                self.configs.TEST_MULTI_PARTITION_CONTAINER_ID,
                PartitionKey(path="/id"), offer_throughput=10100,
            )
        original_read = ContainerProxy.read

        @wraps(original_read)
        async def guarded_read(container, *args, **kwargs):
            return await run_target_operation_async(
                self.key_client, lambda: original_read(container, *args, **kwargs)
            )

        read_patch = patch.object(ContainerProxy, "read", guarded_read)
        read_patch.start()
        self.addCleanup(read_patch.stop)

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

    async def test_collection_crud_async(self):
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

    async def test_partitioned_collection_async(self):
        # Source: tests/test_crud_container_async.py::TestCRUDContainerOperationsAsync.test_partitioned_collection_async
        created_db = self.database_for_test

        collection_definition = {'id': 'test_partitioned_collection ' + str(uuid.uuid4()),
                                 'partitionKey':
                                     {
                                         'paths': ['/id'],
                                         'kind': documents.PartitionKind.Hash
                                     }
                                 }

        offer_throughput = 10100
        created_collection = await created_db.create_container(id=collection_definition['id'],
                                                               partition_key=collection_definition['partitionKey'],
                                                               offer_throughput=offer_throughput)

        assert collection_definition.get('id') == created_collection.id

        created_collection_properties = await created_collection.read()
        assert collection_definition.get('partitionKey').get('paths')[0] == \
               created_collection_properties['partitionKey']['paths'][0]
        assert collection_definition.get('partitionKey').get('kind') == created_collection_properties['partitionKey'][
            'kind']

        expected_offer = await created_collection.get_throughput()

        assert expected_offer is not None

        assert expected_offer.offer_throughput == offer_throughput

        await created_db.delete_container(created_collection.id)


    async def test_partitioned_collection_quota_async(self):
        # Source: tests/test_crud_container_async.py::TestCRUDContainerOperationsAsync.test_partitioned_collection_quota_async
        created_db = self.database_for_test

        created_collection = self.database_for_test.get_container_client(
            self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        retrieved_collection_properties = await created_collection.read(
            populate_partition_key_range_statistics=True,
            populate_quota_info=True)
        assert retrieved_collection_properties.get("statistics") is not None
        assert created_db.client_connection.last_response_headers.get("x-ms-resource-usage") is not None


if __name__ == "__main__":
    unittest.main()
