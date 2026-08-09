# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""The existing v4 async default-indexing-policy check, re-run on the rust engine.

Why this file exists: the async client is a separate code path from the sync
client, so it has to be proved separately. When a customer creates a container
without spelling out a full indexing policy, the service fills in the rest. The
filled-in policy decides which fields can be used in a query without a scan, so
it decides what the customer's queries cost. If rust sent a partly-specified
policy differently on the async path only, async applications would end up with
containers indexed differently from sync ones.

What it does: the real v4 test copied from
``tests/test_crud_container_async.py``, changed in one place -- the client is
built with ``_backend="rust"``. It creates containers with four different
partly-specified policies and checks the service filled each one in the same
way. The helper it calls, ``_check_default_indexing_policy_paths``, is copied
with it because the test cannot run without it.

This is NOT the side-by-side comparison. The comparison tests
(``create_container/aio/test_create_container_parity_async.py``) run the same
call on both engines and diff the results. This file runs on rust only and
reuses assertions the team already trusts.

Self-contained: it creates and deletes its own database, so it shares no state
with any other test. The original's first leg reads a shared container named by
``test_config.TestConfig``; this copy creates that container itself with no
indexing policy given, which is the case the leg is testing. The class name and
method name match the source, so the two test IDs differ only by path. The file
name drops the ``_async`` suffix because the audit reporter pairs sync and
async copies by stripping it.

Run with::

    pytest --noconftest tests/create_container/aio/legacy/test_crud_container.py -v
"""
import os
import unittest
import uuid

import pytest

import azure.cosmos.documents as documents
from azure.cosmos.aio import CosmosClient
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
        self._database_id = "create_container_legacy_async_" + str(uuid.uuid4())
        self.database_for_test = await self.key_client.create_database(self._database_id)
        # The original test's first leg reads a container that already exists
        # and was created with no indexing policy. This copy has to make that
        # container itself. It is created through the low-level client
        # connection rather than DatabaseProxy.create_container so that this
        # scaffolding does not add an extra call to the sequence the parity
        # audit records for the operation under test.
        self._default_policy_container_id = "default_policy_" + uuid.uuid4().hex[:8]
        await self.database_for_test.client_connection.CreateContainer(
            "dbs/" + self._database_id,
            {
                "id": self._default_policy_container_id,
                "partitionKey": {"paths": ["/id"], "kind": "Hash"},
            },
        )

    async def asyncTearDown(self) -> None:
        try:
            await self.key_client.delete_database(self._database_id)
        except Exception:  # pylint: disable=broad-except
            pass
        await self.key_client.close()

    async def _check_default_indexing_policy_paths(self, indexing_policy):
        # Source: tests/test_crud_container_async.py::TestCRUDContainerOperationsAsync._check_default_indexing_policy_paths
        def __get_first(array):
            if array:
                return array[0]
            else:
                return None

        # '/_etag' is present in excluded paths by default
        assert len(indexing_policy['excludedPaths']) == 1
        # included paths should be 1: '/'.
        assert len(indexing_policy['includedPaths']) == 1

        root_included_path = __get_first([included_path for included_path in indexing_policy['includedPaths']
                                          if included_path['path'] == '/*'])
        assert not root_included_path.get('indexes')

    async def test_create_default_indexing_policy_async(self):
        # Source: tests/test_crud_container_async.py::TestCRUDContainerOperationsAsync.test_create_default_indexing_policy_async
        db = self.database_for_test

        # no indexing policy specified
        collection = db.get_container_client(self._default_policy_container_id)
        collection_properties = await collection.read()
        await self._check_default_indexing_policy_paths(collection_properties['indexingPolicy'])

        # partial policy specified
        collection = await db.create_container(
            id='test_create_default_indexing_policy TestCreateDefaultPolicy01' + str(uuid.uuid4()),
            indexing_policy={
                'indexingMode': documents.IndexingMode.Consistent, 'automatic': True
            },
            partition_key=PartitionKey(path='/id', kind='Hash')
        )
        collection_properties = await collection.read()
        await self._check_default_indexing_policy_paths(collection_properties['indexingPolicy'])
        await db.delete_container(container=collection)

        # default policy
        collection = await db.create_container(
            id='test_create_default_indexing_policy TestCreateDefaultPolicy03' + str(uuid.uuid4()),
            indexing_policy={},
            partition_key=PartitionKey(path='/id', kind='Hash')
        )
        collection_properties = await collection.read()
        await self._check_default_indexing_policy_paths(collection_properties['indexingPolicy'])
        await db.delete_container(container=collection)

        # missing indexes
        collection = await db.create_container(
            id='test_create_default_indexing_policy TestCreateDefaultPolicy04' + str(uuid.uuid4()),
            indexing_policy={
                'includedPaths': [
                    {
                        'path': '/*'
                    }
                ]
            },
            partition_key=PartitionKey(path='/id', kind='Hash')
        )
        collection_properties = await collection.read()
        await self._check_default_indexing_policy_paths(collection_properties['indexingPolicy'])
        await db.delete_container(container=collection)

        # missing precision
        collection = await db.create_container(
            id='test_create_default_indexing_policy TestCreateDefaultPolicy05' + str(uuid.uuid4()),
            indexing_policy={
                'includedPaths': [
                    {
                        'path': '/*',
                        'indexes': [
                            {
                                'kind': documents.IndexKind.Hash,
                                'dataType': documents.DataType.String
                            },
                            {
                                'kind': documents.IndexKind.Range,
                                'dataType': documents.DataType.Number
                            }
                        ]
                    }
                ]
            },
            partition_key=PartitionKey(path='/id', kind='Hash')
        )
        collection_properties = await collection.read()
        await self._check_default_indexing_policy_paths(collection_properties['indexingPolicy'])
        await db.delete_container(container=collection)


if __name__ == "__main__":
    unittest.main()
