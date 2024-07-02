# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# cSpell:disable
from datetime import datetime
from typing import Any, Iterable, Optional

import platform
import psutil

from opentelemetry.metrics import CallbackOptions, Observation
from opentelemetry.sdk._logs import LogData
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.id_generator import RandomIdGenerator
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import SpanKind

from azure.monitor.opentelemetry.exporter._generated.models import ContextTagKeys
from azure.monitor.opentelemetry.exporter._quickpulse._constants import (
    _COMMITTED_BYTES_NAME,
    _DEPENDENCY_DURATION_NAME,
    _DEPENDENCY_FAILURE_RATE_NAME,
    _DEPENDENCY_RATE_NAME,
    _EXCEPTION_RATE_NAME,
    _PROCESS_PHYSICAL_BYTES_NAME,
    _PROCESS_TIME_NORMALIZED_NAME,
    _PROCESSOR_TIME_NAME,
    _REQUEST_DURATION_NAME,
    _REQUEST_FAILURE_RATE_NAME,
    _REQUEST_RATE_NAME,
)
from azure.monitor.opentelemetry.exporter._quickpulse._exporter import (
    _QuickpulseExporter,
    _QuickpulseMetricReader,
)
from azure.monitor.opentelemetry.exporter._quickpulse._generated.models import MonitoringDataPoint
from azure.monitor.opentelemetry.exporter._quickpulse._state import (
    _QuickpulseState,
    _is_post_state,
    _append_quickpulse_document,
    _get_quickpulse_last_process_cpu,
    _get_quickpulse_last_process_time,
    _get_quickpulse_process_elapsed_time,
    _set_global_quickpulse_state,
    _set_quickpulse_last_process_cpu,
    _set_quickpulse_last_process_time,
    _set_quickpulse_process_elapsed_time,
)
from azure.monitor.opentelemetry.exporter._quickpulse._utils import (
    _get_log_record_document,
    _get_span_document,
)
from azure.monitor.opentelemetry.exporter.statsbeat._state import (
    set_statsbeat_live_metrics_feature_set,
)
from azure.monitor.opentelemetry.exporter._utils import (
    _get_sdk_version,
    _is_on_app_service,
    _populate_part_a_fields,
    Singleton,
)


PROCESS = psutil.Process()
NUM_CPUS = psutil.cpu_count()

def enable_live_metrics(**kwargs: Any) -> None:  # pylint: disable=C4758
    """Live metrics entry point.

    :keyword str connection_string: The connection string used for your Application Insights resource.
    :keyword Resource resource: The OpenTelemetry Resource used for this Python application.
    :rtype: None
    """
    _QuickpulseManager(kwargs.get('connection_string'), kwargs.get('resource'))
    set_statsbeat_live_metrics_feature_set()


