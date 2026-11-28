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
from common._rust_checks import run_on_rust


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


@pytest.mark.cosmosLong
class TestCRUDContainerOperations(unittest.TestCase):

    def setUp(self) -> None:
        self.key_client = CosmosClient(HOST, KEY, _backend="rust")
        self.addCleanup(self.key_client.close)
        self._database_id = "query_containers_legacy_" + str(uuid.uuid4())
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

    def test_collection_crud_rust(self):
        """Container creation updates listing counts and yields a nonempty id-filtered query.

        This full legacy lifecycle checks the listing count before and after
        creation, reads the stored settings, queries by id, and verifies a 404
        when reading after deletion. It retains the listing checks formerly
        repeated in the sync list_containers copy.

        The read_container copy keeps the same scenario with separate setup
        that guards container reads against legacy fallback and requires Rust
        binding execution.
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

    @pytest.mark.cosmosAADLong
    def test_collection_crud_with_write_payload_disabled_rust(self):
        """Disabling write response bodies must not suppress queried container properties."""
        # Source: tests/test_crud_response_payload_on_write_disabled.py::TestCRUDOperationsResponsePayloadOnWriteDisabled.test_collection_crud
        client = CosmosClient(HOST, KEY, _backend="rust", no_response_on_write=True)
        self.addCleanup(client.close)
        created_db = client.get_database_client(self._database_id)
        collections = list(created_db.list_containers())
        before_create_collections_count = len(collections)
        collection_id = 'test_collection_crud ' + str(uuid.uuid4())
        partition_key = PartitionKey(path="/pk", kind="Hash")
        created_collection = created_db.create_container(
            id=collection_id,
            indexing_policy={'indexingMode': 'consistent'},
            partition_key=partition_key,
        )
        self.assertEqual(collection_id, created_collection.id)

        created_properties = created_collection.read()
        self.assertEqual('consistent', created_properties['indexingPolicy']['indexingMode'])
        self.assertDictEqual(partition_key, created_properties['partitionKey'])
        collections = list(created_db.list_containers())
        self.assertEqual(len(collections),
                         before_create_collections_count + 1,
                         'create should increase the number of collections')

        collections = run_on_rust(client, lambda: list(created_db.query_containers({
            'query': 'SELECT * FROM root r WHERE r.id=@id',
            'parameters': [{'name': '@id', 'value': collection_id}],
        })))
        self.assertTrue(collections)
        self.assertEqual([collection['id'] for collection in collections], [collection_id])
        self.assertDictEqual(partition_key, collections[0]['partitionKey'])

        created_db.delete_container(created_collection.id)
        created_container = created_db.get_container_client(created_collection.id)
        self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND, created_container.read)

    @pytest.mark.cosmosAADLong
    def test_collection_crud_subpartition_rust(self):
        """A three-level partition key must survive querying and recreating the container."""
        # Source: tests/test_crud_subpartition.py::TestSubpartitionCrud.test_collection_crud_subpartition
        created_db = self.databaseForTest
        collections = list(created_db.list_containers())
        before_create_collections_count = len(collections)
        collection_id = 'test_collection_crud_MH ' + str(uuid.uuid4())
        partition_key = PartitionKey(path=["/pk1", "/pk2", "/pk3"], kind="MultiHash")
        created_collection = created_db.create_container(
            id=collection_id,
            indexing_policy={'indexingMode': 'consistent'},
            partition_key=partition_key,
        )
        self.assertEqual(collection_id, created_collection.id)

        created_properties = created_collection.read()
        self.assertEqual('consistent', created_properties['indexingPolicy']['indexingMode'])
        collections = list(created_db.list_containers())
        self.assertEqual(len(collections),
                         before_create_collections_count + 1,
                         'create should increase the number of collections')

        collections = run_on_rust(self.key_client, lambda: list(created_db.query_containers({
            'query': 'SELECT * FROM root r WHERE r.id=@id',
            'parameters': [{'name': '@id', 'value': collection_id}],
        })))
        self.assertTrue(collections)
        self.assertEqual([collection['id'] for collection in collections], [collection_id])
        self.assertDictEqual(partition_key, collections[0]['partitionKey'])

        created_db.delete_container(created_collection.id)
        created_container = created_db.get_container_client(created_collection.id)
        self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND, created_container.read)

        recreated_partition_key = PartitionKey(path=["/id1", "/id2", "/id3"], kind="MultiHash")
        container_proxy = created_db.create_container(
            id=created_collection.id, partition_key=recreated_partition_key,
        )
        self.assertEqual(created_collection.id, container_proxy.id)
        container_properties = container_proxy._get_properties()
        self.assertDictEqual(recreated_partition_key, container_properties['partitionKey'])
        created_db.delete_container(created_collection.id)


if __name__ == "__main__":
    unittest.main()
