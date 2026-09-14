# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""The existing v4 container-read checks, re-run on the rust engine.

Why this file exists: ``ContainerProxy.read`` returns the container's stored
settings -- its id, its partition key, its indexing policy, and on request its
storage usage. Customers read those settings to decide how to query the
container and how much it costs them. If rust returned a different partition
key path or dropped the indexing policy, application code that branches on
those fields would take the wrong branch.

What it does: original v4 tests copied from ``tests/test_crud_container.py``,
changed in one place -- the client is built with ``_backend="rust"``.
``test_collection_crud`` creates a container, reads it back and checks the
indexing mode and partition key survived the round trip.

``test_partitioned_collection`` also verifies partition statistics and quota
usage through Rust. Every container read is guarded by a binding-operation
counter and a zero-fallback assertion.

This is NOT the side-by-side comparison. The comparison tests
(``read_container/sync/test_read_container_parity.py``) run the same call on
both engines and diff the results. This file runs on rust only and reuses
assertions the team already trusts.

Self-contained: it creates and deletes its own database, so it shares no state
with any other test. The originals read a shared container named by
``test_config.TestConfig``; this copy creates that container itself. The class
name and method names match the source, so the two test IDs differ only by
path.

Run with::

    pytest --noconftest tests/read_container/sync/legacy/test_crud_container.py -v
"""
import os
import unittest
import uuid
from functools import wraps
from unittest.mock import patch

import pytest

import azure.cosmos.exceptions as exceptions
import azure.cosmos.documents as documents
from azure.cosmos import CosmosClient, ContainerProxy
from common._parity_helpers import run_target_operation
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
        self._database_id = "read_container_legacy_" + str(uuid.uuid4())
        self.addCleanup(self._delete_owned_database)
        self.databaseForTest = self.key_client.create_database(self._database_id)
        original_read = ContainerProxy.read

        @wraps(original_read)
        def guarded_read(container, *args, **kwargs):
            return run_target_operation(self.key_client, lambda: original_read(container, *args, **kwargs))

        read_patch = patch.object(ContainerProxy, "read", guarded_read)
        read_patch.start()
        self.addCleanup(read_patch.stop)

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


    def test_partitioned_collection(self):
        # Source: tests/test_crud_container.py::TestCRUDContainerOperations.test_partitioned_collection
        created_db = self.databaseForTest

        collection_definition = {'id': 'test_partitioned_collection ' + str(uuid.uuid4()),
                                 'partitionKey':
                                     {
                                         'paths': ['/id'],
                                         'kind': documents.PartitionKind.Hash
                                     }
                                 }

        offer_throughput = 10100
        created_collection = created_db.create_container(id=collection_definition['id'],
                                                         partition_key=collection_definition['partitionKey'],
                                                         offer_throughput=offer_throughput)

        self.assertEqual(collection_definition.get('id'), created_collection.id)

        created_collection_properties = created_collection.read(
            populate_partition_key_range_statistics=True,
            populate_quota_info=True)
        self.assertEqual(collection_definition.get('partitionKey').get('paths')[0],
                         created_collection_properties['partitionKey']['paths'][0])
        self.assertEqual(collection_definition.get('partitionKey').get('kind'),
                         created_collection_properties['partitionKey']['kind'])
        self.assertIsNotNone(created_collection_properties.get("statistics"))
        self.assertIsNotNone(created_db.client_connection.last_response_headers.get("x-ms-resource-usage"))

        expected_offer = created_collection.get_throughput()

        self.assertIsNotNone(expected_offer)

        self.assertEqual(expected_offer.offer_throughput, offer_throughput)

        created_db.delete_container(created_collection.id)


if __name__ == "__main__":
    unittest.main()
