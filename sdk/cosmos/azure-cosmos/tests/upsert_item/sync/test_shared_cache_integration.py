# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Original full CRUD lifecycle from the shared-cache tests, on the Rust path.

The CRUD steps and the deleted-item read check run unchanged. The final check
inspected the legacy Python partition-key-range cache, which Rust operations
never fill; Rust keeps that cache inside its driver with no way to inspect it,
so that one step is skipped. Uses a test-owned database and container.
"""

import os
import unittest
import uuid

import pytest

from config import settings
from azure.cosmos import CosmosClient, PartitionKey


@pytest.mark.cosmosEmulator
class TestSharedCacheIntegration(unittest.TestCase):
    """Integration tests requiring the Cosmos emulator."""

    host = os.environ.get("ACCOUNT_HOST", settings.TestSettings.host)
    master_key = os.environ.get("ACCOUNT_KEY", settings.TestSettings.masterKey)

    @classmethod
    def setUpClass(cls):
        cls.client1 = CosmosClient(cls.host, cls.master_key, _backend="rust")
        cls.TEST_DATABASE_ID = "upsert_shared_cache_" + uuid.uuid4().hex
        cls.db = cls.client1.create_database(cls.TEST_DATABASE_ID)
        cls.container = cls.db.create_container(
            id="MultiPartitionTestContainer-" + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=settings.TestSettings.THROUGHPUT_FOR_5_PARTITIONS,
        )
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
        pytest.skip(
            "internals-only: cache step not run on Rust: the partition-key-range routing map lives in the Rust driver, "
            "which exposes no inspection hook (only _debug_cached_account_regions and attempt/retry "
            "counters); client.client_connection._routing_map_provider is the legacy cache that Rust "
            "operations never populate. All CRUD, delete and read-after-delete assertions above passed."
        )
        cache = self.client1.client_connection._routing_map_provider._collection_routing_map_by_item
        self.assertTrue(len(cache) > 0)
