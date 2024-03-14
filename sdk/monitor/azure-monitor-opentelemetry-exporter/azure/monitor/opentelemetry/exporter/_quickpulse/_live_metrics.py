# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# cSpell:disable

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
    _set_global_quickpulse_state,
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
    _populate_part_a_fields,
    Singleton,
)


PROCESS = psutil.Process()

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
        self._process_memory_gauge = self._meter.create_observable_gauge(
            _COMMITTED_BYTES_NAME[0],
            [_get_process_memory],
        )
        self._processor_time_gauge = self._meter.create_observable_gauge(
            _PROCESSOR_TIME_NAME[0],
            [_get_processor_time],
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
    # rss is non-swapped physical memory a process has used
    yield Observation(
        PROCESS.memory_info().rss,
        {},
    )


# pylint: disable=unused-argument
def _get_processor_time(options: CallbackOptions) -> Iterable[Observation]:
    # Processor time does not include idle time
    yield Observation(
        100 - psutil.cpu_times_percent().idle,
        {},
    )

# cSpell:enable
