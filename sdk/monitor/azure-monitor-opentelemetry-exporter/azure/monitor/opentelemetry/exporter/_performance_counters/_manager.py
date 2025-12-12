# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from datetime import datetime
from typing import Iterable
import logging

import psutil

from opentelemetry import metrics
from opentelemetry.metrics import CallbackOptions, Observation
from opentelemetry.sdk._logs import ReadableLogRecord
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.semconv.attributes.exception_attributes import (
    EXCEPTION_MESSAGE,
    EXCEPTION_TYPE,
)
from opentelemetry.trace import SpanKind

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
)
from azure.monitor.opentelemetry.exporter._utils import (
    Singleton,
)

_logger = logging.getLogger(__name__)

# Global process instance for efficiency.
# A separate object is used for the normalized performance counter so the interval
# is not reset when one performance counter triggers immediately before another.
# Process CPU %
_PROCESS = psutil.Process()
# Process CPU % Normalized
# Since the normalized and non-normalized functions use the same method, they need
# separate objects so as to not reset the interval
_PROCESS_FOR_CPU_NORMALIZED = psutil.Process()
NUM_CPUS = psutil.cpu_count()
# Process I/O Rates
# _PROCESS.io_counters() is not available on Mac OS and some Linux distros.
_IO_AVAILABLE = hasattr(_PROCESS, "io_counters")
_IO_LAST_COUNT = 0
if _IO_AVAILABLE:
    _io_counters_initial = _PROCESS.io_counters()
    _IO_LAST_COUNT = _io_counters_initial.read_bytes + _io_counters_initial.write_bytes
_IO_LAST_TIME = datetime.now()
# Processor Time %
_LAST_CPU_TIMES = psutil.cpu_times()
# Request Rate
_LAST_REQUEST_RATE_TIME = datetime.now()
_REQUESTS_COUNT = 0
# Exception Rate
_LAST_EXCEPTION_RATE_TIME = datetime.now()
_EXCEPTIONS_COUNT = 0


#  pylint: disable=unused-argument
def _get_process_cpu(options: CallbackOptions) -> Iterable[Observation]:
    """Get process CPU usage as a percentage.

    In the case of a process running on multiple threads on different CPU cores,
    the returned value can be > 100.0.
    
    :param options: Callback options for OpenTelemetry observable gauge.
    :type options: ~opentelemetry.metrics.CallbackOptions
    :returns: Process CPU usage percentage observations.
    :rtype: ~typing.Iterable[~opentelemetry.metrics.Observation]
    """
    try:
        # Get CPU percent for the current process
        cpu_percent = _PROCESS.cpu_percent(interval=None)
        yield Observation(cpu_percent, {})
    except (psutil.NoSuchProcess, psutil.AccessDenied, Exception) as e:  # pylint: disable=broad-except
        _logger.exception("Error getting process CPU usage: %s", e)  # pylint: disable=logging-not-lazy
        yield Observation(0.0, {})


#  pylint: disable=unused-argument
def _get_process_cpu_normalized(options: CallbackOptions) -> Iterable[Observation]:
    """Get process CPU usage as a percentage.

    In the case of a process running on multiple threads on different CPU cores,
    the returned value can be > 100.0. We normalize the CPU process usage
    using the number of logical CPUs.
    
    :param options: Callback options for OpenTelemetry observable gauge.
    :type options: ~opentelemetry.metrics.CallbackOptions
    :returns: Normalized process CPU usage percentage observations.
    :rtype: ~typing.Iterable[~opentelemetry.metrics.Observation]
    """
    try:
        # Get number of logical CPUs
        if NUM_CPUS is None or NUM_CPUS == 0:
            yield Observation(0.0, {})
            return

        # Get CPU percent for the current process
        cpu_percent = _PROCESS_FOR_CPU_NORMALIZED.cpu_percent(interval=None)

        # Normalize by CPU count
        normalized_cpu_percent = cpu_percent / NUM_CPUS

        yield Observation(normalized_cpu_percent, {})
    except (psutil.NoSuchProcess, psutil.AccessDenied, Exception) as e:  # pylint: disable=broad-except
        _logger.exception("Error getting normalized process CPU usage: %s", e)  # pylint: disable=logging-not-lazy
        yield Observation(0.0, {})


