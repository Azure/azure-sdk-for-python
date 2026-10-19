# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original hierarchical-container throughput and partition-definition assertions."""

import os
import unittest
import uuid

from azure.cosmos import CosmosClient, documents, exceptions
from azure.cosmos.http_constants import StatusCodes


class TestCRUDOperationsSubPartition(unittest.TestCase):
    def setUp(self):
        self.client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
        self.addCleanup(self.client.close)
        self.database = self.client.create_database("throughput_hpk_" + uuid.uuid4().hex)
        self.addCleanup(self.client.delete_database, self.database.id)

    def test_partitioned_collection_subpartition_rust(self):
        # Source: tests/test_crud_subpartition.py::TestSubpartitionCrud.test_partitioned_collection_subpartition
        created_db = self.database
        collection_definition = {
            "id": "hierarchical",
            "partitionKey": {"paths": ["/id", "/pk"], "kind": documents.PartitionKind.MultiHash, "version": 2},
        }
        offer_throughput = 10100
        created_collection = created_db.create_container(
            id=collection_definition["id"], partition_key=collection_definition["partitionKey"],
            offer_throughput=offer_throughput,
        )
        self.assertEqual(collection_definition.get('id'), created_collection.id)
        created_collection_properties = created_collection.read()
        self.assertEqual(collection_definition.get('partitionKey').get('paths'),
                         created_collection_properties['partitionKey']['paths'])
        self.assertEqual(collection_definition.get('partitionKey').get('kind'),
                         created_collection_properties['partitionKey']['kind'])
        expected_offer = created_collection.get_throughput()
        self.assertIsNotNone(expected_offer)
        self.assertEqual(expected_offer.offer_throughput, offer_throughput)
        collection_definition2 = {
            "partitionKey": {
                "paths": ["/id", "/pk", "/id2", "/pk2"], "kind": documents.PartitionKind.MultiHash, "version": 2,
            },
        }
        try:
            created_db.create_container(
                id=collection_definition["id"], partition_key=collection_definition2["partitionKey"],
                offer_throughput=offer_throughput,
            )
        except exceptions.CosmosHttpResponseError as error:
            self.assertEqual(error.status_code, StatusCodes.BAD_REQUEST)
            self.assertTrue("Too many partition key paths" in error.message)
        else:
            self.fail("Four hierarchical partition-key paths must be rejected")
        collection_definition3 = {
            "partitionKey": {
                "paths": ["/id", "/pk", "/id2", "/pk2"], "kind": documents.PartitionKind.Hash, "version": 2,
            },
        }
        try:
            created_db.create_container(
                id=collection_definition["id"], partition_key=collection_definition3["partitionKey"],
                offer_throughput=offer_throughput,
            )
        except exceptions.CosmosHttpResponseError as error:
            self.assertEqual(error.status_code, StatusCodes.BAD_REQUEST)
            self.assertTrue("Too many partition key paths" in error.message)
        else:
            self.fail("Four hash partition-key paths must be rejected")
        created_db.delete_container(created_collection.id)
