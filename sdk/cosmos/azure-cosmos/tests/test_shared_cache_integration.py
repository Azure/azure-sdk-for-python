# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Integration tests for the shared partition key range cache and PKRange namedtuple.

These tests validate that multiple CosmosClient instances sharing the same endpoint
correctly share the routing map cache, that clear_cache() works transparently,
and that PKRange namedtuples are compatible with all CRUD and query operations.
"""

import unittest
import uuid

import pytest

import test_config
from azure.cosmos import CosmosClient
from azure.cosmos._routing.routing_map_provider import (
    PartitionKeyRangeCache,
    _shared_routing_map_cache,
    _shared_cache_lock,
)


@pytest.mark.cosmosEmulator
class TestSharedCacheIntegration(unittest.TestCase):
    """Integration tests requiring the Cosmos emulator."""

    host = test_config.TestConfig.host
    master_key = test_config.TestConfig.masterKey
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_ID = test_config.TestConfig.TEST_MULTI_PARTITION_CONTAINER_ID

    @classmethod
    def setUpClass(cls):
        cls.client1 = CosmosClient(cls.host, cls.master_key)
        cls.db = cls.client1.get_database_client(cls.TEST_DATABASE_ID)
        cls.container = cls.db.get_container_client(test_config.TestConfig.TEST_MULTI_PARTITION_CONTAINER_ID)
        # Seed data
        for i in range(20):
            cls.container.upsert_item({"id": f"shared-cache-item-{i}", "pk": f"pk-{i % 5}", "value": i})

    @classmethod
    def tearDownClass(cls):
        # Clean up seeded items
        for i in range(20):
            try:
                cls.container.delete_item(f"shared-cache-item-{i}", partition_key=f"pk-{i % 5}")
            except Exception:
                pass
        # Release the class-scoped client and clear the module-level shared routing-map
        # cache so subsequent test modules in the same process start from a clean slate.
        try:
            cls.client1.__exit__(None, None, None)
        except Exception:
            pass
        # Wipe ALL four shared-cache globals so subsequent test modules
        # observe a clean process state — not just the routing-map dict.
        from azure.cosmos._routing.routing_map_provider import (
            _shared_collection_locks,
            _shared_locks_locks,
            _shared_cache_refcounts,
        )
        with _shared_cache_lock:
            _shared_routing_map_cache.clear()
            _shared_collection_locks.clear()
            _shared_locks_locks.clear()
            _shared_cache_refcounts.clear()

    def _get_routing_provider(self, client):
        return client.client_connection._routing_map_provider

    def _get_cache_dict(self, client):
        return self._get_routing_provider(client)._collection_routing_map_by_item

    def _populate_cache(self, client, container):
        """Force PK range cache population by directly calling the routing-map provider.

        This avoids relying on incidental population by particular query
        execution paths, which are an implementation detail of the SDK.
        """
        provider = self._get_routing_provider(client)
        provider.get_routing_map(container.container_link, feed_options=None)

    def test_multi_client_shared_cache_reads(self):
        """Two clients to the same endpoint share the routing map after the first read."""
        with CosmosClient(self.host, self.master_key) as client2:
            container2 = client2.get_database_client(self.TEST_DATABASE_ID).get_container_client(
                self.TEST_CONTAINER_ID)

            # Client1 read triggers routing map population
            self.container.read_item("shared-cache-item-0", partition_key="pk-0")

            cache1 = self._get_cache_dict(self.client1)
            cache2 = self._get_cache_dict(client2)

            # Both clients point to the same cache dict
            self.assertIs(cache1, cache2)

            # Client2 can read without triggering a new _ReadPartitionKeyRanges
            result = container2.read_item("shared-cache-item-1", partition_key="pk-1")
            self.assertEqual(result["id"], "shared-cache-item-1")

    def test_multi_client_shared_cache_queries(self):
        """Client2 uses cached routing map populated by client1 for queries."""
        with CosmosClient(self.host, self.master_key) as client2:
            container2 = client2.get_database_client(self.TEST_DATABASE_ID).get_container_client(
                self.TEST_CONTAINER_ID)

            # Populate the routing-map cache deterministically (mirror the async
            # sibling test). Asserting on incidental population from a
            # particular query path is fragile.
            self._populate_cache(self.client1, self.container)

            cache = self._get_cache_dict(self.client1)
            self.assertTrue(len(cache) > 0, "Cache should be populated after routing-map fetch")

            # Client2 query should use the cached routing map
            results = list(container2.query_items(
                "SELECT * FROM c WHERE c.pk = 'pk-0'",
                enable_cross_partition_query=True
            ))
            self.assertTrue(len(results) > 0)

    def test_clear_cache_triggers_repopulation(self):
        """After clear_cache(), the next operation transparently re-populates."""
        # Populate cache
        self.container.read_item("shared-cache-item-0", partition_key="pk-0")
        cache = self._get_cache_dict(self.client1)
        self.assertTrue(len(cache) > 0)

        # Clear cache
        provider = self._get_routing_provider(self.client1)
        provider.clear_cache()

        # Next read transparently re-populates — verify the read succeeds
        result = self.container.read_item("shared-cache-item-0", partition_key="pk-0")
        self.assertEqual(result["id"], "shared-cache-item-0")
        cache = self._get_cache_dict(self.client1)
        self.assertTrue(len(cache) > 0, "Cache should be re-populated after read")

    def test_clear_cache_propagates_to_shared_clients(self):
        """clear_cache() clears the shared dict in place, preserving identity across clients."""
        with CosmosClient(self.host, self.master_key) as client2:
            container2 = client2.get_database_client(self.TEST_DATABASE_ID).get_container_client(
                self.TEST_CONTAINER_ID)

            # Both populate via client1
            self.container.read_item("shared-cache-item-0", partition_key="pk-0")
            old_cache = self._get_cache_dict(self.client1)
            self.assertTrue(len(old_cache) > 0)

            # Clear via client1
            self._get_routing_provider(self.client1).clear_cache()

            # Both clients still reference the same (now empty) shared dict
            # because clear_cache uses .clear() to preserve references
            cache1 = self._get_cache_dict(self.client1)
            cache2 = self._get_cache_dict(client2)
            self.assertIs(cache1, cache2, "Both clients should reference the same dict after clear_cache")
            self.assertEqual(len(cache1), 0)

            # Client2 read re-populates
            result = container2.read_item("shared-cache-item-2", partition_key="pk-2")
            self.assertEqual(result["id"], "shared-cache-item-2")

    def test_different_endpoints_isolated_with_emulator(self):
        """Emulator client cache is isolated from a different endpoint."""
        # Create a dummy provider for a different endpoint
        class DummyClient:
            url_connection = "https://other-account.documents.azure.com:443/"

        dummy_cache = PartitionKeyRangeCache(DummyClient())
        dummy_cache._collection_routing_map_by_item["dummy-coll"] = "dummy-data"

        # Populate emulator cache
        self.container.read_item("shared-cache-item-0", partition_key="pk-0")
        emulator_cache = self._get_cache_dict(self.client1)

        # Verify isolation
        self.assertNotIn("dummy-coll", emulator_cache)
        self.assertIn("dummy-coll", dummy_cache._collection_routing_map_by_item)

    def test_pkrange_survives_full_crud_lifecycle(self):
        """All CRUD operations work correctly with PKRange-based routing maps."""
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
        cache = self._get_cache_dict(self.client1)
        self.assertTrue(len(cache) > 0)

    def test_pkrange_in_change_feed(self):
        """Change feed operations work with PKRange-based routing maps."""
        # Insert a new item for change feed
        cf_id = f"cf-{uuid.uuid4()}"
        self.container.create_item({"id": cf_id, "pk": "cf-pk", "data": "change-feed-test"})

        # Read change feed from beginning
        results = list(self.container.query_items_change_feed(
            start_time="Beginning",
            partition_key="cf-pk"
        ))
        self.assertTrue(len(results) > 0, "Change feed should return results")

        # Cross-partition change feed
        all_results = list(self.container.query_items_change_feed(start_time="Beginning"))
        self.assertTrue(len(all_results) > 0, "Cross-partition change feed should return results")

        # Clean up
        self.container.delete_item(cf_id, partition_key="cf-pk")


if __name__ == "__main__":
    unittest.main()
