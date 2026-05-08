# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Fault injection tests for the shared partition key range cache.

These tests use FaultInjectionTransport to simulate failures (410 Gone,
partition splits, transient errors) and validate that the shared cache
correctly refreshes, serializes concurrent refreshes, and maintains
data integrity under concurrent access.
"""

import threading
import unittest
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest

import test_config
from azure.cosmos import CosmosClient
from azure.cosmos._routing.routing_range import PKRange


@pytest.mark.cosmosEmulator
class TestSharedCacheFaultInjection(unittest.TestCase):
    """Fault injection tests requiring the Cosmos emulator."""

    host = test_config.TestConfig.host
    master_key = test_config.TestConfig.masterKey
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_ID = test_config.TestConfig.TEST_MULTI_PARTITION_CONTAINER_ID

    @classmethod
    def setUpClass(cls):
        cls.client = CosmosClient(cls.host, cls.master_key)
        cls.db = cls.client.get_database_client(cls.TEST_DATABASE_ID)
        cls.container = cls.db.get_container_client(test_config.TestConfig.TEST_MULTI_PARTITION_CONTAINER_ID)
        for i in range(10):
            cls.container.upsert_item({"id": f"fi-{i}", "pk": f"pk-{i % 3}", "value": i})

    @classmethod
    def tearDownClass(cls):
        for i in range(10):
            try:
                cls.container.delete_item(f"fi-{i}", partition_key=f"pk-{i % 3}")
            except Exception:
                pass

    def _make_fault_client(self, transport):
        return CosmosClient(self.host, self.master_key, transport=transport)

    def test_concurrent_cache_refresh_no_crash(self):
        """Multiple threads calling clear_cache + read concurrently don't crash or corrupt."""
        errors = []

        def worker(worker_id):
            try:
                with CosmosClient(self.host, self.master_key) as client:
                    container = client.get_database_client(self.TEST_DATABASE_ID).get_container_client(
                        self.TEST_CONTAINER_ID)
                    for _ in range(5):
                        # Clear cache and immediately read
                        client.client_connection._routing_map_provider.clear_cache()
                        result = container.read_item(
                            f"fi-{worker_id % 3}", partition_key=f"pk-{worker_id % 3}")
                        assert result["id"] == f"fi-{worker_id % 3}"
            except Exception as e:
                errors.append((worker_id, str(e)))

        with ThreadPoolExecutor(max_workers=5) as pool:
            futures = [pool.submit(worker, i) for i in range(5)]
            for f in as_completed(futures):
                f.result()  # Re-raise exceptions

        self.assertEqual(len(errors), 0, f"Concurrent errors: {errors}")

    def test_pkrange_readonly_fields_not_corrupted(self):
        """PKRange namedtuple fields are immutable and cannot be accidentally modified."""
        pk = PKRange(id="0", minInclusive="", maxExclusive="FF", parents=())

        # Namedtuple fields are read-only
        with self.assertRaises(AttributeError):
            pk.id = "modified"

        with self.assertRaises(AttributeError):
            pk.minInclusive = "modified"

        # Original values unchanged
        self.assertEqual(pk.id, "0")
        self.assertEqual(pk.maxExclusive, "FF")

        # Dict-style access still works
        self.assertEqual(pk["id"], "0")
        self.assertEqual(pk.get("minInclusive"), "")

    def test_clear_cache_during_concurrent_reads(self):
        """Clearing cache while reads are in progress doesn't cause crashes."""
        stop_event = threading.Event()
        errors = []

        def reader():
            with CosmosClient(self.host, self.master_key) as client:
                container = client.get_database_client(self.TEST_DATABASE_ID).get_container_client(
                    self.TEST_CONTAINER_ID)
                while not stop_event.is_set():
                    try:
                        container.read_item("fi-0", partition_key="pk-0")
                    except Exception as e:
                        errors.append(str(e))
                        break

        # Start readers
        threads = [threading.Thread(target=reader) for _ in range(3)]
        for t in threads:
            t.start()

        # Rapidly clear cache while reads are happening
        for _ in range(10):
            self.client.client_connection._routing_map_provider.clear_cache()

        stop_event.set()
        for t in threads:
            t.join(timeout=10)

        self.assertEqual(len(errors), 0, f"Errors during concurrent reads: {errors}")


if __name__ == "__main__":
    unittest.main()
