# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Rust-path copies of the sync change-feed partition-key-variation tests that run query_items.

Source: ``tests/test_changefeed_partition_key_variation.py::TestChangeFeedPKVariation``.
Each copied test reads the change feed and runs ``query_items`` for the same partition
key, then compares the counts. Hash V1, Hash V2 and hierarchical keys are covered, on
single- and multi-partition containers. Steps and assertions are unchanged. Setup is
test-owned: the class creates its own database with a key-auth Rust client, and data
operations go through a Rust data client from ``config.clients``. Tests that never call
query_items (EPK hashing, version-1 properties) are not copied.
"""

import unittest
import uuid

import pytest

from azure.cosmos.partition_key import PartitionKey
from config import clients
from config.settings import TestSettings


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
class TestChangeFeedPKVariation(unittest.TestCase):
    """Test change feed with different partition key variations."""

    configs = TestSettings
    host = configs.host
    masterKey = configs.masterKey
    TEST_DATABASE_ID = "query_items_cf_pk_variation_" + uuid.uuid4().hex
    # Items for Hash V1 partition key
    single_hash_items = [
                        {"id": str(i), "pk": f"short_string"} for i in range(1, 101)
                    ] + [
                        {"id": str(i), "pk": f"long_string_" + "a" * 251} for i in range(101, 201)
                    ] + [
                        {"id": str(i), "pk": 1000} for i in range(201, 301)
                    ] + [
                        {"id": str(i), "pk": 1000 * 1.1111} for i in range(301, 401)
                    ] + [
                        {"id": str(i), "pk": True} for i in range(401, 501)
                    ]

    # Items for Hierarchical Partition Keys
    hpk_items = [
                    {"id": str(i), "pk1": "level1_", "pk2": "level2_"} for i in range(1, 101)
                ] + [
                    {"id": str(i), "pk1": "level1_", "pk2": f"level2_long__" + "c" * 101} for i in range(101, 201)
                ] + [
                    {"id": str(i), "pk1": 10, "pk2": 1000} for i in range(201, 301)
                ] + [
                    {"id": str(i), "pk1": 10 * 1.1, "pk2": 10 * 2.2} for i in range(301, 401)
                ] + [
                        {"id": str(i), "pk1": True, 'pk2': False} for i in range(401, 501)
                    ]

    @classmethod
    def setUpClass(cls):
        # Key-auth setup client is used for container lifecycle (control-plane) in this test.
        cls.key_client = clients.create_setup_client(_backend="rust")
        cls.key_db = cls.key_client.create_database_if_not_exists(cls.TEST_DATABASE_ID)
        # AAD (or key) client for data-plane operations
        cls.client = clients.create_data_client(_backend="rust")
        cls.db = cls.client.get_database_client(cls.TEST_DATABASE_ID)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.key_client.delete_database(cls.TEST_DATABASE_ID)
        finally:
            cls.client.close()
            cls.key_client.close()

    def create_container(self, container_id, partition_key, version=None, throughput=None):
        """Helper to create a container and return a data-plane proxy."""
        # Container creation is control-plane and uses key_db.
        if isinstance(partition_key, list):
            pk_definition = PartitionKey(path=partition_key, kind='MultiHash')
        else:
            pk_definition = PartitionKey(path=partition_key, kind='Hash', version=version)
        if throughput:
            self.key_db.create_container(id=container_id, partition_key=pk_definition, offer_throughput=throughput)
        else:
            self.key_db.create_container(id=container_id, partition_key=pk_definition)
        return self.db.get_container_client(container_id)

    def insert_items(self, container, items):
        """Helper to insert items into a container."""
        for item in items:
            container.create_item(body=item)

    def validate_changefeed(self, container):
        """Helper to validate changefeed results."""
        partition_keys = ["short_string", "long_string_" + "a" * 251, 1000, 1000 * 1.1111, True]
        for pk in partition_keys:
            changefeed = container.query_items_change_feed(is_start_from_beginning=True, partition_key=pk)
            changefeed_items = [item for item in changefeed]

            # Perform a regular query
            regular_query = container.query_items(query="SELECT * FROM c", partition_key=pk)
            regular_query_items = [item for item in regular_query]

            # Compare the number of documents returned
            assert len(changefeed_items) == len(regular_query_items), (
                f"Mismatch in document count for partition key {pk}: Changefeed returned {len(changefeed_items)} items,"
                f"while regular query returned {len(regular_query_items)} items."
            )

    def validate_changefeed_hpk(self, container):
        """Helper to validate changefeed results for hierarchical partition keys."""
        partition_keys = [
            ["level1_", "level2_"],
            ["level1_", "level2_long__" + "c" * 101],
            [10, 1000],
            [10 * 1.1, 10 * 2.2],
            [True, False]
        ]
        for pk in partition_keys:
            # Perform a change feed query
            changefeed = container.query_items_change_feed(is_start_from_beginning=True, partition_key=pk)
            changefeed_items = [item for item in changefeed]

            # Perform a regular query
            regular_query = container.query_items(query="SELECT * FROM c", partition_key=pk)
            regular_query_items = [item for item in regular_query]

            # Compare the number of documents returned
            assert len(changefeed_items) == len(regular_query_items), (
                f"Mismatch in document count for partition key {pk}: Changefeed returned {len(changefeed_items)} items,"
                f"while regular query returned {len(regular_query_items)} items."
            )

    def test_hash_v1_partition_key_rust(self):
        # Source: tests/test_changefeed_partition_key_variation.py::TestChangeFeedPKVariation.test_hash_v1_partition_key
        """Test changefeed with Hash V1 partition key."""
        container_id = f"container_test_hash_V1_{uuid.uuid4()}"
        container = self.create_container(container_id, "/pk", version=1)
        items = self.single_hash_items
        self.insert_items(container, items)
        self.validate_changefeed(container)
        self.key_db.delete_container(container_id)

    def test_hash_v2_partition_key_rust(self):
        # Source: tests/test_changefeed_partition_key_variation.py::TestChangeFeedPKVariation.test_hash_v2_partition_key
        """Test changefeed with Hash V2 partition key."""
        container_id = f"container_test_hash_V2_{uuid.uuid4()}"
        container = self.create_container(container_id, "/pk", version=2)
        items = self.single_hash_items
        self.insert_items(container, items)
        self.validate_changefeed(container)
        self.key_db.delete_container(container_id)

    def test_hpk_partition_key_rust(self):
        # Source: tests/test_changefeed_partition_key_variation.py::TestChangeFeedPKVariation.test_hpk_partition_key
        """Test changefeed with hierarchical partition key."""
        container_id = f"container_test_hpk_{uuid.uuid4()}"
        container = self.create_container(container_id, ["/pk1", "/pk2"])
        items = self.hpk_items
        self.insert_items(container, items)
        self.validate_changefeed_hpk(container)
        self.key_db.delete_container(container_id)

    def test_multiple_physical_partitions_rust(self):
        # Source: tests/test_changefeed_partition_key_variation.py::TestChangeFeedPKVariation.test_multiple_physical_partitions
        """Test change feed with a container having multiple physical partitions."""
        # Test for Hash V1 partition key
        container_id_v1 = f"container_test_multiple_partitions_hash_v1_{uuid.uuid4()}"
        throughput = 12000
        container_v1 = self.create_container(container_id_v1, "/pk", version=1, throughput=throughput)

        feed_ranges_v1 = container_v1.read_feed_ranges()
        feed_ranges_v1 = [feed_range for feed_range in feed_ranges_v1]
        assert len(feed_ranges_v1) > 1, "Hash V1 container does not have multiple physical partitions."

        self.insert_items(container_v1, self.single_hash_items)
        self.validate_changefeed(container_v1)
        self.key_db.delete_container(container_id_v1)

        # Test for Hash V2 partition key
        container_id_v2 = f"container_test_multiple_partitions_hash_v2_{uuid.uuid4()}"
        container_v2 = self.create_container(container_id_v2, "/pk", version=2, throughput=throughput)

        feed_ranges_v2 = container_v2.read_feed_ranges()
        feed_ranges_v2 = [feed_range for feed_range in feed_ranges_v2]
        assert len(feed_ranges_v2) > 1, "Hash V2 container does not have multiple physical partitions."

        self.insert_items(container_v2, self.single_hash_items)
        self.validate_changefeed(container_v2)
        self.key_db.delete_container(container_id_v2)

        # Test for Hierarchical Partition Keys (HPK)
        container_id_hpk = f"container_test_multiple_partitions_hpk_{uuid.uuid4()}"
        container_hpk = self.create_container(container_id_hpk, ["/pk1", "/pk2"], throughput=throughput)

        feed_ranges_hpk = container_hpk.read_feed_ranges()
        feed_ranges_hpk = [feed_range for feed_range in feed_ranges_hpk]
        assert len(feed_ranges_hpk) > 1, "HPK container does not have multiple physical partitions."

        self.insert_items(container_hpk, self.hpk_items)
        self.validate_changefeed_hpk(container_hpk)
        self.key_db.delete_container(container_id_hpk)


if __name__ == "__main__":
    unittest.main()
