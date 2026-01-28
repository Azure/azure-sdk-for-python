# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import collections
import unittest
from datetime import datetime
from unittest import mock
from unittest.mock import MagicMock
import psutil

from opentelemetry.semconv.attributes.exception_attributes import (
    EXCEPTION_MESSAGE,
    EXCEPTION_TYPE,
)
from opentelemetry.trace import SpanKind
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk._logs import ReadableLogRecord
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import InMemoryMetricReader

from azure.monitor.opentelemetry.exporter._performance_counters._manager import (
    _get_process_cpu,
    _get_process_cpu_normalized,
    _get_available_memory,
    _get_process_memory,
    _get_process_io,
    _get_processor_time,
    _get_request_rate,
    _get_exception_rate,
    _get_cpu_times_total,
    _PerformanceCountersManager,
    AvailableMemory,
    ExceptionRate,
    RequestExecutionTime,
    RequestRate,
    ProcessCpu,
    ProcessCpuNormalized,
    ProcessIORate,
    ProcessPrivateBytes,
    ProcessorTime,
    PERFORMANCE_COUNTER_METRICS,
    enable_performance_counters,
)
from azure.monitor.opentelemetry.exporter._utils import Singleton


# pylint: disable=protected-access, docstring-missing-param
class TestPerformanceCounterFunctions(unittest.TestCase):
    """Test individual performance counter callback functions."""

    def setUp(self):
        """Reset global state before each test."""
        # Import the module to reset globals
        import azure.monitor.opentelemetry.exporter._performance_counters._manager as manager_module

        # pylint: disable=protected-access
        # TODO: _PROCESS.io_counters() is not available on Mac OS and some Linux distros. Find alternative.
        manager_module._IO_AVAILABLE = True
        manager_module._IO_LAST_COUNT = 0
        manager_module._IO_LAST_TIME = datetime.now()
        manager_module._REQUESTS_COUNT = 0
        manager_module._EXCEPTIONS_COUNT = 0
        manager_module._LAST_REQUEST_RATE_TIME = datetime.now()
        manager_module._LAST_EXCEPTION_RATE_TIME = datetime.now()

    @mock.patch("azure.monitor.opentelemetry.exporter._performance_counters._manager._PROCESS")
    def test_get_process_cpu_success(self, mock_process):
        """Test successful process CPU retrieval."""
        mock_process.cpu_percent.return_value = 25.5

        result = list(_get_process_cpu(None))

        self.assertEqual(len(result), 1)
        self.assertAlmostEqual(result[0].value, 25.5)
        mock_process.cpu_percent.assert_called_once_with(interval=None)

    @mock.patch("azure.monitor.opentelemetry.exporter._performance_counters._manager._PROCESS")
    def test_get_process_cpu_error(self, mock_process):
        """Test process CPU retrieval with error."""
        mock_process.cpu_percent.side_effect = psutil.NoSuchProcess(1)

        result = list(_get_process_cpu(None))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].value, 0.0)

    @mock.patch("azure.monitor.opentelemetry.exporter._performance_counters._manager.NUM_CPUS", 4)
    @mock.patch("azure.monitor.opentelemetry.exporter._performance_counters._manager._PROCESS_FOR_CPU_NORMALIZED")
    def test_get_process_cpu_normalized_success(self, mock_process):
        """Test successful normalized process CPU retrieval."""
        mock_process.cpu_percent.return_value = 80.0

        result = list(_get_process_cpu_normalized(None))

        self.assertEqual(len(result), 1)
        self.assertAlmostEqual(result[0].value, 20.0)  # 80 / 4 CPUs
        mock_process.cpu_percent.assert_called_once_with(interval=None)

    @mock.patch("azure.monitor.opentelemetry.exporter._performance_counters._manager.NUM_CPUS", 0)
    def test_get_process_cpu_normalized_no_cpus(self):
        """Test normalized process CPU with no CPUs."""
        result = list(_get_process_cpu_normalized(None))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].value, 0.0)

    @mock.patch("psutil.virtual_memory")
    def test_get_available_memory_success(self, mock_virtual_memory):
        """Test successful available memory retrieval."""
        mock_memory = MagicMock()
        mock_memory.available = 1073741824  # 1GB
        mock_virtual_memory.return_value = mock_memory

        result = list(_get_available_memory(None))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].value, 1073741824)

    @mock.patch("psutil.virtual_memory")
    def test_get_available_memory_error(self, mock_virtual_memory):
        """Test available memory retrieval with error."""
        mock_virtual_memory.side_effect = Exception("Memory error")

        result = list(_get_available_memory(None))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].value, 0)

    @mock.patch("azure.monitor.opentelemetry.exporter._performance_counters._manager._PROCESS")
    def test_get_process_memory_success(self, mock_process):
        """Test successful process memory retrieval."""
        mock_memory_info = MagicMock()
        mock_memory_info.rss = 52428800  # 50MB
        mock_process.memory_info.return_value = mock_memory_info

        result = list(_get_process_memory(None))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].value, 52428800)

    @mock.patch("azure.monitor.opentelemetry.exporter._performance_counters._manager._PROCESS")
    def test_get_process_memory_error(self, mock_process):
        """Test process memory retrieval with error."""
        mock_process.memory_info.side_effect = psutil.AccessDenied(1)

        result = list(_get_process_memory(None))

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].value, 0)

    @mock.patch("azure.monitor.opentelemetry.exporter._performance_counters._manager.datetime")
    @mock.patch("azure.monitor.opentelemetry.exporter._performance_counters._manager._PROCESS")
    def test_get_process_io_success(self, mock_process, mock_datetime):
        """Test successful process I/O retrieval."""
        # Setup mock I/O counters
        mock_io_counters = MagicMock()
        mock_io_counters.read_bytes = 2000
        mock_io_counters.write_bytes = 3000

        mock_process.io_counters.return_value = mock_io_counters

        # Setup time mocks
        start_time = datetime(2023, 1, 1, 12, 0, 0)
        end_time = datetime(2023, 1, 1, 12, 0, 2)  # 2 seconds later

        mock_datetime.now.return_value = end_time

        # Import and modify global variables
        import azure.monitor.opentelemetry.exporter._performance_counters._manager as manager_module

        manager_module._IO_LAST_COUNT = 3000  # Previous total
        manager_module._IO_LAST_TIME = start_time

        result = list(_get_process_io(None))

        self.assertEqual(len(result), 1)
        # Expected: (5000 - 3000) / 2 seconds = 1000 bytes/sec
        self.assertAlmostEqual(result[0].value, 1000.0)

    @mock.patch("azure.monitor.opentelemetry.exporter._performance_counters._manager.datetime")
    @mock.patch("azure.monitor.opentelemetry.exporter._performance_counters._manager._PROCESS")
    def test_get_process_io_unavailable(self, mock_process, mock_datetime):
        """Test unavailable process I/O retrieval."""
        # Setup unavailable I/O counters
        mock_process.io_counters.side_effect = AttributeError("'Process' object has no attribute 'io_counters'")

        # Setup time mocks
        start_time = datetime(2023, 1, 1, 12, 0, 0)
        end_time = datetime(2023, 1, 1, 12, 0, 2)  # 2 seconds later

        mock_datetime.now.return_value = end_time

        # Import and modify global variables
        import azure.monitor.opentelemetry.exporter._performance_counters._manager as manager_module

        manager_module._IO_AVAILABLE = 0  # Previous total
        manager_module._IO_LAST_COUNT = 0  # Previous total
        manager_module._IO_LAST_TIME = start_time

        result = list(_get_process_io(None))

        self.assertEqual(len(result), 1)
        self.assertAlmostEqual(result[0].value, 0.0)

    @mock.patch("psutil.cpu_times")
    def test_get_processor_time_success(self, mock_cpu_times):
        """Test successful processor time retrieval."""
        # Create mock CPU times
        CpuTimes = collections.namedtuple("CpuTimes", ["user", "system", "idle", "nice"])

        # First call (stored in _LAST_CPU_TIMES)
        first_times = CpuTimes(user=10.0, system=5.0, idle=80.0, nice=1.0)
        # Second call (current)
        second_times = CpuTimes(user=15.0, system=7.0, idle=85.0, nice=1.5)

        mock_cpu_times.return_value = second_times

        # Import and set up global state
        import azure.monitor.opentelemetry.exporter._performance_counters._manager as manager_module

        manager_module._LAST_CPU_TIMES = first_times

        result = list(_get_processor_time(None))

        self.assertEqual(len(result), 1)
        # Calculate expected utilization
        # Total delta: (15+7+85+1.5) - (10+5+80+1) = 108.5 - 96 = 12.5
        # Idle delta: 85 - 80 = 5
        # Utilization: 100 * (12.5 - 5) / 12.5 = 60%
        self.assertAlmostEqual(result[0].value, 60.0, places=1)

    def test_get_cpu_times_total(self):
        """Test CPU times total calculation."""
        CpuTimes = collections.namedtuple("CpuTimes", ["user", "system", "idle", "nice", "iowait", "irq", "softirq"])
        cpu_times = CpuTimes(user=10.0, system=5.0, idle=80.0, nice=1.0, iowait=2.0, irq=0.5, softirq=0.8)

        total = _get_cpu_times_total(cpu_times)

        expected = 10.0 + 5.0 + 80.0 + 1.0 + 2.0 + 0.5 + 0.8
        self.assertAlmostEqual(total, expected)

    @mock.patch("azure.monitor.opentelemetry.exporter._performance_counters._manager.datetime")
    def test_get_request_rate_success(self, mock_datetime):
        """Test successful request rate calculation."""
        start_time = datetime(2023, 1, 1, 12, 0, 0)
        end_time = datetime(2023, 1, 1, 12, 0, 5)  # 5 seconds later

        mock_datetime.now.side_effect = [end_time, end_time]

        # Import and set up global state
        import azure.monitor.opentelemetry.exporter._performance_counters._manager as manager_module

        manager_module._REQUESTS_COUNT = 10
        manager_module._LAST_REQUEST_RATE_TIME = start_time

        result = list(_get_request_rate(None))

        self.assertEqual(len(result), 1)
        # Expected: 10 requests / 5 seconds = 2 req/sec
        self.assertAlmostEqual(result[0].value, 2.0)

        # Check that globals were reset
        self.assertEqual(manager_module._REQUESTS_COUNT, 0)

    @mock.patch("azure.monitor.opentelemetry.exporter._performance_counters._manager.datetime")
    def test_get_exception_rate_success(self, mock_datetime):
        """Test successful exception rate calculation."""
        start_time = datetime(2023, 1, 1, 12, 0, 0)
        end_time = datetime(2023, 1, 1, 12, 0, 10)  # 10 seconds later

        mock_datetime.now.side_effect = [end_time, end_time]

        # Import and set up global state
        import azure.monitor.opentelemetry.exporter._performance_counters._manager as manager_module

        manager_module._EXCEPTIONS_COUNT = 5
        manager_module._LAST_EXCEPTION_RATE_TIME = start_time

        result = list(_get_exception_rate(None))

        self.assertEqual(len(result), 1)
        # Expected: 5 exceptions / 10 seconds = 0.5 exc/sec
        self.assertAlmostEqual(result[0].value, 0.5)

        # Check that globals were reset
        self.assertEqual(manager_module._EXCEPTIONS_COUNT, 0)


