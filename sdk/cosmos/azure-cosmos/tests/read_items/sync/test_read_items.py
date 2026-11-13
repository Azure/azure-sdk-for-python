# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Sync ``read_items`` contract tests against the ``_backend="rust"`` path.

Self-contained: builds its own database + container in ``setUp`` and deletes them
in ``tearDown``; methods that need a different partition-key shape build (and
delete) their own container. The class and method names match the source (apart from the
method's ``_rust`` suffix) at
``tests/test_read_items.py`` so test IDs differ by path and method suffix.

These pin the customer-facing contract of ``read_items`` -- missing items omitted,
single vs multi item, different / hierarchical partition keys, the aggregated
request-charge header, and input-order preservation -- so an absolute regression
is caught even when the two backends agree with each other.

Faults use native driver injection in ``test_read_items_native.py`` rather
than the original core-python ``FaultInjectionTransport``. That module covers
429/410 recovery, terminal errors, later-page failures, deadlines, cancellation,
and batching beyond 64 selections. Original large-count, scrambled-order and
container-recreation cases are retained below. The removed Python concurrency
coordinator is intentionally not tested.

Run with::

    pytest --import-mode=importlib tests/read_items/sync/test_read_items.py -v
"""
import os
import unittest
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
class TestReadItems(unittest.TestCase):
    """read_items on a Rust-backed client: each test seeds its own container, runs
    the batched read, and checks the customer-visible contract (which items
    come back, in what order, and the aggregated request-charge header)."""

    def setUp(self):
        self.client = CosmosClient(HOST, KEY, _backend="rust", timeout=20)
        self.addCleanup(self.client.close)
        self._db_id = "rust_read_items_sync_" + uuid.uuid4().hex[:8]
        self.database = self.client.create_database(self._db_id)
        self.addCleanup(self.client.delete_database, self._db_id)
        self.key_database = self.database
        self._container_id = "read_items_container_" + str(uuid.uuid4())
        container_ref = self.database.create_container(
            id=self._container_id,
            partition_key=PartitionKey(path="/id"),
        )
        self.container = self.database.get_container_client(container_ref.id)

    @staticmethod
    def _create_records_for_read_items(container, count, id_prefix="item"):
        # Seed `count` items and return the (id, pk) pairs to read back plus the
        # ids alone; the container is keyed on /id, so each id doubles as its own pk.
        items_to_read = []
        item_ids = []
        for i in range(count):
            doc_id = f"{id_prefix}_{i}_{uuid.uuid4()}"
            item_ids.append(doc_id)
            items_to_read.append((doc_id, doc_id))
            container.create_item({'id': doc_id, 'data': i})
        return items_to_read, item_ids

    def test_read_items_single_item_rust(self):
        """One (id, pk) pair in the batch -> read_items returns exactly that one item."""
        # Source: tests/test_read_items.py::TestReadItems.test_read_items_single_item
        items_to_read, item_ids = self._create_records_for_read_items(self.container, 1)
        read_items = self.container.read_items(items=items_to_read)
        self.assertEqual(len(read_items), 1)
        self.assertEqual(read_items[0]['id'], item_ids[0])

    def test_read_items_with_missing_items_rust(self):
        """A batch mixing real and non-existent ids -> only the real items come back; missing ids are omitted, not errors."""
        # Source: tests/test_read_items.py::TestReadItems.test_read_items_with_missing_items
        items_to_read, _ = self._create_records_for_read_items(self.container, 3, "existing_item")
        items_to_read.append(("non_existent_item1" + str(uuid.uuid4()), "non_existent_pk1"))
        items_to_read.append(("non_existent_item2" + str(uuid.uuid4()), "non_existent_pk2"))
        read_items = self.container.read_items(items=items_to_read)
        self.assertEqual(len(read_items), 3)
        returned_ids = {item['id'] for item in read_items}
        expected_ids = {item_tuple[0] for item_tuple in items_to_read if "existing" in item_tuple[0]}
        self.assertSetEqual(returned_ids, expected_ids)

    def test_read_items_different_partition_key_rust(self):
        """Partition key on its own path (/pk, not /id) -> read_items still finds every requested item."""
        # Source: tests/test_read_items.py::TestReadItems.test_read_items_different_partition_key
        container_id = 'read_items_pk_container_' + str(uuid.uuid4())
        self.database.create_container(id=container_id, partition_key=PartitionKey(path="/pk"))
        container_pk = self.database.get_container_client(container_id)
        try:
            items_to_read = []
            item_ids = []
            for i in range(5):
                doc_id = f"item{i}_{uuid.uuid4()}"
                pk_value = f"pk_{i}"
                item_ids.append(doc_id)
                container_pk.create_item({'id': doc_id, 'pk': pk_value, 'data': i})
                items_to_read.append((doc_id, pk_value))
            read_items = container_pk.read_items(items=items_to_read)
            self.assertEqual(len(read_items), len(item_ids))
            read_ids = {item['id'] for item in read_items}
            self.assertSetEqual(read_ids, set(item_ids))
        finally:
            self.database.delete_container(container_id)

    def test_read_items_fails_with_incomplete_hierarchical_pk_rust(self):
        """A hierarchical partition key with too few components makes read_items raise ValueError."""
        # Source: tests/test_read_items.py::TestReadItems.test_read_items_fails_with_incomplete_hierarchical_pk
        container_id = 'read_items_hpk_incomplete_container_' + str(uuid.uuid4())
        self.database.create_container(
            id=container_id,
            partition_key=PartitionKey(path=["/tenantId", "/userId"], kind="MultiHash"),
        )
        container_hpk = self.database.get_container_client(container_id)
        try:
            items_to_read = []
            doc_id = f"item_valid_{uuid.uuid4()}"
            tenant_id = "tenant1"
            user_id = "user1"
            container_hpk.create_item({'id': doc_id, 'tenantId': tenant_id, 'userId': user_id})
            items_to_read.append((doc_id, [tenant_id, user_id]))
            incomplete_pk_item_id = f"item_incomplete_{uuid.uuid4()}"
            items_to_read.append((incomplete_pk_item_id, ["tenant_only"]))
            with self.assertRaises(ValueError) as context:
                container_hpk.read_items(items=items_to_read)
            self.assertIn("read_items requires every component of the container's partition key.",
                          str(context.exception))
        finally:
            self.database.delete_container(container_id)

    def test_read_items_hierarchical_partition_key_rust(self):
        """Two-level (tenantId, userId) partition key -> read_items returns every requested item."""
        # Source: tests/test_read_items.py::TestReadItems.test_read_items_hierarchical_partition_key
        container_id = 'read_hpk_container_' + str(uuid.uuid4())
        self.database.create_container(
            id=container_id,
            partition_key=PartitionKey(path=["/tenantId", "/userId"], kind="MultiHash"),
        )
        container_hpk = self.database.get_container_client(container_id)
        try:
            items_to_read = []
            item_ids = []
            for i in range(3):
                doc_id = f"item{i}_{uuid.uuid4()}"
                tenant_id = f"tenant{i % 2}"
                user_id = f"user{i}"
                item_ids.append(doc_id)
                container_hpk.create_item({'id': doc_id, 'tenantId': tenant_id, 'userId': user_id, 'data': i})
                items_to_read.append((doc_id, [tenant_id, user_id]))
            read_items = container_hpk.read_items(items=items_to_read)
            self.assertEqual(len(read_items), len(item_ids))
            read_ids = {item['id'] for item in read_items}
            self.assertSetEqual(read_ids, set(item_ids))
        finally:
            self.database.delete_container(container_id)

    def test_read_items_with_no_results_preserve_headers_rust(self):
        """All ids non-existent -> an empty result, but the aggregated x-ms-request-charge header is still present and non-zero."""
        # Source: tests/test_read_items.py::TestReadItems.test_read_items_with_no_results_preserve_headers
        items_to_read = [
            ("non_existent_item_1_" + str(uuid.uuid4()), "non_existent_pk_1"),
            ("non_existent_item_2_" + str(uuid.uuid4()), "non_existent_pk_2"),
        ]
        read_items = self.container.read_items(items=items_to_read)
        headers = read_items.get_response_headers()
        self.assertEqual(len(read_items), 0)
        self.assertIn('x-ms-request-charge', headers)
        self.assertNotIn('x-ms-continuation', headers)
        self.assertGreater(float(headers.get('x-ms-request-charge')), 0)

    def test_headers_being_returned_on_success_rust(self):
        """Success exposes the total charge and available metadata, without a continuation."""
        # Source: tests/test_read_items.py::TestReadItems.test_headers_being_returned_on_success
        items_to_read, item_ids = self._create_records_for_read_items(self.container, 5)
        read_items = self.container.read_items(items=items_to_read)
        headers = read_items.get_response_headers()
        self.assertEqual(len(read_items), len(item_ids))
        self.assertIsNotNone(headers)
        self.assertIn('x-ms-request-charge', headers)
        self.assertNotIn('x-ms-continuation', headers)
        self.assertGreater(float(headers.get('x-ms-request-charge')), 0)

    def test_read_items_order_using_zip_comparison_rust(self):
        """The returned items come back in the same order as the input (id, pk) list."""
        # Source: tests/test_read_items.py::TestReadItems.test_read_items_order_using_zip_comparison
        container_id = 'read_order_zip_container_' + str(uuid.uuid4())
        self.database.create_container(id=container_id, partition_key=PartitionKey(path="/pk"))
        container_pk = self.database.get_container_client(container_id)
        try:
            all_items = []
            for i in range(30):
                doc_id = f"zip_item_{i}_{uuid.uuid4()}"
                pk_value = f"pk_{i % 5}"
                container_pk.create_item({'id': doc_id, 'pk': pk_value, 'order_value': i})
                all_items.append((doc_id, pk_value))
            read_items = container_pk.read_items(items=all_items)
            self.assertEqual(len(read_items), len(all_items))
            consolidated = zip(all_items, read_items)
            matching = [x[0][0] == x[1]["id"] and x[0][1] == x[1]["pk"] for x in consolidated]
            self.assertTrue(all(matching),
                            "Order was not preserved. Input order doesn't match output order.")
        finally:
            self.database.delete_container(container_id)

    def test_read_items_large_count_rust(self):
        """Tests read_items with a large number of items."""
        # Source: tests/test_read_items.py::TestReadItems.test_read_items_large_count
        items_to_read, item_ids = self._create_records_for_read_items(self.container, 3100)

        read_items = self.container.read_items(items=items_to_read)

        self.assertEqual(len(read_items), len(item_ids))
        read_ids = {item['id'] for item in read_items}
        self.assertSetEqual(read_ids, set(item_ids))

    def test_read_items_preserves_input_order_rust(self):
        """Tests that read_items preserves the original order of input items."""
        # Source: tests/test_read_items.py::TestReadItems.test_read_items_preserves_input_order
        container_id = 'read_order_container_' + str(uuid.uuid4())
        self.key_database.create_container(
            id=container_id,
            partition_key=PartitionKey(path="/pk")
        )
        container_pk = self.database.get_container_client(container_id)

        try:
            # Create items with varied partition keys to ensure cross-partition queries
            all_items = []

            # Create items with alternating partition keys to ensure they span partitions
            for i in range(50):
                doc_id = f"order_item_{i}_{uuid.uuid4()}"
                # Use different partition keys to ensure items are spread across partitions
                pk_value = f"pk_{i % 5}"

                # Create the item in the container
                container_pk.create_item({'id': doc_id, 'pk': pk_value, 'order_value': i})

                # Add to our master list
                all_items.append((doc_id, pk_value))

            # Create a complex order for the read operation
            # Mix items from different partitions in a non-sequential order
            scrambled_items = []
            scrambled_items.extend(all_items[25:])  # Second half first
            scrambled_items.extend(all_items[:25])  # Then first half

            # Add a few more out-of-order items
            if len(all_items) >= 30:
                # Move some items from the middle to the end
                moved_items = scrambled_items[10:15]
                scrambled_items = scrambled_items[:10] + scrambled_items[15:]
                scrambled_items.extend(moved_items)

            # Read items using read_items with scrambled order
            read_items = container_pk.read_items(items=scrambled_items)

            # Verify that all items were returned
            self.assertEqual(len(read_items), len(scrambled_items))

            # Verify the order matches the scrambled input order
            for i, item in enumerate(read_items):
                expected_id = scrambled_items[i][0]
                expected_pk = scrambled_items[i][1]
                self.assertEqual(
                    item['id'],
                    expected_id,
                    f"Item at position {i} does not match input order. Expected ID {expected_id}, got {item['id']}"
                )
                self.assertEqual(
                    item['pk'],
                    expected_pk,
                    f"Item at position {i} does not match input order. Expected PK {expected_pk}, got {item['pk']}"
                )

        finally:
            # Clean up
            self.key_database.delete_container(container_id)  # control-plane

    def test_read_after_container_recreation_rust(self):
        """Tests read_items after a container is deleted and recreated with a different configuration."""
        # Source: tests/test_read_items.py::TestReadItems.test_read_after_container_recreation
        container_id = self._container_id
        initial_items_to_read, initial_item_ids = self._create_records_for_read_items(self.container, 3, "initial")

        read_items_before = self.container.read_items(items=initial_items_to_read)
        self.assertEqual(len(read_items_before), len(initial_item_ids))

        self.key_database.delete_container(container_id)  # control-plane

        # Recreate the container with a different partition key and throughput
        # control-plane container creation
        container_ref = self.key_database.create_container(
            id=container_id,
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=10100
        )
        self.container = self.database.get_container_client(container_ref.id)
        # Force the AAD client to re-read container properties so it caches the
        # new partition key path (/pk instead of /id) and the new RID.
        self.container.read()

        # Create new items with the new partition key structure
        new_items_to_read = []
        new_item_ids = []
        for i in range(5):
            doc_id = f"new_item_{i}_{uuid.uuid4()}"
            pk_value = f"new_pk_{i}"
            new_item_ids.append(doc_id)
            self.container.create_item({'id': doc_id, 'pk': pk_value, 'data': i})
            new_items_to_read.append((doc_id, pk_value))

        read_items_after = self.container.read_items(items=new_items_to_read)
        self.assertEqual(len(read_items_after), len(new_item_ids))
        read_ids = {item['id'] for item in read_items_after}
        self.assertSetEqual(read_ids, set(new_item_ids))
