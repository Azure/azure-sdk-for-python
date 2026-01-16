# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import unittest

from azure.monitor.opentelemetry.exporter._performance_counters._constants import (
    _AVAILABLE_MEMORY,
    _EXCEPTION_RATE,
    _REQUEST_EXECUTION_TIME,
    _REQUEST_RATE,
    _PROCESS_CPU,
    _PROCESS_CPU_NORMALIZED,
    _PROCESS_IO_RATE,
    _PROCESS_PRIVATE_BYTES,
    _PROCESSOR_TIME,
    _PERFORMANCE_COUNTER_METRIC_NAME_MAPPINGS,
)
from azure.monitor.opentelemetry.exporter._quickpulse._constants import (
    _QUICKPULSE_METRIC_NAME_MAPPINGS,
)


class TestPerformanceCounterConstants(unittest.TestCase):
    """Test performance counter constants and mappings."""

    def test_available_memory_constant(self):
        """Test available memory constant values."""
        self.assertIsInstance(_AVAILABLE_MEMORY, tuple)
        self.assertEqual(len(_AVAILABLE_MEMORY), 2)
        self.assertEqual(
            _AVAILABLE_MEMORY[0], "azuremonitor.performancecounter.memoryavailablebytes"
        )
        self.assertEqual(_AVAILABLE_MEMORY[1], "\\Memory\\Available Bytes")

    def test_exception_rate_constant(self):
        """Test exception rate constant values."""
        self.assertIsInstance(_EXCEPTION_RATE, tuple)
        self.assertEqual(len(_EXCEPTION_RATE), 2)
        self.assertEqual(
            _EXCEPTION_RATE[0], "azuremonitor.performancecounter.exceptionssec"
        )
        self.assertEqual(
            _EXCEPTION_RATE[1],
            "\\.NET CLR Exceptions(??APP_CLR_PROC??)\\# of Exceps Thrown / sec",
        )

    def test_request_execution_time_constant(self):
        """Test request execution time constant values."""
        self.assertIsInstance(_REQUEST_EXECUTION_TIME, tuple)
        self.assertEqual(len(_REQUEST_EXECUTION_TIME), 2)
        self.assertEqual(
            _REQUEST_EXECUTION_TIME[0],
            "azuremonitor.performancecounter.requestexecutiontime",
        )
        self.assertEqual(
            _REQUEST_EXECUTION_TIME[1],
            "\\ASP.NET Applications(??APP_W3SVC_PROC??)\\Request Execution Time",
        )

    def test_request_rate_constant(self):
        """Test request rate constant values."""
        self.assertIsInstance(_REQUEST_RATE, tuple)
        self.assertEqual(len(_REQUEST_RATE), 2)
        self.assertEqual(
            _REQUEST_RATE[0], "azuremonitor.performancecounter.requestssec"
        )
        self.assertEqual(
            _REQUEST_RATE[1], "\\ASP.NET Applications(??APP_W3SVC_PROC??)\\Requests/Sec"
        )

    def test_process_cpu_constant(self):
        """Test process CPU constant values."""
        self.assertIsInstance(_PROCESS_CPU, tuple)
        self.assertEqual(len(_PROCESS_CPU), 2)
        self.assertEqual(_PROCESS_CPU[0], "azuremonitor.performancecounter.processtime")
        self.assertEqual(
            _PROCESS_CPU[1], "\\Process(??APP_WIN32_PROC??)\\% Processor Time"
        )

    def test_process_cpu_normalized_constant(self):
        """Test process CPU normalized constant values."""
        self.assertIsInstance(_PROCESS_CPU_NORMALIZED, tuple)
        self.assertEqual(len(_PROCESS_CPU_NORMALIZED), 2)
        self.assertEqual(
            _PROCESS_CPU_NORMALIZED[0],
            "azuremonitor.performancecounter.processtimenormalized",
        )
        self.assertEqual(
            _PROCESS_CPU_NORMALIZED[1],
            "\\Process(??APP_WIN32_PROC??)\\% Processor Time Normalized",
        )

    def test_process_io_rate_constant(self):
        """Test process I/O rate constant values."""
        self.assertIsInstance(_PROCESS_IO_RATE, tuple)
        self.assertEqual(len(_PROCESS_IO_RATE), 2)
        self.assertEqual(
            _PROCESS_IO_RATE[0], "azuremonitor.performancecounter.processiobytessec"
        )
        self.assertEqual(
            _PROCESS_IO_RATE[1], "\\Process(??APP_WIN32_PROC??)\\IO Data Bytes/sec"
        )

    def test_process_private_bytes_constant(self):
        """Test process private bytes constant values."""
        self.assertIsInstance(_PROCESS_PRIVATE_BYTES, tuple)
        self.assertEqual(len(_PROCESS_PRIVATE_BYTES), 2)
        self.assertEqual(
            _PROCESS_PRIVATE_BYTES[0],
            "azuremonitor.performancecounter.processprivatebytes",
        )
        self.assertEqual(
            _PROCESS_PRIVATE_BYTES[1], "\\Process(??APP_WIN32_PROC??)\\Private Bytes"
        )

    def test_processor_time_constant(self):
        """Test processor time constant values."""
        self.assertIsInstance(_PROCESSOR_TIME, tuple)
        self.assertEqual(len(_PROCESSOR_TIME), 2)
        self.assertEqual(
            _PROCESSOR_TIME[0],
            "azuremonitor.performancecounter.processortotalprocessortime",
        )
        self.assertEqual(_PROCESSOR_TIME[1], "\\Processor(_Total)\\% Processor Time")

    def test_performance_counter_metric_name_mappings(self):
        """Test the performance counter metric name mappings dictionary."""
        expected_mappings = [
            _AVAILABLE_MEMORY,
            _EXCEPTION_RATE,
            _REQUEST_EXECUTION_TIME,
            _REQUEST_RATE,
            _PROCESS_CPU,
            _PROCESS_CPU_NORMALIZED,
            _PROCESS_IO_RATE,
            _PROCESS_PRIVATE_BYTES,
            _PROCESSOR_TIME,
        ]

        self.assertIsInstance(_PERFORMANCE_COUNTER_METRIC_NAME_MAPPINGS, dict)
        self.assertEqual(
            len(_PERFORMANCE_COUNTER_METRIC_NAME_MAPPINGS), len(expected_mappings)
        )

        for metric_tuple in expected_mappings:
            otel_name, quickpulse_name = metric_tuple
            self.assertIn(otel_name, _PERFORMANCE_COUNTER_METRIC_NAME_MAPPINGS)
            self.assertEqual(
                _PERFORMANCE_COUNTER_METRIC_NAME_MAPPINGS[otel_name], quickpulse_name
            )

    def test_all_constants_are_tuples_with_two_elements(self):
        """Test that all metric constants are tuples with exactly two elements."""
        constants = [
            _AVAILABLE_MEMORY,
            _EXCEPTION_RATE,
            _REQUEST_EXECUTION_TIME,
            _REQUEST_RATE,
            _PROCESS_CPU,
            _PROCESS_CPU_NORMALIZED,
            _PROCESS_IO_RATE,
            _PROCESS_PRIVATE_BYTES,
            _PROCESSOR_TIME,
        ]

        for constant in constants:
            with self.subTest(constant=constant):
                self.assertIsInstance(constant, tuple)
                self.assertEqual(len(constant), 2)
                self.assertIsInstance(constant[0], str)
                self.assertIsInstance(constant[1], str)

    def test_opentelemetry_metric_names_are_unique(self):
        """Test that all OpenTelemetry metric names are unique."""
        constants = [
            _AVAILABLE_MEMORY,
            _EXCEPTION_RATE,
            _REQUEST_EXECUTION_TIME,
            _REQUEST_RATE,
            _PROCESS_CPU,
            _PROCESS_CPU_NORMALIZED,
            _PROCESS_IO_RATE,
            _PROCESS_PRIVATE_BYTES,
            _PROCESSOR_TIME,
        ]

        otel_names = [constant[0] for constant in constants]
        unique_names = set(otel_names)

        self.assertEqual(
            len(otel_names),
            len(unique_names),
            "Duplicate OpenTelemetry metric names found",
        )

    def test_quickpulse_perf_counters_unique_otel(self):
        """Test that all Quickpulse and Performance Counters metric names are unique."""
        # Note that the breeze names of Performance Counters and Quickpulse may overlap as they are sent to different endpoints
        for perf_counter_otel in _PERFORMANCE_COUNTER_METRIC_NAME_MAPPINGS:
            self.assertNotIn(perf_counter_otel, _QUICKPULSE_METRIC_NAME_MAPPINGS)

    def test_opentelemetry_metric_names_follow_convention(self):
        """Test that all OpenTelemetry metric names follow the expected convention."""
        constants = [
            _AVAILABLE_MEMORY,
            _EXCEPTION_RATE,
            _REQUEST_EXECUTION_TIME,
            _REQUEST_RATE,
            _PROCESS_CPU,
            _PROCESS_CPU_NORMALIZED,
            _PROCESS_IO_RATE,
            _PROCESS_PRIVATE_BYTES,
            _PROCESSOR_TIME,
        ]

        expected_prefix = "azuremonitor.performancecounter."

        for constant in constants:
            otel_name = constant[0]
            with self.subTest(metric_name=otel_name):
                self.assertTrue(
                    otel_name.startswith(expected_prefix),
                    f"Metric name '{otel_name}' does not start with '{expected_prefix}'",
                )
                # Check that it doesn't end with the prefix (i.e., has additional content)
                self.assertGreater(
                    len(otel_name),
                    len(expected_prefix),
                    f"Metric name '{otel_name}' is too short",
                )

    def test_quickpulse_metric_names_follow_convention(self):
        """Test that all Quickpulse metric names follow the expected Windows performance counter convention."""
        constants = [
            _AVAILABLE_MEMORY,
            _EXCEPTION_RATE,
            _REQUEST_EXECUTION_TIME,
            _REQUEST_RATE,
            _PROCESS_CPU,
            _PROCESS_CPU_NORMALIZED,
            _PROCESS_IO_RATE,
            _PROCESS_PRIVATE_BYTES,
            _PROCESSOR_TIME,
        ]

        for constant in constants:
            quickpulse_name = constant[1]
            with self.subTest(metric_name=quickpulse_name):
                # All should start with backslash (Windows performance counter format)
                self.assertTrue(
                    quickpulse_name.startswith("\\"),
                    f"Quickpulse name '{quickpulse_name}' does not start with '\\'",
                )
                # Should contain at least one more backslash (category\\counter format)
                backslash_count = quickpulse_name.count("\\")
                self.assertGreaterEqual(
                    backslash_count,
                    2,
                    f"Quickpulse name '{quickpulse_name}' doesn't follow \\Category\\Counter format",
                )
