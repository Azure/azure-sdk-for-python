# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Shared-cache integration tests that exercise query_items, on the Rust path.

The CRUD and query steps run unchanged. The originals also fill and inspect the
legacy Python partition-key-range cache, which Rust operations never use; Rust keeps
that cache inside its driver with no way to inspect it, so those steps are skipped.
Uses a test-owned database and container.
"""

import os
import unittest
import uuid

import pytest

from config import settings
from azure.cosmos import CosmosClient, PartitionKey

CACHE_NOT_OBSERVABLE = (
    "internals-only: cache step not run on Rust: the partition-key-range routing map lives in the Rust driver, "
    "which exposes no inspection hook (only _debug_cached_account_regions and attempt/retry "
    "counters); client.client_connection._routing_map_provider is the legacy cache that Rust "
    "operations never populate."
)


@pytest.mark.cosmosEmulator
class TestSharedCacheIntegration(unittest.TestCase):
    """Integration tests requiring the Cosmos emulator."""

    host = os.environ.get("ACCOUNT_HOST", settings.TestSettings.host)
    master_key = os.environ.get("ACCOUNT_KEY", settings.TestSettings.masterKey)

    @classmethod
    def setUpClass(cls):
        cls.client1 = CosmosClient(cls.host, cls.master_key, _backend="rust")
        cls.TEST_DATABASE_ID = "query_shared_cache_" + uuid.uuid4().hex
        cls.db = cls.client1.create_database(cls.TEST_DATABASE_ID)
        cls.container = cls.db.create_container(
            id="MultiPartitionTestContainer-" + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=settings.TestSettings.THROUGHPUT_FOR_5_PARTITIONS,
        )
        cls.TEST_CONTAINER_ID = cls.container.id
        # Seed data
        for i in range(20):
            cls.container.upsert_item({"id": f"shared-cache-item-{i}", "pk": f"pk-{i % 5}", "value": i})

    @classmethod
    def tearDownClass(cls):
        try:
            cls.client1.delete_database(cls.TEST_DATABASE_ID)
        except Exception:  # pylint: disable=broad-except
            pass
        cls.client1.close()

    def test_multi_client_shared_cache_queries_rust(self):
        # Source: tests/test_shared_cache_integration.py::TestSharedCacheIntegration.test_multi_client_shared_cache_queries
        """Client2 uses cached routing map populated by client1 for queries."""
        with CosmosClient(self.host, self.master_key, _backend="rust") as client2:
            container2 = client2.get_database_client(self.TEST_DATABASE_ID).get_container_client(
                self.TEST_CONTAINER_ID)

            # The original fills the legacy routing-map cache via _populate_cache here and asserts
            # it is non-empty; those two steps are reported by the skip below.

            # Client2 query should use the cached routing map
            results = list(container2.query_items(
                "SELECT * FROM c WHERE c.pk = 'pk-0'",
                enable_cross_partition_query=True
            ))
            self.assertTrue(len(results) > 0)

        pytest.skip(CACHE_NOT_OBSERVABLE + " The client2 query and its assertion above passed.")

    def test_pkrange_survives_full_crud_lifecycle_rust(self):
        # Source: tests/test_shared_cache_integration.py::TestSharedCacheIntegration.test_pkrange_survives_full_crud_lifecycle
        crud_id = f"crud-{uuid.uuid4()}"

        # Create
        item = self.container.create_item({"id": crud_id, "pk": "crud-pk", "data": "test"})
        self.assertEqual(item["id"], crud_id)

        # Read
        read = self.container.read_item(crud_id, partition_key="crud-pk")
        self.assertEqual(read["data"], "test")

        # Replace
        read["data"] = "updated"
        replaced = self.container.replace_item(crud_id, read)
        self.assertEqual(replaced["data"], "updated")

        # Query
        results = list(self.container.query_items(
            f"SELECT * FROM c WHERE c.id = '{crud_id}'",
            enable_cross_partition_query=True
        ))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["data"], "updated")

        # Upsert
        read["data"] = "upserted"
        upserted = self.container.upsert_item(read)
        self.assertEqual(upserted["data"], "upserted")

        # Delete
        self.container.delete_item(crud_id, partition_key="crud-pk")
        with self.assertRaises(Exception):
            self.container.read_item(crud_id, partition_key="crud-pk")

        # Verify cache still has PKRange-based routing map
        pytest.skip(CACHE_NOT_OBSERVABLE + " All CRUD, delete and read-after-delete assertions above passed.")
        cache = self.client1.client_connection._routing_map_provider._collection_routing_map_by_item
        self.assertTrue(len(cache) > 0)