#  pylint: disable=unused-argument
def _get_available_memory(options: CallbackOptions) -> Iterable[Observation]:
    """Get available memory in bytes.

    Available memory is defined as memory that can be given instantly to
    processes without the system going into swap.
    
    :param options: Callback options for OpenTelemetry observable gauge.
    :type options: ~opentelemetry.metrics.CallbackOptions
    :returns: Available memory in bytes observations.
    :rtype: ~typing.Iterable[~opentelemetry.metrics.Observation]
    """
    try:
        # Available memory in bytes
        available_memory = psutil.virtual_memory().available
        yield Observation(available_memory, {})
    except Exception as e:  # pylint: disable=broad-except
        _logger.exception("Error getting available memory: %s", e)  # pylint: disable=logging-not-lazy
        yield Observation(0, {})


#  pylint: disable=unused-argument
def _get_process_memory(options: CallbackOptions) -> Iterable[Observation]:
    """Get process private bytes (RSS).

    Private bytes for the current process is measured by the Resident Set Size,
    which is the non-swapped physical memory a process has used.
    
    :param options: Callback options for OpenTelemetry observable gauge.
    :type options: ~opentelemetry.metrics.CallbackOptions
    :returns: Process memory usage in bytes observations.
    :rtype: ~typing.Iterable[~opentelemetry.metrics.Observation]
    """
    try:
        # RSS is non-swapped physical memory a process has used
        private_bytes = _PROCESS.memory_info().rss
        yield Observation(private_bytes, {})
    except (psutil.NoSuchProcess, psutil.AccessDenied, Exception) as e:  # pylint: disable=broad-except
        _logger.exception("Error getting process memory: %s", e)  # pylint: disable=logging-not-lazy
        yield Observation(0, {})


#  pylint: disable=unused-argument
def _get_process_io(options: CallbackOptions) -> Iterable[Observation]:
    """Get process I/O rate in bytes per second.

    Includes both read and write operations for both network and disk I/O.

    :param options: Callback options for OpenTelemetry observable gauge.
    :type options: ~opentelemetry.metrics.CallbackOptions
    :returns: Process I/O rate in bytes per second observations.
    :rtype: ~typing.Iterable[~opentelemetry.metrics.Observation]
    """
    try:
        if not _IO_AVAILABLE:
            yield Observation(0, {})
            return
        # pylint: disable=global-statement
        global _IO_LAST_COUNT
        # pylint: disable=global-statement
        global _IO_LAST_TIME
        # RSS is non-swapped physical memory a process has used
        io_counters = _PROCESS.io_counters()
        rw_count = io_counters.read_bytes + io_counters.write_bytes
        rw_diff = rw_count - _IO_LAST_COUNT
        _IO_LAST_COUNT = rw_count
        current_time = datetime.now()
        elapsed_time_s = (current_time - _IO_LAST_TIME).total_seconds()
        _IO_LAST_TIME = current_time
        io_rate = rw_diff / elapsed_time_s
        yield Observation(io_rate, {})
    except (psutil.NoSuchProcess, psutil.AccessDenied, Exception) as e:  # pylint: disable=broad-except
        _logger.exception("Error getting process I/O rate: %s", e)
        yield Observation(0, {})

def _get_cpu_times_total(cpu_times):
    """Calculate total CPU time from CPU times structure.
    
    :param cpu_times: CPU times structure from psutil.
    :type cpu_times: psutil._common.scputimes
    :returns: Total CPU time.
    :rtype: float
    """
    total = cpu_times.user + cpu_times.system + cpu_times.idle
    # Platform-specific values
    if hasattr(cpu_times, "nice"):
        total += cpu_times.nice
    if hasattr(cpu_times, "iowait"):
        total += cpu_times.iowait
    if hasattr(cpu_times, "irq"):
        total += cpu_times.irq
    if hasattr(cpu_times, "softirq"):
        total += cpu_times.softirq
    if hasattr(cpu_times, "steal"):
        total += cpu_times.steal
    if hasattr(cpu_times, "guest"):
        total += cpu_times.guest
    if hasattr(cpu_times, "guest_nice"):
        total += cpu_times.guest_nice
    if hasattr(cpu_times, "interrupt"):
        total += cpu_times.interrupt
    if hasattr(cpu_times, "dpc"):
        total += cpu_times.dpc
    return total


