# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Original point-operation response-hook comparisons, run on the Rust path.

Each point operation's callback headers are compared with the same
operation's returned headers; delete_item has no body, so only the callback
is checked. Uses a test-owned database.
"""

import unittest
import uuid

import pytest

from config import clients, settings
from azure.cosmos import CosmosClient, PartitionKey


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosQuery
@pytest.mark.cosmosAADQuery
class TestQueryResponseHeaders(unittest.TestCase):
    def setUp(self):
        config = settings.TestSettings
        self.key_client = CosmosClient(config.host, config.masterKey, _backend="rust")
        self.addCleanup(self.key_client.close)
        database_id = "delete_response_hooks_" + uuid.uuid4().hex
        self.key_db = self.key_client.create_database(database_id)
        self.addCleanup(self.key_client.delete_database, database_id)
        self.client = clients.create_data_client(_backend="rust")
        self.addCleanup(self.client.close)
        self.created_db = self.client.get_database_client(database_id)

    def _create_container_for_test(self, container_id, partition_key, **kwargs):
        self.key_db.create_container(id=container_id, partition_key=partition_key, **kwargs)
        return self.created_db.get_container_client(container_id)

    def _delete_container_for_test(self, container_id):
        self.key_db.delete_container(container_id)

    def test_response_hook_parity_point_ops_rust(self):
        # Source: tests/test_query_response_headers.py::TestQueryResponseHeaders.test_response_hook_parity_point_ops
        container_id = "test_hookparity_point_" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        try:
            captured = []

            def hook(headers, _body):
                captured.append(dict(headers))

            # create_item
            captured.clear()
            created = created_collection.create_item(
                body={"pk": "p", "id": "doc1", "value": 1},
                response_hook=hook,
            )
            self.assertEqual(len(captured), 1)
            self.assertEqual(
                created.get_response_headers()["x-ms-request-charge"],
                captured[0]["x-ms-request-charge"],
            )

            # read_item
            captured.clear()
            read = created_collection.read_item(
                item="doc1", partition_key="p", response_hook=hook,
            )
            self.assertEqual(len(captured), 1)
            self.assertEqual(
                read.get_response_headers()["x-ms-request-charge"],
                captured[0]["x-ms-request-charge"],
            )

            # replace_item
            captured.clear()
            replaced = created_collection.replace_item(
                item="doc1",
                body={"pk": "p", "id": "doc1", "value": 2},
                response_hook=hook,
            )
            self.assertEqual(len(captured), 1)
            self.assertEqual(
                replaced.get_response_headers()["x-ms-request-charge"],
                captured[0]["x-ms-request-charge"],
            )

            # upsert_item
            captured.clear()
            upserted = created_collection.upsert_item(
                body={"pk": "p", "id": "doc1", "value": 3},
                response_hook=hook,
            )
            self.assertEqual(len(captured), 1)
            self.assertEqual(
                upserted.get_response_headers()["x-ms-request-charge"],
                captured[0]["x-ms-request-charge"],
            )

            # delete_item (no body)
            captured.clear()
            created_collection.delete_item(item="doc1", partition_key="p", response_hook=hook)
            self.assertEqual(len(captured), 1)
            self.assertIn("x-ms-request-charge", captured[0])
        finally:
            self._delete_container_for_test(container_id)
