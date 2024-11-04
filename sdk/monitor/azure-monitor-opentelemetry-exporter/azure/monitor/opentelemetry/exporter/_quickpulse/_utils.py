# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from dataclasses import fields
from datetime import datetime, timedelta, timezone
import json
from typing import Dict, List, Optional, Tuple, Union

from opentelemetry.sdk._logs import LogData
from opentelemetry.sdk.metrics._internal.point import (
    NumberDataPoint,
    HistogramDataPoint,
)
from opentelemetry.sdk.metrics.export import MetricsData as OTMetricsData
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import SpanKind

from azure.monitor.opentelemetry.exporter._quickpulse._constants import (
    _QUICKPULSE_METRIC_NAME_MAPPINGS,
    _QUICKPULSE_PROJECTION_COUNT,
    _QUICKPULSE_PROJECTION_CUSTOM,
    _QUICKPULSE_PROJECTION_DURATION,
    _QUICKPULSE_PROJECTION_MAX_VALUE,
    _QUICKPULSE_PROJECTION_MIN_VALUE,
)
from azure.monitor.opentelemetry.exporter._quickpulse._generated.models import (
    AggregationType,
    DerivedMetricInfo,
    DocumentIngress,
    DocumentType,
    Exception as ExceptionDocument,
    FilterInfo,
    MetricPoint,
    MonitoringDataPoint,
    PredicateType,
    RemoteDependency as RemoteDependencyDocument,
    Request as RequestDocument,
    TelemetryType,
    Trace as TraceDocument,
)
from azure.monitor.opentelemetry.exporter._quickpulse._state import (
    _clear_quickpulse_projection_map,
    _get_quickpulse_derived_metric_infos,
    _get_quickpulse_projection_map,
    _reset_quickpulse_projection_map,
    _set_quickpulse_derived_metric_infos,
    _set_quickpulse_etag,
    _set_quickpulse_projection_map,
)
from azure.monitor.opentelemetry.exporter._quickpulse._types import (
    _DEPENDENCY_DATA_FIELD_NAMES,
    _KNOWN_STRING_FIELD_NAMES,
    _REQUEST_DATA_FIELD_NAMES,
    _DependencyData,
    _ExceptionData,
    _RequestData,
    _TelemetryData,
    _TraceData,
)
from azure.monitor.opentelemetry.exporter.export.trace._utils import (
    _get_url_for_http_dependency,
    _get_url_for_http_request,
)


def _metric_to_quick_pulse_data_points(  # pylint: disable=too-many-nested-blocks
    metrics_data: OTMetricsData,
    base_monitoring_data_point: MonitoringDataPoint,
    documents: Optional[List[DocumentIngress]],
) -> List[MonitoringDataPoint]:
    metric_points = []
    for resource_metric in metrics_data.resource_metrics:
        for scope_metric in resource_metric.scope_metrics:
            for metric in scope_metric.metrics:
                for point in metric.data.data_points:
                    if point is not None:
                        value = 0
                        if isinstance(point, HistogramDataPoint):
                            if point.count > 0:
                                value = point.sum / point.count
                        elif isinstance(point, NumberDataPoint):
                            value = point.value
                        metric_point = MetricPoint(
                            name=_QUICKPULSE_METRIC_NAME_MAPPINGS[metric.name.lower()],  # type: ignore
                            weight=1,
                            value=value,
                        )
                        metric_points.append(metric_point)
    # Process filtered metrics
    for metric in _get_metrics_from_projections():
        metric_point = MetricPoint(
            name=metric[0],  # type: ignore
            weight=1,
            value=metric[1],  # type: ignore
        )
        metric_points.append(metric_point)

    # Reset projection map for next collection cycle
    _reset_quickpulse_projection_map()

    return [
        MonitoringDataPoint(
            version=base_monitoring_data_point.version,
            invariant_version=base_monitoring_data_point.invariant_version,
            instance=base_monitoring_data_point.instance,
            role_name=base_monitoring_data_point.role_name,
            machine_name=base_monitoring_data_point.machine_name,
            stream_id=base_monitoring_data_point.stream_id,
            is_web_app=base_monitoring_data_point.is_web_app,
            performance_collection_supported=base_monitoring_data_point.performance_collection_supported,
            timestamp=datetime.now(tz=timezone.utc),
            metrics=metric_points,
            documents=documents,
        )
    ]


