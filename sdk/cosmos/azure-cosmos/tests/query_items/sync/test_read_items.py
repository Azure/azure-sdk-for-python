# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Rust-path copy of the sync read_items multi-partition test that exercises query_items.

The original creates a multi-partition container, checks item distribution with a
``partition_key_range_id`` query per physical range, then calls ``read_items`` with a
response hook. Setup is test-owned: a uniquely named database replaces the shared one,
and the key-auth/data client pair are both Rust-backed. Steps and assertions are unchanged.
"""

import os
import unittest
import uuid

import pytest

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos import PartitionKey


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
class TestReadItems(unittest.TestCase):
    """Rust-path copies of tests/test_read_items.py::TestReadItems."""

    host = os.environ.get("ACCOUNT_HOST")
    masterKey = os.environ.get("ACCOUNT_KEY")

    @classmethod
    def setUpClass(cls):
        cls.TEST_DATABASE_ID = "query_items_read_items_" + uuid.uuid4().hex
        # key-auth client for control-plane operations, and a separate data-plane client,
        # like the original create_test_clients pair.
        cls.key_client = cosmos_client.CosmosClient(cls.host, cls.masterKey, _backend="rust")
        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey, _backend="rust")
        cls.key_database = cls.key_client.create_database(cls.TEST_DATABASE_ID)
        cls.database = cls.client.get_database_client(cls.TEST_DATABASE_ID)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.key_client.delete_database(cls.TEST_DATABASE_ID)
        finally:
            cls.client.close()
            cls.key_client.close()

    def test_read_items_multiple_physical_partitions_and_hook_rust(self):
        # Source: tests/test_read_items.py::TestReadItems.test_read_items_multiple_physical_partitions_and_hook
        """Tests read_items on a container with multiple physical partitions and verifies response_hook."""
        pytest.skip(
            "internals-only: the original queries each physical partition through the internal "
            "partition_key_range_id keyword and _ReadPartitionKeyRanges; the Rust query path does not "
            "accept partition_key_range_id."
        )
        container_id = 'multi_partition_container_' + str(uuid.uuid4())
        # Create a container with high throughput to force multiple physical partitions
        # control-plane container creation
        self.key_database.create_container(
            id=container_id,
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=11000
        )
        multi_partition_container = self.database.get_container_client(container_id)
        try:
            # 1. Verify that we have more than one physical partition
            pk_ranges = list(multi_partition_container.client_connection._ReadPartitionKeyRanges(
                multi_partition_container.container_link))
            self.assertGreater(len(pk_ranges), 1, "Container should have multiple physical partitions.")

            # 2. Create items across different logical partitions
            items_to_read = []
            all_item_ids = set()
            for i in range(200):
                doc_id = f"item_{i}_{uuid.uuid4()}"
                pk = i % 2
                all_item_ids.add(doc_id)
                multi_partition_container.create_item({'id': doc_id, 'pk': pk, 'data': i})
                items_to_read.append((doc_id, pk))

            # 3. Check item distribution across physical partitions
            partition_item_map = {}
            for pk_range in pk_ranges:
                pk_range_id = pk_range['id']
                # Query items within this specific physical partition
                items_in_partition = list(multi_partition_container.query_items(
                    "SELECT c.id FROM c",
                    partition_key_range_id=pk_range_id
                ))
                if items_in_partition:
                    partition_item_map[pk_range_id] = {item['id'] for item in items_in_partition}

            # Assert that items were created on more than one physical partition
            self.assertGreater(len(partition_item_map), 1,
                               "Items were not distributed across multiple physical partitions.")

            # 3. Set up a response hook to capture both headers and results
            hook_captured_data = {}

            def response_hook(headers, results_list):
                hook_captured_data['headers'] = headers
                hook_captured_data['results'] = results_list
                hook_captured_data['call_count'] = hook_captured_data.get('call_count', 0) + 1

            # 4. Execute read_items with the hook
            read_items_result = multi_partition_container.read_items(
                items=items_to_read,
                response_hook=response_hook
            )

            # 5. Verify the response_hook was called correctly
            self.assertEqual(hook_captured_data.get('call_count'), 1, "Response hook should be called exactly once.")

            # Verify the headers passed to the hook
            hook_headers = hook_captured_data.get('headers', {})
            self.assertIn('x-ms-request-charge', hook_headers)
            self.assertGreater(float(hook_headers['x-ms-request-charge']), 0)

            # Verify the CosmosList passed to the hook
            hook_results = hook_captured_data.get('results')
            self.assertIsNotNone(hook_results, "CosmosList should be passed to the hook.")
            self.assertIsInstance(hook_results, list)  # CosmosList inherits from list
            self.assertEqual(len(hook_results), len(items_to_read))
            hook_read_ids = {item['id'] for item in hook_results}
            self.assertSetEqual(hook_read_ids, all_item_ids)

            # Verify that the CosmosList passed to the hook is the same object as the one returned
            self.assertIs(read_items_result, hook_results)

        finally:
            try:
                self.key_database.delete_container(container_id)  # control-plane
            except exceptions.CosmosHttpResponseError as e:
                if e.status_code != 404:
                    raise


if __name__ == '__main__':
    unittest.main()
