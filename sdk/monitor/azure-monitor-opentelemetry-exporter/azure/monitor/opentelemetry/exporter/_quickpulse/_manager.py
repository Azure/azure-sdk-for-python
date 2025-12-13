# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# cSpell:disable
from typing import Any, Dict, List, Optional

import logging
import platform
import threading

import psutil

from opentelemetry.sdk._logs import ReadableLogRecord
from opentelemetry.sdk.metrics import MeterProvider, Meter
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
from azure.monitor.opentelemetry.exporter._utils import (
    _get_sdk_version,
    _is_on_app_service,
    _populate_part_a_fields,
    Singleton,
)

_logger = logging.getLogger(__name__)


PROCESS = psutil.Process()
NUM_CPUS = psutil.cpu_count()


# pylint: disable=protected-access,too-many-instance-attributes
class _QuickpulseManager(metaclass=Singleton):

    def __init__(self) -> None:
        """Initialize the QuickpulseManager singleton.

        Basic initialization without configuration. Use initialize() method
        to configure and start the manager with connection parameters.
        """
        # Initialize instance attributes. Called only once due to Singleton metaclass.
        self._lock = threading.Lock()
        self._initialized: bool = False

        # Configuration parameters - set during initialize()
        self._connection_string: Optional[str] = None
        self._credential = None
        self._resource: Optional[Resource] = None

        # Components that depend on configuration - created during initialize()
        self._base_monitoring_data_point: Optional[MonitoringDataPoint] = None
        self._meter_provider: Optional[MeterProvider] = None
        self._meter: Optional[Meter] = None
        self._exporter: Optional[_QuickpulseExporter] = None
        self._reader: Optional[_QuickpulseMetricReader] = None

        # Metric instruments - created during initialize()
        self._request_duration = None
        self._dependency_duration = None
        self._request_rate_counter = None
        self._request_failed_rate_counter = None
        self._dependency_rate_counter = None
        self._dependency_failure_rate_counter = None
        self._exception_rate_counter = None
        self._process_memory_gauge_old = None
        self._process_memory_gauge = None
        self._process_time_gauge_old = None
        self._process_time_gauge = None

    # pylint:disable=docstring-should-be-keyword
    def initialize(self, **kwargs: Any) -> bool:
        """Initialize the QuickpulseManager with configuration parameters.

        Expected keyword arguments:
        :param connection_string: The connection string used for your Application Insights resource
        :type connection_string: Optional[str]
        :param credential: Token credential for Azure Active Directory authentication
        :type credential: Optional[Any]
        :param resource: The OpenTelemetry Resource used for this Python application.
            This is the primary parameter used by the underlying _QuickpulseExporter.
        :type resource: Optional[Resource]

        :return: True if initialization was successful, False otherwise
        :rtype: bool
        """
        with self._lock:
            if self._initialized:
                # Manager is already initialized, no need to reinitialize
                _logger.debug("QuickpulseManager is already initialized.")
                return True

            # Extract and store configuration parameters from kwargs
            self._connection_string = kwargs.get("connection_string")
            self._credential = kwargs.get("credential")
            self._resource = kwargs.get("resource")

            # Initialize using the configuration parameters
            return self._do_initialize()

    def _do_initialize(self) -> bool:
        # Internal initialization method.
        try:
            _set_global_quickpulse_state(_QuickpulseState.PING_SHORT)

            # Use provided resource or create default
            resource = self._resource
            if not resource:
                resource = Resource.create({})

            # Create base monitoring data point
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

            # Create exporter with explicit parameters
            exporter_kwargs = {}
            if self._connection_string:
                exporter_kwargs["connection_string"] = self._connection_string
            if self._credential:
                exporter_kwargs["credential"] = self._credential

            self._exporter = _QuickpulseExporter(**exporter_kwargs)
            self._reader = _QuickpulseMetricReader(self._exporter, self._base_monitoring_data_point)
            self._meter_provider = MeterProvider(
                metric_readers=[self._reader],
                resource=resource,
            )
            self._meter = self._meter_provider.get_meter("azure_monitor_live_metrics")

            # Create metric instruments
            self._create_metric_instruments()

            # Only set initialized to True after everything succeeds
            self._initialized = True
            _logger.info("QuickpulseManager initialized successfully.")
            return True

        except Exception as e:  # pylint: disable=broad-except
            _logger.warning("Failed to initialize QuickpulseManager: %s", e)
            # Ensure cleanup happens and state is consistent
            self._cleanup()
            return False

    def _create_metric_instruments(self) -> None:
        """Create all metric instruments. Called during initialization."""
        if not self._meter:
            raise ValueError("Meter must be initialized before creating instruments")

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

    def shutdown(self) -> bool:
        # Shutdown the QuickpulseManager
        with self._lock:
            if not self._initialized:
                return False

            shutdown_success = False
            try:
                if self._meter_provider is not None:
                    # Store reference before cleanup to avoid race conditions
                    meter_provider = self._meter_provider
                    meter_provider.shutdown()
                    shutdown_success = True
            except Exception:  # pylint: disable=broad-except
                pass
            finally:
                self._cleanup(shutdown_meter_provider=False)

            if shutdown_success:
                _set_global_quickpulse_state(_QuickpulseState.OFFLINE)

            return shutdown_success

    def _cleanup(self, shutdown_meter_provider: bool = True) -> None:
        # Clean up resources with optional meter provider shutdown
        if shutdown_meter_provider and self._meter_provider:
            try:
                self._meter_provider.shutdown()
            except Exception:  # pylint: disable=broad-except
                pass
        # We leave connection_string, credential, and resource intact for potential re-initialization
        self._exporter = None
        self._reader = None
        self._meter_provider = None
        self._meter = None
        self._base_monitoring_data_point = None
        self._initialized = False

    def is_initialized(self) -> bool:
        """Check if the manager is initialized.

        :return: True if initialized, False otherwise
        :rtype: bool
        """
        with self._lock:
            return self._initialized

    # Quickpulse recording methods

    def _record_span(self, span: ReadableSpan) -> None:
        # Only record if in post state and manager is initialized
        if not (_is_post_state() and self.is_initialized()):
            return

        # Validate required resources are available
        if not self._validate_recording_resources():
            _logger.warning("QuickpulseManager: Cannot record span, resources not properly initialized")
            return

        try:
            duration_ms = 0
            if span.end_time and span.start_time:
                duration_ms = (span.end_time - span.start_time) / 1e9  # type: ignore
            # TODO: Spec out what "success" is
            success = span.status.is_ok

            if span.kind in (SpanKind.SERVER, SpanKind.CONSUMER):
                if success:
                    self._request_rate_counter.add(1)  # type: ignore
                else:
                    self._request_failed_rate_counter.add(1)  # type: ignore
                self._request_duration.record(duration_ms)  # type: ignore
            else:
                if success:
                    self._dependency_rate_counter.add(1)  # type: ignore
                else:
                    self._dependency_failure_rate_counter.add(1)  # type: ignore
                self._dependency_duration.record(duration_ms)  # type: ignore

            # Derive metrics for quickpulse filtering
            data = _TelemetryData._from_span(span)
            _derive_metrics_from_telemetry_data(data)

            # Process docs for quickpulse filtering
            _apply_document_filters_from_telemetry_data(data)

            # Derive exception metrics from span events
            if span.events:
                for event in span.events:
                    if event.name == "exception":
                        self._exception_rate_counter.add(1)  # type: ignore
                        # Derive metrics for quickpulse filtering for exception
                        exc_data = _ExceptionData._from_span_event(event)
                        _derive_metrics_from_telemetry_data(exc_data)
                        # Process docs for quickpulse filtering for exception
                        _apply_document_filters_from_telemetry_data(exc_data)
        except Exception as e:  # pylint: disable=broad-except
            _logger.exception("Exception occurred while recording span: %s", e)  # pylint: disable=C4769

    def _record_log_record(self, readable_log_record: ReadableLogRecord) -> None:
        # Only record if in post state and manager is initialized
        if not (_is_post_state() and self.is_initialized()):
            return

        # Validate required resources are available
        if not self._validate_recording_resources():
            _logger.warning("QuickpulseManager: Cannot record log, resources not properly initialized")
            return

        try:
            if readable_log_record.log_record:
                exc_type = None
                log_record = readable_log_record.log_record
                if log_record.attributes:
                    exc_type = log_record.attributes.get(SpanAttributes.EXCEPTION_TYPE)
                    exc_message = log_record.attributes.get(SpanAttributes.EXCEPTION_MESSAGE)
                    if exc_type is not None or exc_message is not None:
                        self._exception_rate_counter.add(1)  # type: ignore

                # Derive metrics for quickpulse filtering
                data = _TelemetryData._from_log_record(log_record)
                _derive_metrics_from_telemetry_data(data)

                # Process docs for quickpulse filtering
                _apply_document_filters_from_telemetry_data(data, exc_type)  # type: ignore
        except Exception as e:  # pylint: disable=broad-except
            _logger.exception("Exception occurred while recording log record: %s", e)  # pylint: disable=C4769

    def _validate_recording_resources(self) -> bool:
        """Validate that all required resources for recording are available.

        :return: True if all required resources are available, False otherwise
        :rtype: bool
        """
        return all([
            self._request_rate_counter is not None,
            self._request_failed_rate_counter is not None,
            self._request_duration is not None,
            self._dependency_rate_counter is not None,
            self._dependency_failure_rate_counter is not None,
            self._dependency_duration is not None,
            self._exception_rate_counter is not None,
        ])


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