# mypy: disable-error-code="assignment,union-attr"
def _get_span_document(span: ReadableSpan) -> Union[RemoteDependencyDocument, RequestDocument]:
    duration = 0
    if span.end_time and span.start_time:
        duration = span.end_time - span.start_time
    status_code = span.attributes.get(SpanAttributes.HTTP_STATUS_CODE, "")  # type: ignore
    grpc_status_code = span.attributes.get(SpanAttributes.RPC_GRPC_STATUS_CODE, "")  # type: ignore
    span_kind = span.kind
    if span_kind in (SpanKind.CLIENT, SpanKind.PRODUCER, SpanKind.INTERNAL):
        url = _get_url_for_http_dependency(span.attributes)
        document = RemoteDependencyDocument(
            document_type=DocumentType.REMOTE_DEPENDENCY,
            name=span.name,
            command_name=url,
            result_code=str(status_code),
            duration=_ns_to_iso8601_string(duration),
        )
    else:
        url = _get_url_for_http_request(span.attributes)
        if status_code:
            code = str(status_code)
        else:
            code = str(grpc_status_code)
        document = RequestDocument(
            document_type=DocumentType.REQUEST,
            name=span.name,
            url=url,
            response_code=code,
            duration=_ns_to_iso8601_string(duration),
        )
    return document


# mypy: disable-error-code="assignment"
def _get_log_record_document(log_data: LogData) -> Union[ExceptionDocument, TraceDocument]:
    exc_type = log_data.log_record.attributes.get(SpanAttributes.EXCEPTION_TYPE)  # type: ignore
    exc_message = log_data.log_record.attributes.get(SpanAttributes.EXCEPTION_MESSAGE)  # type: ignore
    if exc_type is not None or exc_message is not None:
        document = ExceptionDocument(
            document_type=DocumentType.EXCEPTION,
            exception_type=str(exc_type),
            exception_message=str(exc_message),
        )
    else:
        document = TraceDocument(
            document_type=DocumentType.TRACE,
            message=log_data.log_record.body,
        )
    return document


def _ns_to_iso8601_string(nanoseconds: int) -> str:
    seconds, nanoseconds_remainder = divmod(nanoseconds, 1e9)
    microseconds = nanoseconds_remainder // 1000  # Convert nanoseconds to microseconds
    dt = datetime.utcfromtimestamp(seconds)
    dt_microseconds = timedelta(microseconds=microseconds)
    dt_with_microseconds = dt + dt_microseconds
    return dt_with_microseconds.isoformat()


# Filtering


def _update_filter_configuration(etag: str, config_bytes: bytes):
    # Clear projection map
    _clear_quickpulse_projection_map()
    seen_ids = set()
    # config is a byte string that when decoded is a json
    config = json.loads(config_bytes.decode("utf-8"))
    metric_infos: Dict[TelemetryType, List[DerivedMetricInfo]] = {}
    for metric_info_dict in config.get("Metrics", []):
        metric_info = DerivedMetricInfo.from_dict(metric_info_dict)
        # Skip duplicate ids
        if metric_info.id in seen_ids:
            continue
        # Validate derived metric info
        if not _validate_derived_metric_info(metric_info):
            continue
        telemetry_type: TelemetryType = TelemetryType(metric_info.telemetry_type)
        # TODO: Filter out invalid configs: telemetry type, operand
        # TODO: Rename exception fields
        metric_info_list = metric_infos.get(telemetry_type, [])
        metric_info_list.append(metric_info)
        metric_infos[telemetry_type] = metric_info_list
        seen_ids.add(metric_info.id)
        # Initialize projections from this derived metric info
        _init_derived_metric_projection(metric_info)
    _set_quickpulse_derived_metric_infos(metric_infos)
    # Update new etag
    _set_quickpulse_etag(etag)


# Called by record_span/record_log when processing a span/log_record
# Derives metrics from projections if applicable to current filters in config
def _derive_metrics_from_telemetry_data(data: _TelemetryData):
    metric_infos_dict = _get_quickpulse_derived_metric_infos()
    metric_infos = []  # type: ignore
    if isinstance(data, _RequestData):
        metric_infos = metric_infos_dict.get(TelemetryType.REQUEST)
    elif isinstance(data, _DependencyData):
        metric_infos = metric_infos_dict.get(TelemetryType.DEPENDENCY)
    elif isinstance(data, _ExceptionData):
        metric_infos = metric_infos_dict.get(TelemetryType.EXCEPTION)
    elif isinstance(data, _TraceData):
        metric_infos = metric_infos_dict.get(TelemetryType.TRACE)
    if metric_infos and _check_metric_filters(metric_infos, data):
        # Since this data matches the filter, create projections used to
        # generate filtered metrics
        _create_projections(metric_infos, data)
    # TODO: Configuration error handling


