# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Sync ``read_items`` contract tests against the ``_backend="rust"`` path.

Self-contained: builds its own database + container in ``setUp`` and deletes them
in ``tearDown``; methods that need a different partition-key shape build (and
delete) their own container. The class and method names match the source at
``tests/test_read_items.py`` so test IDs differ only by path.

These pin the customer-facing contract of ``read_items`` -- missing items omitted,
single vs multi item, different / hierarchical partition keys, the aggregated
request-charge header, and input-order preservation -- so an absolute regression
is caught even when the two backends agree with each other.

Not copied here (and why): the fault-injection tests
(``test_read_items_surfaces_exceptions``, ``test_read_failure_preserves_headers``,
``test_read_items_with_throttling_retry``, ``test_read_items_with_gone_retry``)
build a client with a core-python ``FaultInjectionTransport`` that the rust
backend does not route through, so a fault cannot be injected on the rust path;
``test_read_items_concurrency_internals`` patches an internal method; and the
very large / multi-physical-partition cases reach into client internals or are
prohibitively slow against a live account.

Run with::

    pytest --noconftest tests/read_items/sync/legacy/test_read_items.py -v
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
class TestReadItems(unittest.TestCase):
    """read_items on a Rust-backed client: each test seeds its own container, runs
    the batched read, and checks the customer-visible contract (which documents
    come back, in what order, and the aggregated request-charge header)."""

    def setUp(self):
        self.client = CosmosClient(HOST, KEY, _backend="rust")
        self._db_id = "legacy_read_items_sync_" + uuid.uuid4().hex[:8]
        self.database = self.client.create_database(self._db_id)
        container_ref = self.database.create_container(
            id="read_items_container_" + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/id"),
        )
        self.container = self.database.get_container_client(container_ref.id)

    def tearDown(self):
        try:
            self.client.delete_database(self._db_id)
        except Exception:  # pylint: disable=broad-except
            pass

    @staticmethod
    def _create_records_for_read_items(container, count, id_prefix="item"):
        # Seed `count` documents and return the (id, pk) pairs to read back plus the
        # ids alone; the container is keyed on /id, so each id doubles as its own pk.
        items_to_read = []
        item_ids = []
        for i in range(count):
            doc_id = f"{id_prefix}_{i}_{uuid.uuid4()}"
            item_ids.append(doc_id)
            items_to_read.append((doc_id, doc_id))
            container.create_item({'id': doc_id, 'data': i})
        return items_to_read, item_ids

    def test_read_items_single_item(self):
        """One (id, pk) pair in the batch -> read_items returns exactly that one document."""
        # Source: tests/test_read_items.py::TestReadItems.test_read_items_single_item
        items_to_read, item_ids = self._create_records_for_read_items(self.container, 1)
        read_items = self.container.read_items(items=items_to_read)
        self.assertEqual(len(read_items), 1)
        self.assertEqual(read_items[0]['id'], item_ids[0])

    def test_read_items_with_missing_items(self):
        """A batch mixing real and non-existent ids -> only the real documents come back; missing ids are omitted, not errors."""
        # Source: tests/test_read_items.py::TestReadItems.test_read_items_with_missing_items
        items_to_read, _ = self._create_records_for_read_items(self.container, 3, "existing_item")
        items_to_read.append(("non_existent_item1" + str(uuid.uuid4()), "non_existent_pk1"))
        items_to_read.append(("non_existent_item2" + str(uuid.uuid4()), "non_existent_pk2"))
        read_items = self.container.read_items(items=items_to_read)
        self.assertEqual(len(read_items), 3)
        returned_ids = {item['id'] for item in read_items}
        expected_ids = {item_tuple[0] for item_tuple in items_to_read if "existing" in item_tuple[0]}
        self.assertSetEqual(returned_ids, expected_ids)

    def test_read_items_different_partition_key(self):
        """Partition key on its own path (/pk, not /id) -> read_items still finds every requested document."""
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

    def test_read_items_fails_with_incomplete_hierarchical_pk(self):
        """A hierarchical partition key with too few components -> read_items raises ValueError before any network call."""
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
            self.assertIn("Number of components in partition key value (1) does not match definition (2)",
                          str(context.exception))
        finally:
            self.database.delete_container(container_id)

    def test_read_items_hierarchical_partition_key(self):
        """Two-level (tenantId, userId) partition key -> read_items returns every requested document."""
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

    def test_read_items_with_no_results_preserve_headers(self):
        """All ids non-existent -> an empty result, but the aggregated x-ms-request-charge header is still present and non-zero."""
        # Source: tests/test_read_items.py::TestReadItems.test_read_items_with_no_results_preserve_headers
        items_to_read = [
            ("non_existent_item_1_" + str(uuid.uuid4()), "non_existent_pk_1"),
            ("non_existent_item_2_" + str(uuid.uuid4()), "non_existent_pk_2"),
        ]
        read_items = self.container.read_items(items=items_to_read)
        headers = read_items.get_response_headers()
        self.assertEqual(len(read_items), 0)
        self.assertListEqual(list(headers.keys()), ['x-ms-request-charge'])
        self.assertGreater(float(headers.get('x-ms-request-charge')), 0)

    def test_headers_being_returned_on_success(self):
        """On success the merged result exposes only the aggregated x-ms-request-charge header (the summed RU cost of all the leaf reads)."""
        # Source: tests/test_read_items.py::TestReadItems.test_headers_being_returned_on_success
        items_to_read, item_ids = self._create_records_for_read_items(self.container, 5)
        read_items = self.container.read_items(items=items_to_read)
        headers = read_items.get_response_headers()
        self.assertEqual(len(read_items), len(item_ids))
        self.assertIsNotNone(headers)
        self.assertListEqual(list(headers.keys()), ['x-ms-request-charge'])
        self.assertGreater(float(headers.get('x-ms-request-charge')), 0)

    def test_read_items_order_using_zip_comparison(self):
        """The returned documents come back in the same order as the input (id, pk) list."""
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