class TestPerformanceCounterClasses(unittest.TestCase):
    """Test performance counter metric classes."""

    def setUp(self):
        """Set up test meter."""
        self.meter_provider = MeterProvider()
        self.meter = self.meter_provider.get_meter("test")

    def test_available_memory_initialization(self):
        """Test AvailableMemory class initialization."""
        counter = AvailableMemory(self.meter)

        self.assertIsNotNone(counter.gauge)
        self.assertEqual(counter.NAME[0], "azuremonitor.performancecounter.memoryavailablebytes")
        self.assertEqual(counter.NAME[1], "\\Memory\\Available Bytes")

    def test_exception_rate_initialization(self):
        """Test ExceptionRate class initialization."""
        counter = ExceptionRate(self.meter)

        self.assertIsNotNone(counter.gauge)
        self.assertEqual(counter.NAME[0], "azuremonitor.performancecounter.exceptionssec")
        self.assertEqual(counter.NAME[1], "\\.NET CLR Exceptions(??APP_CLR_PROC??)\\# of Exceps Thrown / sec")

    def test_request_execution_time_initialization(self):  # pylint: disable=name-too-long
        """Test RequestExecutionTime class initialization."""
        counter = RequestExecutionTime(self.meter)

        self.assertIsNotNone(counter.gauge)
        self.assertEqual(counter.NAME[0], "azuremonitor.performancecounter.requestexecutiontime")
        self.assertEqual(counter.NAME[1], "\\ASP.NET Applications(??APP_W3SVC_PROC??)\\Request Execution Time")

    def test_request_rate_initialization(self):
        """Test RequestRate class initialization."""
        counter = RequestRate(self.meter)

        self.assertIsNotNone(counter.gauge)
        self.assertEqual(counter.NAME[0], "azuremonitor.performancecounter.requestssec")
        self.assertEqual(counter.NAME[1], "\\ASP.NET Applications(??APP_W3SVC_PROC??)\\Requests/Sec")

    def test_process_cpu_initialization(self):
        """Test ProcessCpu class initialization."""
        counter = ProcessCpu(self.meter)

        self.assertIsNotNone(counter.gauge)
        self.assertEqual(counter.NAME[0], "azuremonitor.performancecounter.processtime")
        self.assertEqual(counter.NAME[1], "\\Process(??APP_WIN32_PROC??)\\% Processor Time")

    def test_process_cpu_normalized_initialization(self):  # pylint: disable=name-too-long
        """Test ProcessCpuNormalized class initialization."""
        counter = ProcessCpuNormalized(self.meter)

        self.assertIsNotNone(counter.gauge)
        self.assertEqual(counter.NAME[0], "azuremonitor.performancecounter.processtimenormalized")
        self.assertEqual(counter.NAME[1], "\\Process(??APP_WIN32_PROC??)\\% Processor Time Normalized")

    def test_process_io_rate_initialization(self):
        """Test ProcessIORate class initialization."""
        counter = ProcessIORate(self.meter)

        self.assertIsNotNone(counter.gauge)
        self.assertEqual(counter.NAME[0], "azuremonitor.performancecounter.processiobytessec")
        self.assertEqual(counter.NAME[1], "\\Process(??APP_WIN32_PROC??)\\IO Data Bytes/sec")

    def test_process_private_bytes_initialization(self):  # pylint: disable=name-too-long
        """Test ProcessPrivateBytes class initialization."""
        counter = ProcessPrivateBytes(self.meter)

        self.assertIsNotNone(counter.gauge)
        self.assertEqual(counter.NAME[0], "azuremonitor.performancecounter.processprivatebytes")
        self.assertEqual(counter.NAME[1], "\\Process(??APP_WIN32_PROC??)\\Private Bytes")

    def test_processor_time_initialization(self):
        """Test ProcessorTime class initialization."""
        counter = ProcessorTime(self.meter)

        self.assertIsNotNone(counter.gauge)
        self.assertEqual(counter.NAME[0], "azuremonitor.performancecounter.processortotalprocessortime")
        self.assertEqual(counter.NAME[1], "\\Processor(_Total)\\% Processor Time")


