# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import unittest
from unittest import mock

from opentelemetry.metrics import get_meter_provider
from opentelemetry.sdk.metrics import MeterProvider

from azure.monitor.opentelemetry.exporter._performance_counters import (
    AvailableMemoryMetric,
    ProcessMemoryMetric,
    ProcessorTimeMetric,
    ProcessCpuMetric,
    PerformanceCountersManager,
    setup_performance_counters,
    shutdown_performance_counters,
    get_performance_counters_manager,
)


class TestPerformanceCounters(unittest.TestCase):
    def setUp(self):
        self.meter_provider = MeterProvider()
        self.meter = self.meter_provider.get_meter("test")

    def test_available_memory_metric_init(self):
        metric = AvailableMemoryMetric(self.meter)
        self.assertIsNotNone(metric.gauge)
        self.assertEqual(metric.NAME, r"\Memory\Available Bytes")

    def test_process_memory_metric_init(self):
        metric = ProcessMemoryMetric(self.meter)
        self.assertIsNotNone(metric.gauge)
        self.assertEqual(metric.NAME, r"\Process(??APP_WIN32_PROC??)\Private Bytes")

    def test_processor_time_metric_init(self):
        metric = ProcessorTimeMetric(self.meter)
        self.assertIsNotNone(metric.gauge)
        self.assertEqual(metric.NAME, r"\Processor(_Total)\% Processor Time")

    def test_process_cpu_metric_init(self):
        metric = ProcessCpuMetric(self.meter)
        self.assertIsNotNone(metric.gauge)
        self.assertEqual(metric.NAME, r"\Process(??APP_WIN32_PROC??)\% Processor Time")

    def test_performance_counters_manager_init(self):
        manager = PerformanceCountersManager()
        self.assertTrue(manager.enabled)
        self.assertEqual(len(manager.performance_counters), 0)

    def test_performance_counters_manager_setup(self):
        manager = PerformanceCountersManager()
        manager.setup(self.meter_provider)
        # Should have 4 performance counters
        self.assertEqual(len(manager.performance_counters), 4)
        manager.shutdown()
        self.assertEqual(len(manager.performance_counters), 0)

    def test_performance_counters_manager_setup_disabled(self):
        manager = PerformanceCountersManager()
        manager.setup(self.meter_provider, enabled=False)
        # Should have 0 performance counters when disabled
        self.assertEqual(len(manager.performance_counters), 0)
        self.assertFalse(manager.enabled)

    @mock.patch('azure.monitor.opentelemetry.exporter._performance_counters._manager.metrics.get_meter_provider')
    def test_setup_performance_counters(self, mock_get_meter_provider):
        mock_get_meter_provider.return_value = self.meter_provider
        setup_performance_counters(enabled=True)
        manager = get_performance_counters_manager()
        self.assertTrue(manager.enabled)
        shutdown_performance_counters()

    def test_global_manager_access(self):
        manager1 = get_performance_counters_manager()
        manager2 = get_performance_counters_manager()
        # Should be the same singleton instance
        self.assertEqual(id(manager1), id(manager2))


if __name__ == "__main__":
    unittest.main()
