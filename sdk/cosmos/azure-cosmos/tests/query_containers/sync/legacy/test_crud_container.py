# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""The existing v4 container-query checks, re-run on the rust engine.

Why this file exists: ``DatabaseProxy.query_containers`` is how an application
finds containers matching a condition rather than fetching all of them. A
management tool looking up one container by id, or filtering on a naming
convention, goes through here. If rust returned no rows for a query that
matches, the caller concludes the container does not exist and may recreate it.

What it does: one real v4 test copied from ``tests/test_crud_container.py``,
changed in one place -- the client is built with ``_backend="rust"``.
``test_collection_crud`` queries for the container it just created by id and
asserts the result is non-empty.

Two things worth knowing about how this operation routes:

First, ``DatabaseProxy.query_containers`` calls ``QueryContainers`` with no
visible backend branch; the routing happens further down, inside
``__QueryFeed``'s ``ResourceType.Collection`` branch. Reading only the public
method suggests this operation was never migrated; it was.

Second, a query reaches rust as a dict. A caller may pass a bare string, which
``__CheckAndUnifyQueryFormat`` normalizes to ``{"query": ...}`` before the
routing gate sees it, so that spelling routes to rust too. The gate's branch
rejecting a non-dict payload targets the ``SqlQuery`` compatibility mode, which
is unreachable today because ``__CheckAndUnifyQueryFormat`` raises for every
input in that mode. This copy uses the dict form, matching the source test.

This is NOT the side-by-side comparison. The comparison tests
(``query_containers/sync/test_query_containers_parity.py``) run the same call on
both engines and diff the results. This file runs on rust only and reuses
assertions the team already trusts.

Self-contained: it creates and deletes its own database, so it shares no state
with any other test. The class name and method names match the source, so the
two test IDs differ only by path.

Run with::

    pytest --noconftest tests/query_containers/sync/legacy/test_crud_container.py -v
"""
import os
import unittest
import uuid

import pytest

import azure.cosmos.exceptions as exceptions
from azure.cosmos import CosmosClient
from azure.cosmos.http_constants import StatusCodes
from azure.cosmos.partition_key import PartitionKey


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


@pytest.mark.cosmosEmulator
class TestCRUDContainerOperations(unittest.TestCase):

    def setUp(self) -> None:
        self.key_client = CosmosClient(HOST, KEY, _backend="rust")
        self._database_id = "query_containers_legacy_" + str(uuid.uuid4())
        self.databaseForTest = self.key_client.create_database(self._database_id)

    def tearDown(self) -> None:
        try:
            self.key_client.delete_database(self._database_id)
        except Exception:  # pylint: disable=broad-except
            pass
        self.key_client.close()

    def __AssertHTTPFailureWithStatus(self, status_code, func, *args, **kwargs):
        try:
            func(*args, **kwargs)
            self.assertFalse(True, 'function should fail.')
        except exceptions.CosmosHttpResponseError as inst:
            self.assertEqual(inst.status_code, status_code)

    def test_collection_crud(self):
        # Source: tests/test_crud_container.py::TestCRUDContainerOperations.test_collection_crud
        created_db = self.databaseForTest
        collections = list(created_db.list_containers())
        # create a collection
        before_create_collections_count = len(collections)
        collection_id = 'test_collection_crud ' + str(uuid.uuid4())
        collection_indexing_policy = {'indexingMode': 'consistent'}
        created_collection = created_db.create_container(id=collection_id,
                                                         indexing_policy=collection_indexing_policy,
                                                         partition_key=PartitionKey(path="/pk", kind="Hash"))
        self.assertEqual(collection_id, created_collection.id)

        created_properties = created_collection.read()
        self.assertEqual('consistent', created_properties['indexingPolicy']['indexingMode'])
        self.assertDictEqual(PartitionKey(path='/pk', kind='Hash'), created_properties['partitionKey'])

        # read collections after creation
        collections = list(created_db.list_containers())
        self.assertEqual(len(collections),
                         before_create_collections_count + 1,
                         'create should increase the number of collections')
        # query collections
        collections = list(created_db.query_containers(
            {
                'query': 'SELECT * FROM root r WHERE r.id=@id',
                'parameters': [
                    {'name': '@id', 'value': collection_id}
                ]
            }))

        self.assertTrue(collections)
        # delete collection
        created_db.delete_container(created_collection.id)
        # read collection after deletion
        created_container = created_db.get_container_client(created_collection.id)
        self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND,
                                           created_container.read)


if __name__ == "__main__":
    unittest.main()
