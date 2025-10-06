# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import collections
import unittest
from unittest import mock

import psutil

from azure.monitor.opentelemetry.exporter._performance_counters._memory import _get_available_memory, _get_process_memory


class TestMemoryCounters(unittest.TestCase):
    
    @mock.patch("psutil.virtual_memory")
    def test_get_available_memory(self, mock_virtual_memory):
        # Mock virtual memory object
        memory = collections.namedtuple("memory", "available")
        vmem = memory(available=1024*1024*1024)  # 1GB
        mock_virtual_memory.return_value = vmem
        
        observations = list(_get_available_memory(None))
        self.assertEqual(len(observations), 1)
        self.assertEqual(observations[0].value, 1024*1024*1024)

    @mock.patch("psutil.virtual_memory")  
    def test_get_available_memory_error(self, mock_virtual_memory):
        mock_virtual_memory.side_effect = Exception("Test error")
        
        observations = list(_get_available_memory(None))
        self.assertEqual(len(observations), 1)
        self.assertEqual(observations[0].value, 0)

    @mock.patch("psutil.Process")
    def test_get_process_memory(self, mock_process_class):
        # Mock process and memory info
        memory = collections.namedtuple("memory", "rss")  
        pmem = memory(rss=100*1024*1024)  # 100MB
        mock_process = mock.Mock()
        mock_process.memory_info.return_value = pmem
        mock_process_class.return_value = mock_process
        
        observations = list(_get_process_memory(None))
        self.assertEqual(len(observations), 1)
        self.assertEqual(observations[0].value, 100*1024*1024)

    @mock.patch("psutil.Process")
    def test_get_process_memory_error(self, mock_process_class):
        mock_process = mock.Mock()
        mock_process.memory_info.side_effect = psutil.NoSuchProcess(1)
        mock_process_class.return_value = mock_process
        
        observations = list(_get_process_memory(None))
        self.assertEqual(len(observations), 1)
        self.assertEqual(observations[0].value, 0)


if __name__ == "__main__":
    unittest.main()