class TestPerformanceCountersManager(unittest.TestCase):
    """Test the performance counters manager."""

    def setUp(self):
        """Reset singleton before each test."""
        # Clear the singleton instance using the Singleton metaclass
        if _PerformanceCountersManager in Singleton._instances:
            del Singleton._instances[_PerformanceCountersManager]

    def tearDown(self):
        """Clean up after each test."""
        # Clear the singleton instance using the Singleton metaclass
        if _PerformanceCountersManager in Singleton._instances:
            del Singleton._instances[_PerformanceCountersManager]

    @mock.patch("azure.monitor.opentelemetry.exporter._performance_counters._manager._IO_AVAILABLE", True)
    @mock.patch("azure.monitor.opentelemetry.exporter._performance_counters._manager.metrics.get_meter_provider")
    def test_manager_initialization_success(self, mock_get_meter_provider):
        """Test successful manager initialization."""
        mock_meter_provider = MagicMock()
        mock_meter = MagicMock()
        mock_meter_provider.get_meter.return_value = mock_meter
        mock_get_meter_provider.return_value = mock_meter_provider

        # Mock create_observable_gauge and create_histogram to return mock objects
        mock_meter.create_observable_gauge.return_value = MagicMock()
        mock_meter.create_histogram.return_value = MagicMock()

        manager = _PerformanceCountersManager()

        self.assertEqual(len(manager._performance_counters), len(PERFORMANCE_COUNTER_METRICS))
        mock_meter_provider.get_meter.assert_called_once()

    @mock.patch("azure.monitor.opentelemetry.exporter._performance_counters._manager._IO_AVAILABLE", False)
    @mock.patch("azure.monitor.opentelemetry.exporter._performance_counters._manager.metrics.get_meter_provider")
    def test_manager_initialization_success_no_io(self, mock_get_meter_provider):  # pylint: disable=name-too-long
        """Test successful manager initialization."""
        mock_meter_provider = MagicMock()
        mock_meter = MagicMock()
        mock_meter_provider.get_meter.return_value = mock_meter
        mock_get_meter_provider.return_value = mock_meter_provider

        # Mock create_observable_gauge and create_histogram to return mock objects
        mock_meter.create_observable_gauge.return_value = MagicMock()
        mock_meter.create_histogram.return_value = MagicMock()

        manager = _PerformanceCountersManager()

        # TODO: _PROCESS.io_counters() is not available on Mac OS and some Linux distros. Find alternative.
        self.assertEqual(len(manager._performance_counters), len(PERFORMANCE_COUNTER_METRICS) - 1)
        mock_meter_provider.get_meter.assert_called_once()

    def test_manager_initialization_with_custom_meter_provider(self):  # pylint: disable=name-too-long
        """Test manager initialization with custom meter provider."""
        mock_meter_provider = MagicMock()
        mock_meter = MagicMock()
        mock_meter_provider.get_meter.return_value = mock_meter

        # Mock create_observable_gauge and create_histogram to return mock objects
        mock_meter.create_observable_gauge.return_value = MagicMock()
        mock_meter.create_histogram.return_value = MagicMock()

        _manager = _PerformanceCountersManager(meter_provider=mock_meter_provider)

        mock_meter_provider.get_meter.assert_called_once()

    @mock.patch("azure.monitor.opentelemetry.exporter._performance_counters._manager.metrics.get_meter_provider")
    def test_manager_initialization_failure(self, mock_get_meter_provider):
        """Test manager initialization failure."""
        mock_get_meter_provider.side_effect = Exception("Meter provider error")

        manager = _PerformanceCountersManager()

        # Manager should handle the exception gracefully
        self.assertIsNotNone(manager)

    def test_manager_singleton_behavior(self):
        """Test that manager follows singleton pattern."""
        manager1 = _PerformanceCountersManager()
        manager2 = _PerformanceCountersManager()

        self.assertIs(manager1, manager2)

    @mock.patch("azure.monitor.opentelemetry.exporter._performance_counters._manager.metrics.get_meter_provider")
    def test_record_span_consumer(self, mock_get_meter_provider):
        """Test recording span for requests."""
        mock_meter_provider = MagicMock()
        mock_meter = MagicMock()
        mock_meter_provider.get_meter.return_value = mock_meter
        mock_get_meter_provider.return_value = mock_meter_provider

        manager = _PerformanceCountersManager()
        manager._request_duration_histogram = MagicMock()

        # Create a mock span
        mock_span = MagicMock(spec=ReadableSpan)
        mock_span.kind = SpanKind.CONSUMER
        mock_span.start_time = 1000000000  # 1 second in nanoseconds
        mock_span.end_time = 2000000000  # 2 seconds in nanoseconds
        mock_span.events = []

        # Import to access global counter
        import azure.monitor.opentelemetry.exporter._performance_counters._manager as manager_module

        initial_count = manager_module._REQUESTS_COUNT

        manager._record_span(mock_span)

        # Check that request was counted and duration recorded
        self.assertEqual(manager_module._REQUESTS_COUNT, initial_count + 1)
        manager._request_duration_histogram.record.assert_called_once_with(1.0)  # 1 second duration

    @mock.patch("azure.monitor.opentelemetry.exporter._performance_counters._manager.metrics.get_meter_provider")
    def test_record_span_request(self, mock_get_meter_provider):
        """Test recording span for requests."""
        mock_meter_provider = MagicMock()
        mock_meter = MagicMock()
        mock_meter_provider.get_meter.return_value = mock_meter
        mock_get_meter_provider.return_value = mock_meter_provider

        manager = _PerformanceCountersManager()
        manager._request_duration_histogram = MagicMock()

        # Create a mock span
        mock_span = MagicMock(spec=ReadableSpan)
        mock_span.kind = SpanKind.SERVER
        mock_span.start_time = 1000000000  # 1 second in nanoseconds
        mock_span.end_time = 2000000000  # 2 seconds in nanoseconds
        mock_span.events = []

        # Import to access global counter
        import azure.monitor.opentelemetry.exporter._performance_counters._manager as manager_module

        initial_count = manager_module._REQUESTS_COUNT

        manager._record_span(mock_span)

        # Check that request was counted and duration recorded
        self.assertEqual(manager_module._REQUESTS_COUNT, initial_count + 1)
        manager._request_duration_histogram.record.assert_called_once_with(1.0)  # 1 second duration

    @mock.patch("azure.monitor.opentelemetry.exporter._performance_counters._manager.metrics.get_meter_provider")
    def test_record_span_with_exception(self, mock_get_meter_provider):
        """Test recording span with exception event."""
        mock_meter_provider = MagicMock()
        mock_meter = MagicMock()
        mock_meter_provider.get_meter.return_value = mock_meter
        mock_get_meter_provider.return_value = mock_meter_provider

        manager = _PerformanceCountersManager()
        manager._request_duration_histogram = MagicMock()

        # Create a mock span with exception event
        mock_event = MagicMock()
        mock_event.name = "exception"

        mock_span = MagicMock(spec=ReadableSpan)
        mock_span.kind = SpanKind.SERVER
        mock_span.start_time = 1000000000
        mock_span.end_time = 2000000000
        mock_span.events = [mock_event]

        # Import to access global counter
        import azure.monitor.opentelemetry.exporter._performance_counters._manager as manager_module

        initial_exceptions = manager_module._EXCEPTIONS_COUNT

        manager._record_span(mock_span)

        # Check that exception was counted
        self.assertEqual(manager_module._EXCEPTIONS_COUNT, initial_exceptions + 1)

    def test_record_span_non_server_consumer_kind(self):  # pylint: disable=name-too-long
        """Test recording span that's not a server/consumer kind."""
        manager = _PerformanceCountersManager()

        # Create a mock span with CLIENT kind
        mock_span = MagicMock(spec=ReadableSpan)
        mock_span.kind = SpanKind.CLIENT

        # Import to access global counter
        import azure.monitor.opentelemetry.exporter._performance_counters._manager as manager_module

        initial_count = manager_module._REQUESTS_COUNT

        manager._record_span(mock_span)

        # Request count should not change
        self.assertEqual(manager_module._REQUESTS_COUNT, initial_count)

    @mock.patch("azure.monitor.opentelemetry.exporter._performance_counters._manager.metrics.get_meter_provider")
    def test_record_log_record_with_exception(self, mock_get_meter_provider):
        """Test recording log record with exception attributes."""
        mock_meter_provider = MagicMock()
        mock_meter = MagicMock()
        mock_meter_provider.get_meter.return_value = mock_meter
        mock_get_meter_provider.return_value = mock_meter_provider

        manager = _PerformanceCountersManager()

        # Create a mock log data with exception attributes
        mock_log_record = MagicMock()
        mock_log_record.attributes = {EXCEPTION_TYPE: "ValueError", EXCEPTION_MESSAGE: "Test exception"}

        mock_readable_log_record = MagicMock(spec=ReadableLogRecord)
        mock_readable_log_record.log_record = mock_log_record

        # Import to access global counter
        import azure.monitor.opentelemetry.exporter._performance_counters._manager as manager_module

        initial_exceptions = manager_module._EXCEPTIONS_COUNT

        manager._record_log_record(mock_readable_log_record)

        # Check that exception was counted
        self.assertEqual(manager_module._EXCEPTIONS_COUNT, initial_exceptions + 1)

    def test_record_log_record_without_exception(self):
        """Test recording log record without exception attributes."""
        manager = _PerformanceCountersManager()

        # Create a mock log data without exception attributes
        mock_log_record = MagicMock()
        mock_log_record.attributes = {"normal": "attribute"}

        mock_readable_log_record = MagicMock(spec=ReadableLogRecord)
        mock_readable_log_record.log_record = mock_log_record

        # Import to access global counter
        import azure.monitor.opentelemetry.exporter._performance_counters._manager as manager_module

        initial_exceptions = manager_module._EXCEPTIONS_COUNT

        manager._record_log_record(mock_readable_log_record)

        # Exception count should not change
        self.assertEqual(manager_module._EXCEPTIONS_COUNT, initial_exceptions)


