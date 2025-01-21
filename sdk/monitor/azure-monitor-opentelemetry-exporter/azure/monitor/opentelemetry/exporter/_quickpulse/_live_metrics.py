# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# cSpell:disable
from typing import Any, Dict, List, Optional

import logging
import platform
import psutil

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
from azure.monitor.opentelemetry.exporter._quickpulse._cpu import (
    _get_process_memory,
    _get_process_time_normalized,
    _get_process_time_normalized_old,
)
from azure.monitor.opentelemetry.exporter._quickpulse._exporter import (
    _QuickpulseExporter,
    _QuickpulseMetricReader,
)
from azure.monitor.opentelemetry.exporter._quickpulse._filter import (
    _check_filters,
    _check_metric_filters,
)
from azure.monitor.opentelemetry.exporter._quickpulse._generated.models import (
    DerivedMetricInfo,
    FilterConjunctionGroupInfo,
    MonitoringDataPoint,
    TelemetryType,
)
from azure.monitor.opentelemetry.exporter._quickpulse._projection import (
    _create_projections,
)
from azure.monitor.opentelemetry.exporter._quickpulse._state import (
    _QuickpulseState,
    _is_post_state,
    _append_quickpulse_document,
    _get_quickpulse_derived_metric_infos,
    _get_quickpulse_doc_stream_infos,
    _set_global_quickpulse_state,
)
from azure.monitor.opentelemetry.exporter._quickpulse._types import (
    _DependencyData,
    _ExceptionData,
    _RequestData,
    _TelemetryData,
    _TraceData,
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

_logger = logging.getLogger(__name__)


PROCESS = psutil.Process()
NUM_CPUS = psutil.cpu_count()


def enable_live_metrics(**kwargs: Any) -> None:  # pylint: disable=C4758
    """Live metrics entry point.

    :keyword str connection_string: The connection string used for your Application Insights resource.
    :keyword Resource resource: The OpenTelemetry Resource used for this Python application.
    :keyword TokenCredential credential: Token credential, such as ManagedIdentityCredential or
        ClientSecretCredential, used for Azure Active Directory (AAD) authentication. Defaults to None.
    :rtype: None
    """
    _QuickpulseManager(**kwargs)
    # We can detect feature usage for statsbeat since we are in an opt-in model currently
    # Once we move to live metrics on-by-default, we will have to check for both explicit usage
    # and whether or not user is actually using live metrics (being on live metrics blade in UX)
    set_statsbeat_live_metrics_feature_set()


# pylint: disable=protected-access,too-many-instance-attributes
class _QuickpulseManager(metaclass=Singleton):

    def __init__(self, **kwargs: Any) -> None:
        _set_global_quickpulse_state(_QuickpulseState.PING_SHORT)
        self._exporter = _QuickpulseExporter(**kwargs)
        part_a_fields = {}
        resource = kwargs.get("resource")
        if not resource:
            resource = Resource.create({})
        part_a_fields = _populate_part_a_fields(resource)
        id_generator = RandomIdGenerator()
        self._base_monitoring_data_point = MonitoringDataPoint(
            version=_get_sdk_version(),
            # Invariant version 5 indicates filtering is supported
            invariant_version=5,
            instance=part_a_fields.get(ContextTagKeys.AI_CLOUD_ROLE_INSTANCE, ""),
            role_name=part_a_fields.get(ContextTagKeys.AI_CLOUD_ROLE, ""),
            machine_name=platform.node(),
            stream_id=str(id_generator.generate_trace_id()),
            is_web_app=_is_on_app_service(),
            performance_collection_supported=True,
        )
        self._reader = _QuickpulseMetricReader(self._exporter, self._base_monitoring_data_point)
        self._meter_provider = MeterProvider(
            metric_readers=[self._reader],
            resource=resource,
        )
        self._meter = self._meter_provider.get_meter("azure_monitor_live_metrics")

        self._request_duration = self._meter.create_histogram(
            _REQUEST_DURATION_NAME[0], "ms", "live metrics avg request duration in ms"
        )
        self._dependency_duration = self._meter.create_histogram(
            _DEPENDENCY_DURATION_NAME[0], "ms", "live metrics avg dependency duration in ms"
        )
        # We use a counter to represent rates per second because collection
        # interval is one second so we simply need the number of requests
        # within the collection interval
        self._request_rate_counter = self._meter.create_counter(
            _REQUEST_RATE_NAME[0], "req/sec", "live metrics request rate per second"
        )
        self._request_failed_rate_counter = self._meter.create_counter(
            _REQUEST_FAILURE_RATE_NAME[0], "req/sec", "live metrics request failed rate per second"
        )
        self._dependency_rate_counter = self._meter.create_counter(
            _DEPENDENCY_RATE_NAME[0], "dep/sec", "live metrics dependency rate per second"
        )
        self._dependency_failure_rate_counter = self._meter.create_counter(
            _DEPENDENCY_FAILURE_RATE_NAME[0], "dep/sec", "live metrics dependency failure rate per second"
        )
        self._exception_rate_counter = self._meter.create_counter(
            _EXCEPTION_RATE_NAME[0], "exc/sec", "live metrics exception rate per second"
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
            try:
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

                # Derive metrics for quickpulse filtering
                data = _TelemetryData._from_span(span)
                _derive_metrics_from_telemetry_data(data)

                # Process docs for quickpulse filtering
                _apply_document_filters_from_telemetry_data(data)

                # Derive exception metrics from span events
                if span.events:
                    for event in span.events:
                        if event.name == "exception":
                            self._exception_rate_counter.add(1)
                            # Derive metrics for quickpulse filtering for exception
                            exc_data = _ExceptionData._from_span_event(event)
                            _derive_metrics_from_telemetry_data(exc_data)
                            # Process docs for quickpulse filtering for exception
                            _apply_document_filters_from_telemetry_data(exc_data)
            except Exception:  # pylint: disable=broad-except
                _logger.exception("Exception occurred while recording span.")

    def _record_log_record(self, log_data: LogData) -> None:
        # Only record if in post state
        if _is_post_state():
            try:
                if log_data.log_record:
                    exc_type = None
                    log_record = log_data.log_record
                    if log_record.attributes:
                        exc_type = log_record.attributes.get(SpanAttributes.EXCEPTION_TYPE)
                        exc_message = log_record.attributes.get(SpanAttributes.EXCEPTION_MESSAGE)
                        if exc_type is not None or exc_message is not None:
                            self._exception_rate_counter.add(1)

                    # Derive metrics for quickpulse filtering
                    data = _TelemetryData._from_log_record(log_record)
                    _derive_metrics_from_telemetry_data(data)

                    # Process docs for quickpulse filtering
                    _apply_document_filters_from_telemetry_data(data, exc_type)  # type: ignore
            except Exception:  # pylint: disable=broad-except
                _logger.exception("Exception occurred while recording log record.")


# Filtering

# Called by record_span/record_log when processing a span/log_record for metrics filtering
# Derives metrics from projections if applicable to current filters in config
def _derive_metrics_from_telemetry_data(data: _TelemetryData):
    metric_infos_dict: Dict[TelemetryType, List[DerivedMetricInfo]] = _get_quickpulse_derived_metric_infos()
    # if empty, filtering was not configured
    if not metric_infos_dict:
        return
    metric_infos = []  # type: ignore
    if isinstance(data, _RequestData):
        metric_infos = metric_infos_dict.get(TelemetryType.REQUEST)  # type: ignore
    elif isinstance(data, _DependencyData):
        metric_infos = metric_infos_dict.get(TelemetryType.DEPENDENCY)  # type: ignore
    elif isinstance(data, _ExceptionData):
        metric_infos = metric_infos_dict.get(TelemetryType.EXCEPTION)  # type: ignore
    elif isinstance(data, _TraceData):
        metric_infos = metric_infos_dict.get(TelemetryType.TRACE)  # type: ignore
    if metric_infos and _check_metric_filters(metric_infos, data):
        # Since this data matches the filter, create projections used to
        # generate filtered metrics
        _create_projections(metric_infos, data)


# Called by record_span/record_log when processing a span/log_record for docs filtering
# Finds doc stream Ids and their doc filter configurations
def _apply_document_filters_from_telemetry_data(data: _TelemetryData, exc_type: Optional[str] = None):
    doc_config_dict: Dict[TelemetryType, Dict[str, List[FilterConjunctionGroupInfo]]] = _get_quickpulse_doc_stream_infos()  # pylint: disable=C0301
    stream_ids = set()
    doc_config = {}  # type: ignore
    if isinstance(data, _RequestData):
        doc_config = doc_config_dict.get(TelemetryType.REQUEST, {})  # type: ignore
    elif isinstance(data, _DependencyData):
        doc_config = doc_config_dict.get(TelemetryType.DEPENDENCY, {})  # type: ignore
    elif isinstance(data, _ExceptionData):
        doc_config = doc_config_dict.get(TelemetryType.EXCEPTION, {})  # type: ignore
    elif isinstance(data, _TraceData):
        doc_config = doc_config_dict.get(TelemetryType.TRACE, {})  # type: ignore
    for stream_id, filter_groups in doc_config.items():
        for filter_group in filter_groups:
            if _check_filters(filter_group.filters, data):
                stream_ids.add(stream_id)
                break

    # We only append and send the document if either:
    # 1. The document matched the filtering for a specific streamId
    # 2. Filtering was not enabled for this telemetry type (empty doc_config)
    if len(stream_ids) > 0 or not doc_config:
        if type(data) in (_DependencyData, _RequestData):
            document = _get_span_document(data)  # type: ignore
        else:
            document = _get_log_record_document(data, exc_type)  # type: ignore
        # A stream (with a unique streamId) is relevant if there are multiple sources sending to the same
        # ApplicationInsights instace with live metrics enabled
        # Modify the document's streamIds to determine which stream to send to in post
        # Note that the default case is that the list of document_stream_ids is empty, in which
        # case no filtering is done for the telemetry type and it is sent to all streams
        if stream_ids:
            document.document_stream_ids = list(stream_ids)

        # Add the generated document to be sent to quickpulse
        _append_quickpulse_document(document)

# cSpell:enable
