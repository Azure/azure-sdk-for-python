# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import collections
import unittest
from unittest import mock

import psutil

from azure.monitor.opentelemetry.exporter._performance_counters._cpu import _get_processor_time, _get_process_cpu


class TestCpuCounters(unittest.TestCase):

    @mock.patch("psutil.cpu_times_percent")
    def test_get_processor_time(self, mock_cpu_times_percent):
        # Mock CPU times percent object
        cpu = collections.namedtuple("cpu", "idle")
        cpu_times = cpu(idle=20.0)  # 20% idle = 80% processor time
        mock_cpu_times_percent.return_value = cpu_times
        
        observations = list(_get_processor_time(None))
        self.assertEqual(len(observations), 1)
        self.assertEqual(observations[0].value, 80.0)  # 100 - 20

    @mock.patch("psutil.cpu_times_percent")
    def test_get_processor_time_error(self, mock_cpu_times_percent):
        mock_cpu_times_percent.side_effect = Exception("Test error")
        
        observations = list(_get_processor_time(None))
        self.assertEqual(len(observations), 1)
        self.assertEqual(observations[0].value, 0.0)

    @mock.patch("azure.monitor.opentelemetry.exporter._performance_counters._cpu.PROCESS")
    @mock.patch("psutil.cpu_count")
    def test_get_process_cpu(self, mock_cpu_count, mock_process):
        mock_cpu_count.return_value = 4  # 4 logical CPUs
        mock_process.cpu_percent.return_value = 80.0  # 80% CPU usage
        
        observations = list(_get_process_cpu(None))
        self.assertEqual(len(observations), 1)
        self.assertEqual(observations[0].value, 20.0)  # 80 / 4

    @mock.patch("azure.monitor.opentelemetry.exporter._performance_counters._cpu.PROCESS")
    @mock.patch("psutil.cpu_count")
    def test_get_process_cpu_zero_cpus(self, mock_cpu_count, mock_process):
        mock_cpu_count.return_value = 0  # Edge case
        mock_process.cpu_percent.return_value = 80.0
        
        observations = list(_get_process_cpu(None))
        self.assertEqual(len(observations), 1)
        self.assertEqual(observations[0].value, 0.0)

    @mock.patch("azure.monitor.opentelemetry.exporter._performance_counters._cpu.PROCESS")
    @mock.patch("psutil.cpu_count")
    def test_get_process_cpu_none_cpus(self, mock_cpu_count, mock_process):
        mock_cpu_count.return_value = None  # Edge case
        mock_process.cpu_percent.return_value = 80.0
        
        observations = list(_get_process_cpu(None))
        self.assertEqual(len(observations), 1)
        self.assertEqual(observations[0].value, 0.0)

    @mock.patch("azure.monitor.opentelemetry.exporter._performance_counters._cpu.PROCESS")
    @mock.patch("psutil.cpu_count")
    def test_get_process_cpu_error(self, mock_cpu_count, mock_process):
        mock_cpu_count.return_value = 4
        mock_process.cpu_percent.side_effect = psutil.NoSuchProcess(1)
        
        observations = list(_get_process_cpu(None))
        self.assertEqual(len(observations), 1)
        self.assertEqual(observations[0].value, 0.0)


if __name__ == "__main__":
    unittest.main()
