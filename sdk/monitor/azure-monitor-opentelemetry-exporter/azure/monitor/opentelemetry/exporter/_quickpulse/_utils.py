# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple, Union

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
    _QUICKPULSE_PROJECTION_MAX_VALUE,
    _QUICKPULSE_PROJECTION_MIN_VALUE,
)
from azure.monitor.opentelemetry.exporter._quickpulse._generated.models import (
    AggregationType,
    DocumentIngress,
    DocumentType,
    Exception as ExceptionDocument,
    MetricPoint,
    MonitoringDataPoint,
    RemoteDependency as RemoteDependencyDocument,
    Request as RequestDocument,
    Trace as TraceDocument,
)
from azure.monitor.opentelemetry.exporter._quickpulse._state import (
    _get_quickpulse_projection_map,
    _reset_quickpulse_projection_map,
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


# Time


def _ns_to_iso8601_string(nanoseconds: int) -> str:
    seconds, nanoseconds_remainder = divmod(nanoseconds, 1e9)
    microseconds = nanoseconds_remainder // 1000  # Convert nanoseconds to microseconds
    dt = datetime.utcfromtimestamp(seconds)
    dt_microseconds = timedelta(microseconds=microseconds)
    dt_with_microseconds = dt + dt_microseconds
    return dt_with_microseconds.isoformat()


def _filter_time_stamp_to_ms(time_stamp: str) -> Optional[int]:
    # The service side will return a timestamp in the following format:
    # [days].[hours]:[minutes]:[seconds]
    # the seconds may be a whole number or something like 7.89. 7.89 seconds translates to 7890 ms.
    # examples: "14.6:56:7.89" = 1234567890 ms, "0.0:0:0.2" = 200 ms
    total_milliseconds = None
    try:
        days_hours, minutes, seconds = time_stamp.split(":")
        days, hours = map(float, days_hours.split("."))
        total_milliseconds = int(
            days * 24 * 60 * 60 * 1000  # days to milliseconds
            + hours * 60 * 60 * 1000  # hours to milliseconds
            + float(minutes) * 60 * 1000  # minutes to milliseconds
            + float(seconds) * 1000  # seconds to milliseconds
        )
    except Exception:  # pylint: disable=broad-except,invalid-name
        pass
    return total_milliseconds
