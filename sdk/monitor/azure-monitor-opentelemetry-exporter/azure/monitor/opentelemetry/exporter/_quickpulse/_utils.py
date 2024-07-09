# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Union

from opentelemetry.sdk._logs import LogData
from opentelemetry.sdk.metrics._internal.point import (
    NumberDataPoint,
    HistogramDataPoint,
)
from opentelemetry.sdk.metrics.export import MetricsData as OTMetricsData
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import SpanKind
from opentelemetry.util.types import Attributes

from azure.monitor.opentelemetry.exporter._quickpulse._constants import (
    _DocumentIngressDocumentType,
    _QUICKPULSE_METRIC_NAME_MAPPINGS,
)
from azure.monitor.opentelemetry.exporter._quickpulse._generated.models import (
    DocumentIngress,
    Exception as ExceptionDocument,
    MetricPoint,
    MonitoringDataPoint,
    RemoteDependency as RemoteDependencyDocument,
    Request as RequestDocument,
    Trace as TraceDocument,
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
                            name=_QUICKPULSE_METRIC_NAME_MAPPINGS[metric.name.lower()],
                            weight=1,
                            value=value
                        )
                        metric_points.append(metric_point)
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
    url = _get_url(span_kind, span.attributes)
    if span_kind in (SpanKind.CLIENT, SpanKind.PRODUCER, SpanKind.INTERNAL):
        document = RemoteDependencyDocument(
            document_type=_DocumentIngressDocumentType.RemoteDependency.value,
            name=span.name,
            command_name=url,
            result_code=str(status_code),
            duration=_ns_to_iso8601_string(duration),
        )
    else:
        if status_code:
            code = str(status_code)
        else:
            code = str(grpc_status_code)
        document = RequestDocument(
            document_type=_DocumentIngressDocumentType.Request.value,
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
            document_type=_DocumentIngressDocumentType.Exception.value,
            exception_type=str(exc_type),
            exception_message=str(exc_message),
        )
    else:
        document = TraceDocument(
            document_type=_DocumentIngressDocumentType.Trace.value,
            message=log_data.log_record.body,
        )
    return document


# mypy: disable-error-code="assignment"
# pylint: disable=no-else-return
def _get_url(span_kind: SpanKind, attributes: Attributes) -> str:
    if not attributes:
        return ""
    http_method = attributes.get(SpanAttributes.HTTP_METHOD)
    if http_method:
        http_scheme = attributes.get(SpanAttributes.HTTP_SCHEME)
        # Client
        if span_kind in (SpanKind.CLIENT, SpanKind.PRODUCER):
            http_url = attributes.get(SpanAttributes.HTTP_URL)
            if http_url:
                return str(http_url)

            host = attributes.get(SpanAttributes.NET_PEER_NAME)
            port = attributes.get(SpanAttributes.NET_PEER_PORT, "")
            ip = attributes.get(SpanAttributes.NET_PEER_IP)
            if http_scheme:
                if host:
                    return f"{http_scheme}://{host}:{port}"
                else:
                    return f"{http_scheme}://{ip}:{port}"
        else:  # Server
            host = attributes.get(SpanAttributes.NET_HOST_NAME)
            port = attributes.get(SpanAttributes.NET_HOST_PORT)
            http_target = attributes.get(SpanAttributes.HTTP_TARGET, "")
            if http_scheme and host:
                http_host = attributes.get(SpanAttributes.HTTP_HOST)
                if http_host:
                    return f"{http_scheme}://{http_host}:{port}{http_target}"
    return ""


def _ns_to_iso8601_string(nanoseconds: int) -> str:
    seconds, nanoseconds_remainder = divmod(nanoseconds, 1e9)
    microseconds = nanoseconds_remainder // 1000  # Convert nanoseconds to microseconds
    dt = datetime.utcfromtimestamp(seconds)
    dt_microseconds = timedelta(microseconds=microseconds)
    dt_with_microseconds = dt + dt_microseconds
    return dt_with_microseconds.isoformat()