class TestEnablePerformanceCounters(unittest.TestCase):
    """Test the enable_performance_counters function."""

    def setUp(self):
        """Reset singleton before each test."""
        if _PerformanceCountersManager in Singleton._instances:
            del Singleton._instances[_PerformanceCountersManager]

    def tearDown(self):
        """Clean up after each test."""
        if _PerformanceCountersManager in Singleton._instances:
            del Singleton._instances[_PerformanceCountersManager]

    def test_enable_performance_counters_default_provider(self):  # pylint: disable=name-too-long
        """Test enabling performance counters with default provider."""
        # Create a proper meter provider for testing
        meter_provider = MeterProvider()

        with mock.patch(
            "azure.monitor.opentelemetry.exporter._performance_counters._manager.metrics.get_meter_provider",
            return_value=meter_provider,
        ):
            enable_performance_counters()

        # Should create a manager instance
        # self.assertIsNotNone(_PerformanceCountersManager._instance)
        self.assertIn(_PerformanceCountersManager, Singleton._instances)

    def test_enable_performance_counters_custom_provider(self):  # pylint: disable=name-too-long
        """Test enabling performance counters with custom provider."""
        # Create a proper meter provider for testing
        meter_provider = MeterProvider()

        enable_performance_counters(meter_provider=meter_provider)

        # Should create a manager instance
        # self.assertIsNotNone(_PerformanceCountersManager._instance)
        self.assertIn(_PerformanceCountersManager, Singleton._instances)