def _check_metric_filters(metric_infos: List[DerivedMetricInfo], data: _TelemetryData) -> bool:
    match = False
    for metric_info in metric_infos:
        # Should only be a single `FilterConjunctionGroupInfo` in `filter_groups`
        # but we use a logical OR to match if there is more than one
        for group in metric_info.filter_groups:
            match = match or _check_filters(group.filters, data)
    return match


# pylint: disable=unused-argument
def _check_filters(filters: List[FilterInfo], data: _TelemetryData) -> bool:
    # # All of the filters need to match for this to return true (and operation).
    # for filter in filters:
    #     # TODO: apply filter logic
    #     pass
    return True


# Validation

def _validate_derived_metric_info(metric_info: DerivedMetricInfo) -> bool:
    # Validate telemetry type
    try:
        telemetry_type = TelemetryType(metric_info.telemetry_type)
    except Exception:  # pylint: disable=broad-except,invalid-name
        return False
    # Only REQUEST, DEPENDENCY, EXCEPTION, TRACE are supported
    # No filtering options in UX for PERFORMANCE_COUNTERS
    if not telemetry_type in (TelemetryType.REQUEST, TelemetryType.DEPENDENCY, TelemetryType.EXCEPTION, TelemetryType.TRACE):
        return False
    # Check for CustomMetric projection
    if metric_info.projection and metric_info.projection.startswith("CustomMetrics."):
        return False
    # Validate filters
    for filter_group in metric_info.filter_groups:
        for filter in filter_group.filters:
            # Validate field names to telemetry type
            # Validate predicate and comparands
            if not _validate_filter_field_name(filter, telemetry_type) or \
            not _validate_filter_predicate_and_comparand(filter):
                return False
    return True


def _validate_filter_field_name(filter: FilterInfo, telemetry_type: TelemetryType) -> bool:
    name = filter.field_name
    if not name:
        return False
    if name.startswith("CustomMetrics"):
        return False
    if name.startswith("CustomDimensions") or name == "*":
        return True
    name = name.lower()
    if telemetry_type == TelemetryType.DEPENDENCY:
        if name not in _DEPENDENCY_DATA_FIELD_NAMES:
            return False
    elif telemetry_type == TelemetryType.REQUEST:
        if name not in _REQUEST_DATA_FIELD_NAMES:
            return False
    elif telemetry_type == TelemetryType.EXCEPTION:
        if name not in ("exception.message", "exception.stacktrace"):
            return False
    elif telemetry_type == TelemetryType.TRACE:
        if name != "message":
            return False
    else:
        return True
    return True


def _validate_filter_predicate_and_comparand(filter: FilterInfo) -> bool:
    name = filter.field_name
    comparand = filter.comparand
    # Validate predicate type
    try:
        predicate = PredicateType(filter.predicate)
    except Exception:  # pylint: disable=broad-except,invalid-name
        return False
    if not comparand:
        return False
    if name == "*" and predicate not in (PredicateType.CONTAINS, PredicateType.DOES_NOT_CONTAIN):
        return False
    if name in ("ResultCode", "ResponseCode", "Duration"):
        if predicate in (PredicateType.CONTAINS, PredicateType.DOES_NOT_CONTAIN):
            return False
        if name == "Duration":
            # Duration comparand should be a string timestamp
            if _filter_time_stamp_to_ms(comparand) is None:
                return False
        else:
            try:
                # Response/ResultCode comparand should be interpreted as integer
                int(comparand)
            except Exception:  # pylint: disable=broad-except,invalid-name
                return False
    elif name == "Success":
        if predicate not in (PredicateType.EQUAL, PredicateType.NOT_EQUAL):
            return False
        comparand = comparand.lower()
        if comparand not in ("true", "false"):
            return False
    elif name in _KNOWN_STRING_FIELD_NAMES or name.startswith("CustomDimensions."):
        if predicate in (PredicateType.GREATER_THAN, PredicateType.GREATER_THAN_OR_EQUAL, PredicateType.LESS_THAN, PredicateType.LESS_THAN_OR_EQUAL):
            return False
    return True

        