#  pylint: disable=unused-argument
def _get_processor_time(options: CallbackOptions) -> Iterable[Observation]:
    """Get system-wide CPU utilization as a percentage.

    Processor time is defined as the current system-wide CPU utilization
    minus idle CPU time as a percentage. Return values range from 0.0 to 100.0.
    
    :param options: Callback options for OpenTelemetry observable gauge.
    :type options: ~opentelemetry.metrics.CallbackOptions
    :returns: System-wide CPU utilization percentage observations.
    :rtype: ~typing.Iterable[~opentelemetry.metrics.Observation]
    """
    try:
        # pylint: disable=global-statement
        global _LAST_CPU_TIMES
        cpu_times = psutil.cpu_times()
        total = _get_cpu_times_total(cpu_times)
        last_total = _get_cpu_times_total(_LAST_CPU_TIMES)
        idle_d = cpu_times.idle - _LAST_CPU_TIMES.idle
        total_d = total - last_total
        utilization_percentage = 100*(total_d - idle_d)/total_d
        _LAST_CPU_TIMES = cpu_times
        yield Observation(utilization_percentage, {})
    except Exception as e:  # pylint: disable=broad-except
        _logger.exception("Error getting processor time: %s", e)
        yield Observation(0.0, {})


#  pylint: disable=unused-argument
def _get_request_rate(options: CallbackOptions) -> Iterable[Observation]:
    """Get request rate in requests per second.
    
    :param options: Callback options for OpenTelemetry observable gauge.
    :type options: ~opentelemetry.metrics.CallbackOptions
    :returns: Request rate in requests per second observations.
    :rtype: ~typing.Iterable[~opentelemetry.metrics.Observation]
    """
    try:
        # pylint: disable=global-statement
        global _LAST_REQUEST_RATE_TIME
        # pylint: disable=global-statement
        global _REQUESTS_COUNT
        current_time = datetime.now()
        elapsed_time_s = (current_time - _LAST_REQUEST_RATE_TIME).total_seconds()
        request_rate = _REQUESTS_COUNT / elapsed_time_s
        _LAST_REQUEST_RATE_TIME = current_time
        _REQUESTS_COUNT = 0
        yield Observation(request_rate, {})
    except Exception as e:  # pylint: disable=broad-except
        _logger.exception("Error getting request rate: %s", e)
        yield Observation(0.0, {})


#  pylint: disable=unused-argument
def _get_exception_rate(options: CallbackOptions) -> Iterable[Observation]:
    """Get exception rate in exceptions per second.
    
    :param options: Callback options for OpenTelemetry observable gauge.
    :type options: ~opentelemetry.metrics.CallbackOptions
    :returns: Exception rate in exceptions per second observations.
    :rtype: ~typing.Iterable[~opentelemetry.metrics.Observation]
    """
    try:
        # pylint: disable=global-statement
        global _LAST_EXCEPTION_RATE_TIME
        # pylint: disable=global-statement
        global _EXCEPTIONS_COUNT
        current_time = datetime.now()
        elapsed_time_s = (current_time - _LAST_EXCEPTION_RATE_TIME).total_seconds()
        exception_rate = _EXCEPTIONS_COUNT / elapsed_time_s
        _LAST_EXCEPTION_RATE_TIME = current_time
        _EXCEPTIONS_COUNT = 0
        yield Observation(exception_rate, {})
    except Exception as e:  # pylint: disable=broad-except
        _logger.exception("Error getting exception rate: %s", e)
        yield Observation(0.0, {})


class AvailableMemory:
    """Performance counter for available memory in bytes."""

    NAME = _AVAILABLE_MEMORY

    def __init__(self, meter):
        """Initialize the available memory metric.

        :param meter: OpenTelemetry meter instance.
        :type meter: ~opentelemetry.metrics.Meter
        """
        self._gauge = meter.create_observable_gauge(
            name=self.NAME[0],
            description="performance counter available memory in bytes",
            unit="byte",
            callbacks=[_get_available_memory]
        )

    @property
    def gauge(self):
        """Get the underlying gauge.
        
        :returns: The OpenTelemetry observable gauge instance.
        :rtype: ~opentelemetry.metrics.ObservableGauge
        """
        return self._gauge


class ExceptionRate:
    """Performance counter for exception rate in exceptions per second."""

    NAME = _EXCEPTION_RATE

    def __init__(self, meter):
        """Initialize the exception rate metric.

        :param meter: OpenTelemetry meter instance.
        :type meter: ~opentelemetry.metrics.Meter
        """
        self._gauge = meter.create_observable_gauge(
            name=self.NAME[0],
            description="performance counter exceptions per second",
            unit="exc/sec",
            callbacks=[_get_exception_rate]
        )

    @property
    def gauge(self):
        """Get the underlying gauge.
        
        :returns: The OpenTelemetry observable gauge instance.
        :rtype: ~opentelemetry.metrics.ObservableGauge
        """
        return self._gauge


