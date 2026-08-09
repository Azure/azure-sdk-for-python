# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""The existing v4 async container-query checks, re-run on the rust engine.

The async twin of ``query_containers/sync/legacy/test_crud_container.py``. See
that file for why this operation matters, why reading only
``DatabaseProxy.query_containers`` makes it look unmigrated when it is not, and
why the routing gate's non-dict branch is unreachable today.

Two things differ from the sync copy. The pager is drained with an async
comprehension rather than ``list()``, which matters here because the HTTP call
happens on drain, not when the method returns. And the async surface spells the
query as separate ``query=`` and ``parameters=`` keywords, where the sync
surface takes a single dict positionally -- both spellings have to route to
rust, and this copy covers the keyword one.

The file name deliberately drops the ``_async`` suffix the source carries. The
parity reporter pairs a legacy copy to its original on the file name with any
trailing ``_async`` stripped, and decides sync-vs-async from the ``/aio/`` path
segment. The class and method names keep their ``_async`` suffix, matching the
source exactly.

Run with::

    pytest --noconftest tests/query_containers/aio/legacy/test_crud_container.py -v
"""
import os
import unittest
import uuid

import pytest

import azure.cosmos.exceptions as exceptions
from azure.cosmos.aio import CosmosClient
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
        self._database_id = "query_containers_legacy_async_" + str(uuid.uuid4())
        self.database_for_test = await self.key_client.create_database(self._database_id)

    async def asyncTearDown(self) -> None:
        try:
            await self.key_client.delete_database(self._database_id)
        except Exception:  # pylint: disable=broad-except
            pass
        await self.key_client.close()

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


if __name__ == "__main__":
    unittest.main()