def _filter_time_stamp_to_ms(time_stamp: str) -> Optional[int]:
    # The service side will return a timestamp in the following format:
    # [days].[hours]:[minutes]:[seconds]
    # the seconds may be a whole number or something like 7.89. 7.89 seconds translates to 7890 ms.
    # examples: "14.6:56:7.89" = 1234567890 ms, "0.0:0:0.2" = 200 ms
    total_milliseconds = None
    try:
        days_hours, minutes, seconds = time_stamp.split(':')
        days, hours = map(float, days_hours.split('.'))
        total_milliseconds = int(
            days * 24 * 60 * 60 * 1000 +  # days to milliseconds
            hours * 60 * 60 * 1000 +           # hours to milliseconds
            float(minutes) * 60 * 1000 +               # minutes to milliseconds
            float(seconds) * 1000                      # seconds to milliseconds
        )
    except Exception:  # pylint: disable=broad-except,invalid-name
        pass
    return total_milliseconds


# Projections


# Initialize metric projections per DerivedMetricInfo
def _init_derived_metric_projection(filter_info: DerivedMetricInfo):
    derived_metric_agg_value = 0
    if filter_info.aggregation == AggregationType.MIN:
        derived_metric_agg_value = _QUICKPULSE_PROJECTION_MAX_VALUE
    elif filter_info.aggregation == AggregationType.MAX:
        derived_metric_agg_value = _QUICKPULSE_PROJECTION_MIN_VALUE
    elif filter_info.aggregation == AggregationType.SUM:
        derived_metric_agg_value = 0
    elif filter_info.aggregation == AggregationType.AVG:
        derived_metric_agg_value = 0
    _set_quickpulse_projection_map(
        filter_info.id,
        AggregationType(filter_info.aggregation),
        derived_metric_agg_value,
        0,
    )


# Create projections based off of DerivedMetricInfos and current data being processed
def _create_projections(metric_infos: List[DerivedMetricInfo], data: _TelemetryData):
    for metric_info in metric_infos:
        value = 0
        if metric_info.projection == _QUICKPULSE_PROJECTION_COUNT:
            value = 1
        elif metric_info.projection == _QUICKPULSE_PROJECTION_DURATION:
            if isinstance(data, (_DependencyData, _RequestData)):
                value = data.duration
            else:
                continue
        elif metric_info.projection.startswith(_QUICKPULSE_PROJECTION_CUSTOM):
            key = metric_info.projection.split(_QUICKPULSE_PROJECTION_CUSTOM, 1)[1].strip()
            dim_value = data.custom_dimensions.get(key, 0)
            try:
                value = float(dim_value)
            except ValueError:
                continue

        aggregate: Optional[Tuple[float, int]] = _calculate_aggregation(
            AggregationType(metric_info.aggregation),
            metric_info.id,
            value,
        )
        if aggregate:
            _set_quickpulse_projection_map(
                metric_info.id,
                AggregationType(metric_info.aggregation),
                aggregate[0],
                aggregate[1],
            )


# Calculate aggregation based off of previous projection value, aggregation type of a specific metric filter
# Return type is a Tuple of (value, count)
def _calculate_aggregation(aggregation: AggregationType, id: str, value: float) -> Optional[Tuple[float, int]]:
    projection: Optional[Tuple[AggregationType, float, int]] = _get_quickpulse_projection_map().get(id)
    if projection:
        prev_value = projection[1]
        prev_count = projection[2]
        if aggregation == AggregationType.SUM:
            return (prev_value + value, prev_count + 1)
        elif aggregation == AggregationType.MIN:
            return (min(prev_value, value), prev_count + 1)
        elif aggregation == AggregationType.MAX:
            return (max(prev_value, value), prev_count + 1)
        elif aggregation == AggregationType.AVG:
            return (prev_value + value, prev_count + 1)
    return None


# Gets filtered metrics from projections to be exported
# Called every second on export
def _get_metrics_from_projections() -> List[Tuple[str, float]]:
    metrics = []
    projection_map = _get_quickpulse_projection_map()
    for id, projection in projection_map.items():
        metric_value = 0
        aggregation_type = projection[0]
        if aggregation_type == AggregationType.MIN:
            metric_value = 0 if projection[1] == _QUICKPULSE_PROJECTION_MAX_VALUE else projection[1]
        elif aggregation_type == AggregationType.MAX:
            metric_value = 0 if projection[1] == _QUICKPULSE_PROJECTION_MIN_VALUE else projection[1]
        elif aggregation_type == AggregationType.AVG:
            metric_value = 0 if projection[2] == 0 else projection[1] / float(projection[2])
        elif aggregation_type == AggregationType.SUM:
            metric_value = projection[1]
        metrics.append((id, metric_value))
    return metrics  # type: ignore