class TestPerformanceCounterMetricsConstants(unittest.TestCase):
    """Test performance counter metrics constants and mappings."""

    def test_performance_counter_metrics_list(self):
        """Test that PERFORMANCE_COUNTER_METRICS contains all expected classes."""
        expected_classes = [
            AvailableMemory,
            ExceptionRate,
            RequestExecutionTime,
            RequestRate,
            ProcessCpu,
            ProcessCpuNormalized,
            ProcessIORate,
            ProcessPrivateBytes,
            ProcessorTime,
        ]

        self.assertEqual(len(PERFORMANCE_COUNTER_METRICS), len(expected_classes))

        for expected_class in expected_classes:
            self.assertIn(expected_class, PERFORMANCE_COUNTER_METRICS)

    def test_metric_name_constants(self):
        """Test that all metric classes have proper NAME constants."""
        for metric_class in PERFORMANCE_COUNTER_METRICS:
            self.assertTrue(hasattr(metric_class, "NAME"))
            self.assertIsInstance(metric_class.NAME, tuple)
            self.assertEqual(len(metric_class.NAME), 2)
            # First element should be the OpenTelemetry metric name
            self.assertIsInstance(metric_class.NAME[0], str)
            self.assertTrue(metric_class.NAME[0].startswith("azuremonitor.performancecounter."))
            # Second element should be the Quickpulse metric name
            self.assertIsInstance(metric_class.NAME[1], str)