# pylint: disable=protected-access,too-many-instance-attributes
class _QuickpulseManager(metaclass=Singleton):

    def __init__(self, connection_string: Optional[str], resource: Optional[Resource]) -> None:
        _set_global_quickpulse_state(_QuickpulseState.PING_SHORT)
        self._exporter = _QuickpulseExporter(connection_string)
        part_a_fields = {}
        if resource:
            part_a_fields = _populate_part_a_fields(resource)
        id_generator = RandomIdGenerator()
        self._base_monitoring_data_point = MonitoringDataPoint(
            version=_get_sdk_version(),
            invariant_version=1,
            instance=part_a_fields.get(ContextTagKeys.AI_CLOUD_ROLE_INSTANCE, ""),
            role_name=part_a_fields.get(ContextTagKeys.AI_CLOUD_ROLE, ""),
            machine_name=platform.node(),
            stream_id=str(id_generator.generate_trace_id()),
            is_web_app=_is_on_app_service(),
            performance_collection_supported=True,
        )
        self._reader = _QuickpulseMetricReader(self._exporter, self._base_monitoring_data_point)
        self._meter_provider = MeterProvider([self._reader])
        self._meter = self._meter_provider.get_meter("azure_monitor_live_metrics")

        self._request_duration = self._meter.create_histogram(
            _REQUEST_DURATION_NAME[0],
            "ms",
            "live metrics avg request duration in ms"
        )
        self._dependency_duration = self._meter.create_histogram(
            _DEPENDENCY_DURATION_NAME[0],
            "ms",
            "live metrics avg dependency duration in ms"
        )
        # We use a counter to represent rates per second because collection
        # interval is one second so we simply need the number of requests
        # within the collection interval
        self._request_rate_counter = self._meter.create_counter(
            _REQUEST_RATE_NAME[0],
            "req/sec",
            "live metrics request rate per second"
        )
        self._request_failed_rate_counter = self._meter.create_counter(
            _REQUEST_FAILURE_RATE_NAME[0],
            "req/sec",
            "live metrics request failed rate per second"
        )
        self._dependency_rate_counter = self._meter.create_counter(
            _DEPENDENCY_RATE_NAME[0],
            "dep/sec",
            "live metrics dependency rate per second"
        )
        self._dependency_failure_rate_counter = self._meter.create_counter(
            _DEPENDENCY_FAILURE_RATE_NAME[0],
            "dep/sec",
            "live metrics dependency failure rate per second"
        )
        self._exception_rate_counter = self._meter.create_counter(
            _EXCEPTION_RATE_NAME[0],
            "exc/sec",
            "live metrics exception rate per second"
        )
        self._process_memory_gauge_old = self._meter.create_observable_gauge(
            _COMMITTED_BYTES_NAME[0],
            [_get_process_memory],
        )
        self._process_memory_gauge = self._meter.create_observable_gauge(
            _PROCESS_PHYSICAL_BYTES_NAME[0],
            [_get_process_memory],
        )
        self._process_time_gauge_old = self._meter.create_observable_gauge(
            _PROCESSOR_TIME_NAME[0],
            [_get_process_time_normalized_old],
        )
        self._process_time_gauge = self._meter.create_observable_gauge(
            _PROCESS_TIME_NORMALIZED_NAME[0],
            [_get_process_time_normalized],
        )

    def _record_span(self, span: ReadableSpan) -> None:
        # Only record if in post state
        if _is_post_state():
            document = _get_span_document(span)
            _append_quickpulse_document(document)
            duration_ms = 0
            if span.end_time and span.start_time:
                duration_ms = (span.end_time - span.start_time) / 1e9  # type: ignore
            # TODO: Spec out what "success" is
            success = span.status.is_ok

            if span.kind in (SpanKind.SERVER, SpanKind.CONSUMER):
                if success:
                    self._request_rate_counter.add(1)
                else:
                    self._request_failed_rate_counter.add(1)
                self._request_duration.record(duration_ms)
            else:
                if success:
                    self._dependency_rate_counter.add(1)
                else:
                    self._dependency_failure_rate_counter.add(1)
                self._dependency_duration.record(duration_ms)

    def _record_log_record(self, log_data: LogData) -> None:
        # Only record if in post state
        if _is_post_state():
            if log_data.log_record:
                log_record = log_data.log_record
                if log_record.attributes:
                    document = _get_log_record_document(log_data)
                    _append_quickpulse_document(document)
                    exc_type = log_record.attributes.get(SpanAttributes.EXCEPTION_TYPE)
                    exc_message = log_record.attributes.get(SpanAttributes.EXCEPTION_MESSAGE)
                    if exc_type is not None or exc_message is not None:
                        self._exception_rate_counter.add(1)


# pylint: disable=unused-argument
def _get_process_memory(options: CallbackOptions) -> Iterable[Observation]:
    memory = 0
    try:
        # rss is non-swapped physical memory a process has used
        memory = PROCESS.memory_info().rss
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
    yield Observation(memory, {})


# pylint: disable=unused-argument
def _get_process_time_normalized_old(options: CallbackOptions) -> Iterable[Observation]:
    normalized_cpu_percentage = 0.0
    try:
        cpu_times = PROCESS.cpu_times()
        # total process time is user + system in s
        total_time_s = cpu_times.user + cpu_times.system
        process_time_s = total_time_s - _get_quickpulse_last_process_time()
        _set_quickpulse_last_process_time(process_time_s)
        # Find elapsed time in s since last collection
        current_time = datetime.now()
        elapsed_time_s = (current_time - _get_quickpulse_process_elapsed_time()).total_seconds()
        _set_quickpulse_process_elapsed_time(current_time)
        # Obtain cpu % by dividing by elapsed time
        cpu_percentage = process_time_s / elapsed_time_s
        # Normalize by dividing by amount of logical cpus
        normalized_cpu_percentage = cpu_percentage / NUM_CPUS
        _set_quickpulse_last_process_cpu(normalized_cpu_percentage)
    except (psutil.NoSuchProcess, psutil.AccessDenied, ZeroDivisionError):
        pass
    yield Observation(normalized_cpu_percentage, {})


# pylint: disable=unused-argument
def _get_process_time_normalized(options: CallbackOptions) -> Iterable[Observation]:
    yield Observation(_get_quickpulse_last_process_cpu(), {})

# cSpell:enable