class RequestExecutionTime:
    """Performance counter for average request execution time in milliseconds."""

    NAME = _REQUEST_EXECUTION_TIME

    def __init__(self, meter):
        """Initialize the request execution time metric.

        :param meter: OpenTelemetry meter instance.
        :type meter: ~opentelemetry.metrics.Meter
        """
        self._gauge = meter.create_histogram(
            name=self.NAME[0],
            description="performance counter avg request execution time in ms",
            unit="ms",
        )

    @property
    def gauge(self):
        """Get the underlying gauge.
        
        :returns: The OpenTelemetry histogram instance.
        :rtype: ~opentelemetry.metrics.Histogram
        """
        return self._gauge


class RequestRate:
    """Performance counter for request rate in requests per second."""

    NAME = _REQUEST_RATE

    def __init__(self, meter):
        """Initialize the request rate metric.

        :param meter: OpenTelemetry meter instance.
        :type meter: ~opentelemetry.metrics.Meter
        """
        self._gauge = meter.create_observable_gauge(
            name=self.NAME[0],
            description="performance counter requests per second",
            unit="req/sec",
            callbacks=[_get_request_rate]
        )

    @property
    def gauge(self):
        """Get the underlying gauge.
        
        :returns: The OpenTelemetry observable gauge instance.
        :rtype: ~opentelemetry.metrics.ObservableGauge
        """
        return self._gauge


class ProcessCpu:
    """Performance counter for process CPU usage percentage."""

    NAME = _PROCESS_CPU

    def __init__(self, meter):
        """Initialize the process CPU metric.

        :param meter: OpenTelemetry meter instance.
        :type meter: ~opentelemetry.metrics.Meter
        """
        # Initialize process CPU percent to get meaningful subsequent readings
        _PROCESS.cpu_percent(interval=None)

        self._gauge = meter.create_observable_gauge(
            name=self.NAME[0],
            description="performance counter process cpu usage as a percentage",
            unit="percent",
            callbacks=[_get_process_cpu]
        )

    @property
    def gauge(self):
        """Get the underlying gauge.
        
        :returns: The OpenTelemetry observable gauge instance.
        :rtype: ~opentelemetry.metrics.ObservableGauge
        """
        return self._gauge


class ProcessCpuNormalized:
    """Performance counter for normalized process CPU usage percentage."""

    NAME = _PROCESS_CPU_NORMALIZED

    def __init__(self, meter):
        """Initialize the process CPU normalized metric.

        :param meter: OpenTelemetry meter instance.
        :type meter: ~opentelemetry.metrics.Meter
        """
        # Initialize process CPU percent to get meaningful subsequent readings
        _PROCESS_FOR_CPU_NORMALIZED.cpu_percent(interval=None)

        self._gauge = meter.create_observable_gauge(
            name=self.NAME[0],
            description="performance counter process cpu usage as a percentage "
                       "divided by the number of total processors.",
            unit="percent",
            callbacks=[_get_process_cpu_normalized]
        )

    @property
    def gauge(self):
        """Get the underlying gauge.
        
        :returns: The OpenTelemetry observable gauge instance.
        :rtype: ~opentelemetry.metrics.ObservableGauge
        """
        return self._gauge


class ProcessIORate:
    """Performance counter for process I/O rate."""

    NAME = _PROCESS_IO_RATE

    def __init__(self, meter):
        """Initialize the process I/O metric.

        :param meter: OpenTelemetry meter instance.
        :type meter: ~opentelemetry.metrics.Meter
        """
        self._gauge = meter.create_observable_gauge(
            name=self.NAME[0],
            description="performance counter rate of I/O operations per second",
            unit="byte/sec",
            callbacks=[_get_process_io]
        )

    @property
    def gauge(self):
        """Get the underlying gauge.
        
        :returns: The OpenTelemetry observable gauge instance.
        :rtype: ~opentelemetry.metrics.ObservableGauge
        """
        return self._gauge


class ProcessPrivateBytes:
    """Performance counter for process private bytes."""

    NAME = _PROCESS_PRIVATE_BYTES

    def __init__(self, meter):
        """Initialize the process memory metric.

        :param meter: OpenTelemetry meter instance.
        :type meter: ~opentelemetry.metrics.Meter
        """
        self._gauge = meter.create_observable_gauge(
            name=self.NAME[0],
            description="performance counter amount of memory process has used in bytes",
            unit="byte",
            callbacks=[_get_process_memory]
        )

    @property
    def gauge(self):
        """Get the underlying gauge.
        
        :returns: The OpenTelemetry observable gauge instance.
        :rtype: ~opentelemetry.metrics.ObservableGauge
        """
        return self._gauge


