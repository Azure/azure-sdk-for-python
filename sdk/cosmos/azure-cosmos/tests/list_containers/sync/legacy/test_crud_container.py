# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Copied legacy container lifecycle assertions with _backend="rust".

This sync copy retains the source assertions and owns its setup database.
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
        self.addCleanup(self.key_client.close)
        self._database_id = "list_containers_legacy_" + str(uuid.uuid4())
        self.addCleanup(self._delete_owned_database)
        self.databaseForTest = self.key_client.create_database(self._database_id)

    def _delete_owned_database(self) -> None:
        try:
            self.key_client.delete_database(self._database_id)
        except exceptions.CosmosResourceNotFoundError:
            pass

    def __AssertHTTPFailureWithStatus(self, status_code, func, *args, **kwargs):
        try:
            func(*args, **kwargs)
            self.assertFalse(True, 'function should fail.')
        except exceptions.CosmosHttpResponseError as inst:
            self.assertEqual(inst.status_code, status_code)

    def test_collection_crud(self):
        """Container listing stays accurate across a create and a delete.

        The full legacy lifecycle test, kept here for the listing half. It
        counts containers, creates one, counts again and expects exactly one
        more, then deletes it and confirms the container is really gone by
        reading it and getting a 404.

        The count comparison is the point: a listing that caches, pages badly,
        or silently truncates would still return a plausible-looking list, and
        only counting before and against after catches it.

        The same legacy test is also copied into ``query_containers`` and
        ``read_container``, each pinning the part of it they own.
        """
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
