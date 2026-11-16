# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original callback/result comparisons on Rust, with a test-owned database.

These tests compare callback headers with the same operation's result, not
legacy execution with Rust. Composite cases remain together to retain their
original assertions. No Python HTTP observer is substituted for Rust traffic.
"""

import unittest
import uuid
from collections.abc import Mapping

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
        database_id = "response_hooks_" + uuid.uuid4().hex
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

    def test_query_response_headers_match_last_response_hook_invocation_rust(self):
        # Source: tests/test_query_response_headers.py::TestQueryResponseHeaders.test_query_response_headers_match_last_response_hook_invocation
        container_id = "test_headers_hookparity_" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        try:
            for i in range(12):
                created_collection.create_item(body={"pk": "test", "id": f"item_{i}", "value": i})
            captured_pages = []

            def hook(headers, _result):
                captured_pages.append(dict(headers))

            query_iterable = created_collection.query_items(
                query="SELECT * FROM c WHERE c.pk = @pk",
                parameters=[{"name": "@pk", "value": "test"}],
                partition_key="test", max_item_count=4, response_hook=hook,
            )
            items = list(query_iterable)
            self.assertEqual(len(items), 12)
            self.assertGreater(len(captured_pages), 0)
            final_headers = query_iterable.get_response_headers()
            self.assertEqual(final_headers["x-ms-request-charge"], captured_pages[-1]["x-ms-request-charge"])
            self.assertEqual(final_headers["x-ms-activity-id"], captured_pages[-1]["x-ms-activity-id"])
        finally:
            self._delete_container_for_test(container_id)

    def test_response_hook_parity_query_items_change_feed_rust(self):
        # Source: tests/test_query_response_headers.py::TestQueryResponseHeaders.test_response_hook_parity_query_items_change_feed
        container_id = "test_hookparity_cf_" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        try:
            for i in range(6):
                created_collection.create_item(body={"pk": "test", "id": f"item_{i}"})
            captured = []

            def hook(headers, _result):
                captured.append(dict(headers))

            paged = created_collection.query_items_change_feed(
                start_time="Beginning", max_item_count=2, response_hook=hook,
            )
            items = list(paged)
            self.assertGreaterEqual(len(items), 6)
            self.assertGreater(len(captured), 0, "response_hook must fire at least once")
            self.assertIn("x-ms-request-charge", captured[-1])
            if hasattr(paged, "get_response_headers"):
                final_headers = paged.get_response_headers()
                self.assertIn("x-ms-request-charge", final_headers)
                self.assertEqual(final_headers["x-ms-request-charge"], captured[-1]["x-ms-request-charge"])
        finally:
            self._delete_container_for_test(container_id)

    def test_response_hook_parity_point_ops_rust(self):
        # Source: tests/test_query_response_headers.py::TestQueryResponseHeaders.test_response_hook_parity_point_ops
        container_id = "test_hookparity_point_" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        try:
            captured = []

            def hook(headers, _body):
                captured.append(dict(headers))

            captured.clear()
            created = created_collection.create_item(
                body={"pk": "p", "id": "doc1", "value": 1}, response_hook=hook,
            )
            self.assertEqual(len(captured), 1)
            self.assertEqual(created.get_response_headers()["x-ms-request-charge"],
                             captured[0]["x-ms-request-charge"])
            captured.clear()
            read = created_collection.read_item(item="doc1", partition_key="p", response_hook=hook)
            self.assertEqual(len(captured), 1)
            self.assertEqual(read.get_response_headers()["x-ms-request-charge"],
                             captured[0]["x-ms-request-charge"])
            captured.clear()
            replaced = created_collection.replace_item(
                item="doc1", body={"pk": "p", "id": "doc1", "value": 2}, response_hook=hook,
            )
            self.assertEqual(len(captured), 1)
            self.assertEqual(replaced.get_response_headers()["x-ms-request-charge"],
                             captured[0]["x-ms-request-charge"])
            captured.clear()
            upserted = created_collection.upsert_item(
                body={"pk": "p", "id": "doc1", "value": 3}, response_hook=hook,
            )
            self.assertEqual(len(captured), 1)
            self.assertEqual(upserted.get_response_headers()["x-ms-request-charge"],
                             captured[0]["x-ms-request-charge"])
            captured.clear()
            created_collection.delete_item(item="doc1", partition_key="p", response_hook=hook)
            self.assertEqual(len(captured), 1)
            self.assertIn("x-ms-request-charge", captured[0])
        finally:
            self._delete_container_for_test(container_id)

    def test_response_hook_parity_query_databases_and_query_containers_rust(self):
        # Source: tests/test_query_response_headers.py::TestQueryResponseHeaders.test_response_hook_parity_query_databases_and_query_containers
        captured_db = []

        def hook_db(*args):
            captured_db.append(args[0])

        db_pager = self.client.query_databases(query="SELECT * FROM root r", response_hook=hook_db)
        _ = list(db_pager)
        self.assertEqual(len(captured_db), 1, "query_databases response_hook must fire exactly once")
        self.assertIsInstance(captured_db[0], Mapping)
        captured_c = []

        def hook_c(*args):
            captured_c.append(args[0])

        c_pager = self.created_db.query_containers(query="SELECT * FROM root r", response_hook=hook_c)
        _ = list(c_pager)
        self.assertEqual(len(captured_c), 1, "query_containers response_hook must fire exactly once")
        self.assertIsInstance(captured_c[0], Mapping)

    def test_response_hook_fires_at_least_once_for_every_paged_surface_rust(self):
        # Source: tests/test_query_response_headers.py::TestQueryResponseHeaders.test_response_hook_fires_at_least_once_for_every_paged_surface
        container_id = "test_hookfires_paged_" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        try:
            for i in range(6):
                created_collection.create_item(body={"pk": "test", "id": f"item_{i}"})

            def _run(surface_name, build_pager):
                captured = []

                def hook(headers, _result):
                    captured.append(dict(headers))

                pager = build_pager(hook)
                list(pager)
                self.assertGreater(len(captured), 0, f"{surface_name} response_hook never fired")
                for payload in captured:
                    self.assertIsInstance(payload, Mapping, f"{surface_name} hook received non-Mapping payload")

            _run("query_items", lambda h: created_collection.query_items(
                query="SELECT * FROM c", partition_key="test", response_hook=h,
            ))
            _run("query_items_change_feed", lambda h: created_collection.query_items_change_feed(
                start_time="Beginning", max_item_count=2, response_hook=h,
            ))
        finally:
            self._delete_container_for_test(container_id)

    def test_response_hook_parity_patch_item_rust(self):
        # Source: tests/test_query_response_headers.py::TestQueryResponseHeaders.test_response_hook_parity_patch_item
        container_id = "test_hookparity_patch_" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        try:
            created_collection.create_item(body={"pk": "p", "id": "doc-patch", "value": 1})
            captured = []

            def hook(headers, _body):
                captured.append(dict(headers))

            patched = created_collection.patch_item(
                item="doc-patch", partition_key="p",
                patch_operations=[{"op": "replace", "path": "/value", "value": 99}],
                response_hook=hook,
            )
            self.assertEqual(len(captured), 1)
            patched_headers = patched.get_response_headers()
            self.assertEqual(patched_headers["x-ms-request-charge"], captured[0]["x-ms-request-charge"])
            self.assertEqual(patched_headers["x-ms-activity-id"], captured[0]["x-ms-activity-id"])
            self.assertEqual(patched["value"], 99)
        finally:
            self._delete_container_for_test(container_id)

    def test_response_hook_parity_execute_item_batch_rust(self):
        # Source: tests/test_query_response_headers.py::TestQueryResponseHeaders.test_response_hook_parity_execute_item_batch
        container_id = "test_hookparity_batch_" + str(uuid.uuid4())
        created_collection = self._create_container_for_test(container_id, PartitionKey(path="/pk"))
        try:
            captured = []

            def hook(headers, _body):
                captured.append(dict(headers))

            batch_ops = [
                ("create", ({"pk": "p", "id": "batch-doc-1", "value": 1},)),
                ("upsert", ({"pk": "p", "id": "batch-doc-2", "value": 2},)),
            ]
            result = created_collection.execute_item_batch(
                batch_operations=batch_ops, partition_key="p", response_hook=hook,
            )
            self.assertEqual(len(captured), 1)
            result_headers = result.get_response_headers()
            self.assertEqual(result_headers["x-ms-request-charge"], captured[0]["x-ms-request-charge"])
            self.assertEqual(result_headers["x-ms-activity-id"], captured[0]["x-ms-activity-id"])
            self.assertEqual(len(result), 2)
        finally:
            self._delete_container_for_test(container_id)