class TestPerformanceCountersMetricsIntegration(unittest.TestCase):  # pylint: disable=name-too-long
    """Test actual metrics generation from performance counters."""

    def setUp(self):
        """Set up test environment."""
        # Reset singleton
        if _PerformanceCountersManager in Singleton._instances:
            del Singleton._instances[_PerformanceCountersManager]

        # Create a metrics setup that allows us to read metrics
        self.reader = InMemoryMetricReader()
        self.meter_provider = MeterProvider(metric_readers=[self.reader])

    def tearDown(self):
        """Clean up after tests."""
        if _PerformanceCountersManager in Singleton._instances:
            del Singleton._instances[_PerformanceCountersManager]

    def _get_metric_names(self, metrics_data):  # pylint: disable=docstring-missing-return, docstring-missing-rtype
        """Helper to extract metric names from metrics data."""
        metric_names = []
        for resource_metrics in metrics_data.resource_metrics:
            for scope_metrics in resource_metrics.scope_metrics:
                for metric in scope_metrics.metrics:
                    metric_names.append(metric.name)
        return metric_names

    def _get_metric_value(
        self, metrics_data, metric_name
    ):  # pylint: disable=docstring-missing-return, docstring-missing-rtype
        """Helper to extract metric value from metrics data."""
        for resource_metrics in metrics_data.resource_metrics:
            for scope_metrics in resource_metrics.scope_metrics:
                for metric in scope_metrics.metrics:
                    if metric.name == metric_name:
                        if hasattr(metric.data, "data_points") and metric.data.data_points:
                            return metric.data.data_points[0].value
        return None

    @mock.patch("psutil.virtual_memory")
    def test_available_memory_metric_generation(self, mock_virtual_memory):
        """Test that available memory metrics are generated correctly."""
        # Mock available memory
        mock_virtual_memory.return_value.available = 2147483648  # 2GB

        # Initialize performance counters - use real meter provider, not mocked
        _manager = _PerformanceCountersManager(meter_provider=self.meter_provider)

        # Force metrics collection
        metrics_data = self.reader.get_metrics_data()

        # Verify that available memory metric was created
        metric_names = self._get_metric_names(metrics_data)
        self.assertIn("azuremonitor.performancecounter.memoryavailablebytes", metric_names)

        # Verify the metric value
        memory_value = self._get_metric_value(metrics_data, "azuremonitor.performancecounter.memoryavailablebytes")
        self.assertEqual(memory_value, 2147483648)  # Should match our mocked value

    @mock.patch("azure.monitor.opentelemetry.exporter._performance_counters._manager._PROCESS")
    def test_process_memory_metric_generation(self, mock_process):
        """Test that process memory metrics are generated correctly."""
        # Mock process memory
        mock_memory_info = MagicMock()
        mock_memory_info.rss = 104857600  # 100MB
        mock_process.memory_info.return_value = mock_memory_info

        # Initialize performance counters - use real meter provider, not mocked
        _manager = _PerformanceCountersManager(meter_provider=self.meter_provider)

        # Force metrics collection
        metrics_data = self.reader.get_metrics_data()

        # Verify that process memory metric was created
        metric_names = self._get_metric_names(metrics_data)
        self.assertIn("azuremonitor.performancecounter.processprivatebytes", metric_names)

        # Verify the metric value
        memory_value = self._get_metric_value(metrics_data, "azuremonitor.performancecounter.processprivatebytes")
        self.assertEqual(memory_value, 104857600)  # Should match our mocked value
