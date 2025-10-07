# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock
from azure.cosmos._read_items_helper import ReadItemsHelperSync


class TestMaxConcurrency(unittest.TestCase):
    """Unit tests for max_concurrency parameter behavior."""

    def test_max_concurrency_none_uses_default(self):
        """Test that max_concurrency=None uses ThreadPoolExecutor's default."""
        # Mock client connection
        mock_client = Mock()
        mock_client._routing_map_provider = Mock()
        mock_client._routing_map_provider.get_overlapping_ranges = Mock(return_value=[])
        
        # Create helper with max_concurrency=None
        helper = ReadItemsHelperSync(
            client=mock_client,
            collection_link="/dbs/test/colls/test",
            items=[],
            options={},
            partition_key_definition={"paths": ["/id"], "kind": "Hash"},
            max_concurrency=None
        )
        
        # Verify that max_concurrency is None
        self.assertIsNone(helper.max_concurrency)
        
    def test_max_concurrency_value_is_preserved(self):
        """Test that explicit max_concurrency value is preserved."""
        # Mock client connection
        mock_client = Mock()
        mock_client._routing_map_provider = Mock()
        
        # Create helper with explicit max_concurrency
        helper = ReadItemsHelperSync(
            client=mock_client,
            collection_link="/dbs/test/colls/test",
            items=[],
            options={},
            partition_key_definition={"paths": ["/id"], "kind": "Hash"},
            max_concurrency=5
        )
        
        # Verify that max_concurrency is set correctly
        self.assertEqual(helper.max_concurrency, 5)


if __name__ == '__main__':
    unittest.main()
