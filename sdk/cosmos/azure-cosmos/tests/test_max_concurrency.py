# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import os
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, patch
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

    def test_max_concurrency_ignored_with_executor(self):
        """Test that max_concurrency is ignored if an executor is provided."""
        # Mock client connection
        mock_client = Mock()
        mock_client._routing_map_provider = Mock()
        mock_client._routing_map_provider.get_overlapping_ranges = Mock(return_value=[])
        
        # Create a mock executor
        mock_executor = Mock(spec=ThreadPoolExecutor)
        
        # Create helper with both executor and max_concurrency
        helper = ReadItemsHelperSync(
            client=mock_client,
            collection_link="/dbs/test/colls/test",
            items=[],
            options={},
            partition_key_definition={"paths": ["/id"], "kind": "Hash"},
            executor=mock_executor,
            max_concurrency=5
        )
        
        # Verify that executor is set and max_concurrency is preserved
        self.assertEqual(helper.executor, mock_executor)
        self.assertEqual(helper.max_concurrency, 5)
        
        # When read_items is called with empty items, it returns early
        # But we can verify the executor is stored
        result = helper.read_items()
        self.assertIsNotNone(result)

    def test_default_max_concurrency_uses_python_default(self):
        """Test that if max_concurrency not specified, defaults to Python's ThreadPoolExecutor default."""
        # Get Python's default calculation
        cpu_count = os.cpu_count() or 1
        expected_default = min(32, cpu_count + 4)
        
        # Create a ThreadPoolExecutor with None to see what Python uses
        with ThreadPoolExecutor(max_workers=None) as executor:
            actual_workers = executor._max_workers
            
        # Verify the expected default matches Python's calculation
        self.assertEqual(actual_workers, expected_default)
        
        # Now verify that our helper will pass None to ThreadPoolExecutor
        mock_client = Mock()
        mock_client._routing_map_provider = Mock()
        mock_client._routing_map_provider.get_overlapping_ranges = Mock(return_value=[])
        
        helper = ReadItemsHelperSync(
            client=mock_client,
            collection_link="/dbs/test/colls/test",
            items=[],
            options={},
            partition_key_definition={"paths": ["/id"], "kind": "Hash"},
            max_concurrency=None
        )
        
        # Verify None is passed through
        self.assertIsNone(helper.max_concurrency)


if __name__ == '__main__':
    unittest.main()
