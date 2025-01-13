# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Union

from opentelemetry.sdk.metrics._internal.point import (
    NumberDataPoint,
    HistogramDataPoint,
)
from opentelemetry.sdk.metrics.export import MetricsData as OTMetricsData

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
from azure.monitor.opentelemetry.exporter._quickpulse._types import (
    _DependencyData,
    _ExceptionData,
    _RequestData,
    _TraceData,
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
def _get_span_document(data: Union[_DependencyData, _RequestData]) -> Union[RemoteDependencyDocument, RequestDocument]:
    if isinstance(data, _DependencyData):
        document = RemoteDependencyDocument(
            document_type=DocumentType.REMOTE_DEPENDENCY,
            name=data.name,
            command_name=data.data,
            result_code=str(data.result_code),
            duration=_ms_to_iso8601_string(data.duration),
        )
    else:
        document = RequestDocument(
            document_type=DocumentType.REQUEST,
            name=data.name,
            url=data.url,
            response_code=str(data.response_code),
            duration=_ms_to_iso8601_string(data.duration),
        )
    return document


# mypy: disable-error-code="assignment"
def _get_log_record_document(data: Union[_ExceptionData, _TraceData], exc_type: Optional[str] = None) -> Union[ExceptionDocument, TraceDocument]:  # pylint: disable=C0301
    if isinstance(data, _ExceptionData):
        document = ExceptionDocument(
            document_type=DocumentType.EXCEPTION,
            exception_type=exc_type or "",
            exception_message=data.message,
        )
    else:
        document = TraceDocument(
            document_type=DocumentType.TRACE,
            message=data.message,
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

def _ms_to_iso8601_string(ms: float) -> str:
    seconds, ms = divmod(ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    years, days = divmod(days, 365)
    months, days = divmod(days, 30)
    duration = f"P{years}Y{months}M{days}DT{hours}H{minutes}M{seconds}.{int(ms):03d}S"
    return duration


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
    except Exception:  # pylint: disable=broad-except
        pass
    return total_milliseconds