class ProcessorTime:
    """Performance counter for system-wide processor time percentage."""

    NAME = _PROCESSOR_TIME

    def __init__(self, meter):
        """Initialize the processor time metric.

        :param meter: OpenTelemetry meter instance.
        :type meter: ~opentelemetry.metrics.Meter
        """
        self._gauge = meter.create_observable_gauge(
            name=self.NAME[0],
            description="performance counter processor time as a percentage",
            unit="percent",
            callbacks=[_get_processor_time]
        )

    @property
    def gauge(self):
        """Get the underlying gauge.
        
        :returns: The OpenTelemetry observable gauge instance.
        :rtype: ~opentelemetry.metrics.ObservableGauge
        """
        return self._gauge


# List of all performance counter metrics
# Note: ProcessIORate may not be available on all platforms. It is filtered out in
# _PerformanceCountersManager
PERFORMANCE_COUNTER_METRICS = [
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


class _PerformanceCountersManager(metaclass=Singleton):
    """Manager for Application Insights performance counters."""

    def __init__(self, meter_provider=None):
        """Initialize the performance counters manager.
        
        :param meter_provider: OpenTelemetry meter provider, if None uses global provider.
        :type meter_provider: ~opentelemetry.metrics.MeterProvider or None
        """
        self._meter = None
        self._performance_counters = []
        self._requests_count = 0
        self._exceptions_count = 0
        try:
            if meter_provider is None:
                meter_provider = metrics.get_meter_provider()

            self._meter = meter_provider.get_meter(
                "azure.monitor.opentelemetry.performance_counters"
            )

            # Initialize all performance counter metrics
            for metric_class in PERFORMANCE_COUNTER_METRICS:
                try:
                    # Note: ProcessIORate may not be available on all platforms
                    if metric_class == ProcessIORate and not _IO_AVAILABLE:
                        _logger.warning("Process I/O Rate performance counter is not available on this platform.")
                        continue
                    performance_counter = metric_class(self._meter)
                    self._performance_counters.append(performance_counter)
                    if metric_class == RequestExecutionTime:
                        self._request_duration_histogram = performance_counter.gauge
                except Exception as e:  # pylint: disable=broad-except
                    _logger.warning("Failed to initialize performance counter %s: %s", metric_class.NAME[0], e)

        except Exception as e:  # pylint: disable=broad-except
            _logger.warning("Failed to setup performance counters: %s", e)

    def _record_span(self, span: ReadableSpan) -> None:
        try:
            # pylint: disable=global-statement
            global _REQUESTS_COUNT
            # pylint: disable=global-statement
            global _EXCEPTIONS_COUNT
            # Requests and Consumer only
            if span.kind not in (SpanKind.SERVER, SpanKind.CONSUMER):
                return
            _REQUESTS_COUNT += 1
            duration_ms = 0
            # Times are in ns
            if span.end_time and span.start_time:
                duration_ms = (span.end_time - span.start_time) / 1e9  # type: ignore
            self._request_duration_histogram.record(duration_ms)
            if span.events:
                for event in span.events:
                    if event.name == "exception":
                        _EXCEPTIONS_COUNT += 1
        except Exception:  # pylint: disable=broad-except
            _logger.exception("Exception occurred while recording span.")  # pylint: disable=C4769

    def _record_log_record(self, readable_log_record: ReadableLogRecord) -> None:
        try:
            # pylint: disable=global-statement
            global _EXCEPTIONS_COUNT
            if readable_log_record.log_record:
                exc_type = None
                log_record = readable_log_record.log_record
                if log_record.attributes:
                    exc_type = log_record.attributes.get(EXCEPTION_TYPE)
                    exc_message = log_record.attributes.get(EXCEPTION_MESSAGE)
                    if exc_type is not None or exc_message is not None:
                        _EXCEPTIONS_COUNT += 1  # type: ignore
        except Exception:  # pylint: disable=broad-except
            _logger.exception("Exception occurred while recording log record.")  # pylint: disable=C4769


def enable_performance_counters(meter_provider=None):
    """Set up performance counters globally.

    :param meter_provider: OpenTelemetry meter provider, if None uses global provider.
    :type meter_provider: ~opentelemetry.metrics.MeterProvider or None
    """
    _PerformanceCountersManager(meter_provider)
    # TODO: Add perf counters to statsbeat
    # set_statsbeat_performance_counters_feature_set()
