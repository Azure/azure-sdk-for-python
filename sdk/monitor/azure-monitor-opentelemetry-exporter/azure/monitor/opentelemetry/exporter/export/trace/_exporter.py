# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from os import environ
import json
import logging
from time import time_ns
from typing import Any, Dict, List, Sequence
from urllib.parse import urlparse

from opentelemetry.semconv.trace import DbSystemValues, SpanAttributes
from opentelemetry.semconv._incubating.attributes import gen_ai_attributes
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from opentelemetry.trace import SpanKind, get_tracer_provider

from azure.monitor.opentelemetry.exporter._constants import (
    _APPLICATIONINSIGHTS_OPENTELEMETRY_RESOURCE_METRIC_DISABLED,
    _AZURE_SDK_NAMESPACE_NAME,
    _AZURE_SDK_OPENTELEMETRY_NAME,
    _INSTRUMENTATION_SUPPORTING_METRICS_LIST,
    _SAMPLE_RATE_KEY,
    _METRIC_ENVELOPE_NAME,
    _MESSAGE_ENVELOPE_NAME,
    _REQUEST_ENVELOPE_NAME,
    _EXCEPTION_ENVELOPE_NAME,
    _REMOTE_DEPENDENCY_ENVELOPE_NAME,
)
from azure.monitor.opentelemetry.exporter import _utils
from azure.monitor.opentelemetry.exporter._generated.models import (
    ContextTagKeys,
    MessageData,
    MetricDataPoint,
    MetricsData,
    MonitorBase,
    RemoteDependencyData,
    RequestData,
    TelemetryExceptionData,
    TelemetryExceptionDetails,
    TelemetryItem,
)
from azure.monitor.opentelemetry.exporter.export._base import (
    BaseExporter,
    ExportResult,
)
from . import _utils as trace_utils


_logger = logging.getLogger(__name__)

__all__ = ["AzureMonitorTraceExporter"]

_STANDARD_OPENTELEMETRY_ATTRIBUTE_PREFIXES = [
    "http.",
    "db.",
    "message.",
    "messaging.",
    "rpc.",
    "enduser.",
    "net.",
    "peer.",
    "exception.",
    "thread.",
    "fass.",
    "code.",
]

_STANDARD_AZURE_MONITOR_ATTRIBUTES = [
    _SAMPLE_RATE_KEY,
]


class AzureMonitorTraceExporter(BaseExporter, SpanExporter):
    """Azure Monitor Trace exporter for OpenTelemetry."""

    def __init__(self, **kwargs: Any):
        self._tracer_provider = kwargs.pop("tracer_provider", None)
        super().__init__(**kwargs)

    def export(
        self, spans: Sequence[ReadableSpan], **kwargs: Any  # pylint: disable=unused-argument
    ) -> SpanExportResult:
        """Export span data.

        :param spans: Open Telemetry Spans to export.
        :type spans: ~typing.Sequence[~opentelemetry.trace.Span]
        :return: The result of the export.
        :rtype: ~opentelemetry.sdk.trace.export.SpanExportResult
        """
        envelopes = []
        if spans and self._should_collect_otel_resource_metric():
            resource = None
            try:
                tracer_provider = self._tracer_provider or get_tracer_provider()
                resource = tracer_provider.resource  # type: ignore
                envelopes.append(self._get_otel_resource_envelope(resource))
            except AttributeError as e:
                _logger.exception("Failed to derive Resource from Tracer Provider: %s", e)
        for span in spans:
            envelopes.append(self._span_to_envelope(span))
            envelopes.extend(self._span_events_to_envelopes(span))
        try:
            result = self._transmit(envelopes)
            self._handle_transmit_from_storage(envelopes, result)
            return _get_trace_export_result(result)
        except Exception:  # pylint: disable=broad-except
            _logger.exception("Exception occurred while exporting the data.")
            return _get_trace_export_result(ExportResult.FAILED_NOT_RETRYABLE)

    def shutdown(self) -> None:
        """Shuts down the exporter.

        Called when the SDK is shut down.
        """
        if self.storage:
            self.storage.close()

    # pylint: disable=protected-access
    def _get_otel_resource_envelope(self, resource: Resource) -> TelemetryItem:
        attributes: Dict[str, str] = {}
        if resource:
            attributes = resource.attributes
        envelope = _utils._create_telemetry_item(time_ns())
        envelope.name = _METRIC_ENVELOPE_NAME
        envelope.tags.update(_utils._populate_part_a_fields(resource))  # pylint: disable=W0212
        envelope.instrumentation_key = self._instrumentation_key
        data_point = MetricDataPoint(
            name=str("_OTELRESOURCE_")[:1024],
            value=0,
        )

        data = MetricsData(
            properties=attributes,
            metrics=[data_point],
        )

        envelope.data = MonitorBase(base_data=data, base_type="MetricData")

        return envelope

    def _span_to_envelope(self, span: ReadableSpan) -> TelemetryItem:
        envelope = _convert_span_to_envelope(span)
        envelope.instrumentation_key = self._instrumentation_key
        return envelope

    def _span_events_to_envelopes(self, span: ReadableSpan) -> Sequence[TelemetryItem]:
        if not span or len(span.events) == 0:
            return []
        envelopes = _convert_span_events_to_envelopes(span)
        for envelope in envelopes:
            envelope.instrumentation_key = self._instrumentation_key
        return envelopes

    def _should_collect_otel_resource_metric(self):
        disabled = environ.get(_APPLICATIONINSIGHTS_OPENTELEMETRY_RESOURCE_METRIC_DISABLED)
        return disabled is None or disabled.lower() != "true"

    # pylint: disable=docstring-keyword-should-match-keyword-only
    @classmethod
    def from_connection_string(cls, conn_str: str, **kwargs: Any) -> "AzureMonitorTraceExporter":
        """
        Create an AzureMonitorTraceExporter from a connection string. This is
        the recommended way of instantiation if a connection string is passed in
        explicitly. If a user wants to use a connection string provided by
        environment variable, the constructor of the exporter can be called
        directly.

        :param str conn_str: The connection string to be used for
            authentication.
        :keyword str api_version: The service API version used. Defaults to
            latest.
        :return: an instance of ~AzureMonitorTraceExporter
        :rtype: ~azure.monitor.opentelemetry.exporter.AzureMonitorTraceExporter
        """
        return cls(connection_string=conn_str, **kwargs)


# pylint: disable=too-many-statements
# pylint: disable=too-many-branches
# pylint: disable=too-many-locals
# pylint: disable=protected-access
# mypy: disable-error-code="assignment,attr-defined,index,operator,union-attr"
def _convert_span_to_envelope(span: ReadableSpan) -> TelemetryItem:
    # Update instrumentation bitmap if span was generated from instrumentation
    _check_instrumentation_span(span)
    duration = 0
    start_time = 0
    if span.start_time:
        start_time = span.start_time
        if span.end_time:
            duration = span.end_time - span.start_time
    envelope = _utils._create_telemetry_item(start_time)
    envelope.tags.update(_utils._populate_part_a_fields(span.resource))
    envelope.tags[ContextTagKeys.AI_OPERATION_ID] = "{:032x}".format(span.context.trace_id)
    if SpanAttributes.ENDUSER_ID in span.attributes:
        envelope.tags[ContextTagKeys.AI_USER_ID] = span.attributes[SpanAttributes.ENDUSER_ID]
    if span.parent and span.parent.span_id:
        envelope.tags[ContextTagKeys.AI_OPERATION_PARENT_ID] = "{:016x}".format(span.parent.span_id)
    # pylint: disable=too-many-nested-blocks
    if span.kind in (SpanKind.CONSUMER, SpanKind.SERVER):
        envelope.name = _REQUEST_ENVELOPE_NAME
        data = RequestData(
            name=span.name,
            id="{:016x}".format(span.context.span_id),
            duration=_utils.ns_to_duration(duration),
            response_code="0",
            success=span.status.is_ok,
            properties={},
            measurements={},
        )
        envelope.data = MonitorBase(base_data=data, base_type="RequestData")
        envelope.tags[ContextTagKeys.AI_OPERATION_NAME] = span.name
        if SpanAttributes.NET_PEER_IP in span.attributes:
            envelope.tags[ContextTagKeys.AI_LOCATION_IP] = span.attributes[SpanAttributes.NET_PEER_IP]
        if _AZURE_SDK_NAMESPACE_NAME in span.attributes:  # Azure specific resources
            # Currently only eventhub and servicebus are supported (kind CONSUMER)
            data.source = trace_utils._get_azure_sdk_target_source(span.attributes)
            if span.links:
                total = 0
                for link in span.links:
                    attributes = link.attributes
                    enqueued_time = attributes.get("enqueuedTime")
                    if isinstance(enqueued_time, int):
                        difference = (start_time / 1000000) - enqueued_time
                        total += difference
                data.measurements["timeSinceEnqueued"] = max(0, total / len(span.links))
        elif SpanAttributes.HTTP_METHOD in span.attributes:  # HTTP
            url = ""
            path = ""
            if SpanAttributes.HTTP_USER_AGENT in span.attributes:
                # TODO: Not exposed in Swagger, need to update def
                envelope.tags["ai.user.userAgent"] = span.attributes[SpanAttributes.HTTP_USER_AGENT]
            # http specific logic for ai.location.ip
            if SpanAttributes.HTTP_CLIENT_IP in span.attributes:
                envelope.tags[ContextTagKeys.AI_LOCATION_IP] = span.attributes[SpanAttributes.HTTP_CLIENT_IP]
            # url
            if SpanAttributes.HTTP_URL in span.attributes:
                url = span.attributes[SpanAttributes.HTTP_URL]
            elif SpanAttributes.HTTP_SCHEME in span.attributes and SpanAttributes.HTTP_TARGET in span.attributes:
                scheme = span.attributes[SpanAttributes.HTTP_SCHEME]
                http_target = span.attributes[SpanAttributes.HTTP_TARGET]
                if SpanAttributes.HTTP_HOST in span.attributes:
                    url = "{}://{}{}".format(
                        scheme,
                        span.attributes[SpanAttributes.HTTP_HOST],
                        http_target,
                    )
                elif SpanAttributes.NET_HOST_PORT in span.attributes:
                    host_port = span.attributes[SpanAttributes.NET_HOST_PORT]
                    if SpanAttributes.HTTP_SERVER_NAME in span.attributes:
                        server_name = span.attributes[SpanAttributes.HTTP_SERVER_NAME]
                        url = "{}://{}:{}{}".format(
                            scheme,
                            server_name,
                            host_port,
                            http_target,
                        )
                    elif SpanAttributes.NET_HOST_NAME in span.attributes:
                        host_name = span.attributes[SpanAttributes.NET_HOST_NAME]
                        url = "{}://{}:{}{}".format(
                            scheme,
                            host_name,
                            host_port,
                            http_target,
                        )
            data.url = url
            # Http specific logic for ai.operation.name
            if SpanAttributes.HTTP_ROUTE in span.attributes:
                envelope.tags[ContextTagKeys.AI_OPERATION_NAME] = "{} {}".format(
                    span.attributes[SpanAttributes.HTTP_METHOD],
                    span.attributes[SpanAttributes.HTTP_ROUTE],
                )
            elif url:
                try:
                    parse_url = urlparse(url)
                    path = parse_url.path
                    if not path:
                        path = "/"
                    envelope.tags[ContextTagKeys.AI_OPERATION_NAME] = "{} {}".format(
                        span.attributes[SpanAttributes.HTTP_METHOD],
                        path,
                    )
                except Exception:  # pylint: disable=broad-except
                    pass
            status_code = span.attributes.get(SpanAttributes.HTTP_STATUS_CODE)
            if status_code:
                try:
                    status_code = int(status_code)  # type: ignore
                except ValueError:
                    status_code = 0
            else:
                status_code = 0
            data.response_code = str(status_code)
            # Success criteria for server spans depends on span.success and the actual status code
            data.success = span.status.is_ok and status_code and status_code not in range(400, 500)
        elif SpanAttributes.MESSAGING_SYSTEM in span.attributes:  # Messaging
            if SpanAttributes.NET_PEER_IP in span.attributes:
                envelope.tags[ContextTagKeys.AI_LOCATION_IP] = span.attributes[SpanAttributes.NET_PEER_IP]
            if span.attributes.get(SpanAttributes.MESSAGING_DESTINATION):
                if span.attributes.get(SpanAttributes.NET_PEER_NAME):
                    data.source = "{}/{}".format(
                        span.attributes.get(SpanAttributes.NET_PEER_NAME),
                        span.attributes.get(SpanAttributes.MESSAGING_DESTINATION),
                    )
                elif span.attributes.get(SpanAttributes.NET_PEER_IP):
                    data.source = "{}/{}".format(
                        span.attributes[SpanAttributes.NET_PEER_IP],
                        span.attributes.get(SpanAttributes.MESSAGING_DESTINATION),
                    )
                else:
                    data.source = span.attributes.get(SpanAttributes.MESSAGING_DESTINATION, "")
        # Apply truncation
        # See https://github.com/MohanGsk/ApplicationInsights-Home/tree/master/EndpointSpecs/Schemas/Bond
        if envelope.tags.get(ContextTagKeys.AI_OPERATION_NAME):
            data.name = envelope.tags[ContextTagKeys.AI_OPERATION_NAME][:1024]
        if data.response_code:
            data.response_code = data.response_code[:1024]
        if data.source:
            data.source = data.source[:1024]
        if data.url:
            data.url = data.url[:2048]
    else:  # INTERNAL, CLIENT, PRODUCER
        envelope.name = _REMOTE_DEPENDENCY_ENVELOPE_NAME
        # TODO: ai.operation.name for non-server spans
        time = 0
        if span.end_time and span.start_time:
            time = span.end_time - span.start_time
        data = RemoteDependencyData(  # type: ignore
            name=span.name,
            id="{:016x}".format(span.context.span_id),
            result_code="0",
            duration=_utils.ns_to_duration(time),
            success=span.status.is_ok,  # Success depends only on span status
            properties={},
        )
        envelope.data = MonitorBase(base_data=data, base_type="RemoteDependencyData")
        target = trace_utils._get_target_for_dependency_from_peer(span.attributes)
        if span.kind is SpanKind.CLIENT:
            if _AZURE_SDK_NAMESPACE_NAME in span.attributes:  # Azure specific resources
                # Currently only eventhub and servicebus are supported
                # https://github.com/Azure/azure-sdk-for-python/issues/9256
                data.type = span.attributes[_AZURE_SDK_NAMESPACE_NAME]
                data.target = trace_utils._get_azure_sdk_target_source(span.attributes)
            elif SpanAttributes.HTTP_METHOD in span.attributes:  # HTTP
                data.type = "HTTP"
                if SpanAttributes.HTTP_USER_AGENT in span.attributes:
                    # TODO: Not exposed in Swagger, need to update def
                    envelope.tags["ai.user.userAgent"] = span.attributes[SpanAttributes.HTTP_USER_AGENT]
                url = trace_utils._get_url_for_http_dependency(span.attributes)
                # data
                if url:
                    data.data = url
                target, path = trace_utils._get_target_and_path_for_http_dependency(
                    span.attributes,
                    target,  # type: ignore
                    url,
                )
                # http specific logic for name
                if path:
                    data.name = "{} {}".format(
                        span.attributes[SpanAttributes.HTTP_METHOD],
                        path,
                    )
                status_code = span.attributes.get(SpanAttributes.HTTP_STATUS_CODE)
                if status_code:
                    try:
                        status_code = int(status_code)  # type: ignore
                    except ValueError:
                        status_code = 0
                else:
                    status_code = 0
                data.result_code = str(status_code)
            elif SpanAttributes.DB_SYSTEM in span.attributes:  # Database
                db_system = span.attributes[SpanAttributes.DB_SYSTEM]
                if db_system == DbSystemValues.MYSQL.value:
                    data.type = "mysql"
                elif db_system == DbSystemValues.POSTGRESQL.value:
                    data.type = "postgresql"
                elif db_system == DbSystemValues.MONGODB.value:
                    data.type = "mongodb"
                elif db_system == DbSystemValues.REDIS.value:
                    data.type = "redis"
                elif trace_utils._is_sql_db(str(db_system)):
                    data.type = "SQL"
                else:
                    data.type = db_system
                # data is the full statement or operation
                if SpanAttributes.DB_STATEMENT in span.attributes:
                    data.data = span.attributes[SpanAttributes.DB_STATEMENT]
                elif SpanAttributes.DB_OPERATION in span.attributes:
                    data.data = span.attributes[SpanAttributes.DB_OPERATION]
                # db specific logic for target
                target = trace_utils._get_target_for_db_dependency(
                    target,  # type: ignore
                    db_system,  # type: ignore
                    span.attributes,
                )
            elif SpanAttributes.MESSAGING_SYSTEM in span.attributes:  # Messaging
                data.type = span.attributes[SpanAttributes.MESSAGING_SYSTEM]
                target = trace_utils._get_target_for_messaging_dependency(
                    target,  # type: ignore
                    span.attributes,
                )
            elif SpanAttributes.RPC_SYSTEM in span.attributes:  # Rpc
                data.type = SpanAttributes.RPC_SYSTEM
                target = trace_utils._get_target_for_rpc_dependency(
                    target,  # type: ignore
                    span.attributes,
                )
            elif gen_ai_attributes.GEN_AI_SYSTEM in span.attributes:  # GenAI
                data.type = span.attributes[gen_ai_attributes.GEN_AI_SYSTEM]
            else:
                data.type = "N/A"
        elif span.kind is SpanKind.PRODUCER:  # Messaging
            # Currently only eventhub and servicebus are supported that produce PRODUCER spans
            if _AZURE_SDK_NAMESPACE_NAME in span.attributes:
                data.type = "Queue Message | {}".format(span.attributes[_AZURE_SDK_NAMESPACE_NAME])
                target = trace_utils._get_azure_sdk_target_source(span.attributes)
            else:
                data.type = "Queue Message"
                msg_system = span.attributes.get(SpanAttributes.MESSAGING_SYSTEM)
                if msg_system:
                    data.type += " | {}".format(msg_system)
                target = trace_utils._get_target_for_messaging_dependency(
                    target,  # type: ignore
                    span.attributes,
                )
        else:  # SpanKind.INTERNAL
            data.type = "InProc"
            if _AZURE_SDK_NAMESPACE_NAME in span.attributes:
                data.type += " | {}".format(span.attributes[_AZURE_SDK_NAMESPACE_NAME])
        # Apply truncation
        # See https://github.com/MohanGsk/ApplicationInsights-Home/tree/master/EndpointSpecs/Schemas/Bond
        if data.name:
            data.name = str(data.name)[:1024]
        if data.result_code:
            data.result_code = str(data.result_code)[:1024]
        if data.data:
            data.data = str(data.data)[:8192]
        if data.type:
            data.type = str(data.type)[:1024]
        if target:
            data.target = str(target)[:1024]

    # sampleRate
    if _SAMPLE_RATE_KEY in span.attributes:
        envelope.sample_rate = span.attributes[_SAMPLE_RATE_KEY]

    data.properties = _utils._filter_custom_properties(
        span.attributes, lambda key, val: not _is_standard_attribute(key)
    )

    # Standard metrics special properties
    # Only add the property if span was generated from instrumentation that supports metrics collection
    if (
        span.instrumentation_scope is not None
        and span.instrumentation_scope.name in _INSTRUMENTATION_SUPPORTING_METRICS_LIST
    ):
        data.properties["_MS.ProcessedByMetricExtractors"] = "True"

    if span.links:
        # Max length for value is 8192
        # Since links are a fixed length (80) in json, max number of links would be 102
        links: List[Dict[str, str]] = []
        for link in span.links:
            if len(links) > 102:
                break
            operation_id = "{:032x}".format(link.context.trace_id)
            span_id = "{:016x}".format(link.context.span_id)
            links.append({"operation_Id": operation_id, "id": span_id})
        data.properties["_MS.links"] = json.dumps(links)
    return envelope


# pylint: disable=protected-access
def _convert_span_events_to_envelopes(span: ReadableSpan) -> Sequence[TelemetryItem]:
    envelopes = []
    for event in span.events:
        envelope = _utils._create_telemetry_item(event.timestamp)
        envelope.tags.update(_utils._populate_part_a_fields(span.resource))
        envelope.tags[ContextTagKeys.AI_OPERATION_ID] = "{:032x}".format(span.context.trace_id)
        if span.context and span.context.span_id:
            envelope.tags[ContextTagKeys.AI_OPERATION_PARENT_ID] = "{:016x}".format(span.context.span_id)

        # sampleRate
        if span.attributes and _SAMPLE_RATE_KEY in span.attributes:
            envelope.sample_rate = span.attributes[_SAMPLE_RATE_KEY]

        properties = _utils._filter_custom_properties(
            event.attributes, lambda key, val: not _is_standard_attribute(key)
        )
        if event.name == "exception":
            envelope.name = _EXCEPTION_ENVELOPE_NAME
            exc_type = exc_message = stack_trace = None
            if event.attributes:
                exc_type = event.attributes.get(SpanAttributes.EXCEPTION_TYPE)
                exc_message = event.attributes.get(SpanAttributes.EXCEPTION_MESSAGE)
                stack_trace = event.attributes.get(SpanAttributes.EXCEPTION_STACKTRACE)
            if not exc_type:
                exc_type = "Exception"
            if not exc_message:
                exc_message = "Exception"
            has_full_stack = stack_trace is not None
            exc_details = TelemetryExceptionDetails(
                type_name=str(exc_type)[:1024],
                message=str(exc_message)[:32768],
                has_full_stack=has_full_stack,
                stack=str(stack_trace)[:32768],
            )
            data = TelemetryExceptionData(
                properties=properties,
                exceptions=[exc_details],
            )
            # pylint: disable=line-too-long
            envelope.data = MonitorBase(base_data=data, base_type="ExceptionData")
        else:
            envelope.name = _MESSAGE_ENVELOPE_NAME
            data = MessageData(  # type: ignore
                message=str(event.name)[:32768],
                properties=properties,
            )
            envelope.data = MonitorBase(base_data=data, base_type="MessageData")

        envelopes.append(envelope)

    return envelopes


def _check_instrumentation_span(span: ReadableSpan) -> None:
    # Special use-case for spans generated from azure-sdk services
    # Identified by having az.namespace as a span attribute
    if span.attributes and _AZURE_SDK_NAMESPACE_NAME in span.attributes:
        _utils.add_instrumentation(_AZURE_SDK_OPENTELEMETRY_NAME)
        return
    if span.instrumentation_scope is None:
        return
    # All instrumentation scope names from OpenTelemetry instrumentations have
    # `opentelemetry.instrumentation.` as a prefix
    if span.instrumentation_scope.name.startswith("opentelemetry.instrumentation."):
        # The string after the prefix is the name of the instrumentation
        name = span.instrumentation_scope.name.split("opentelemetry.instrumentation.", 1)[1]
        # Update the bit map to indicate instrumentation is being used
        _utils.add_instrumentation(name)


def _is_standard_attribute(key: str) -> bool:
    for prefix in _STANDARD_OPENTELEMETRY_ATTRIBUTE_PREFIXES:
        if key.startswith(prefix):
            return True
    return key in _STANDARD_AZURE_MONITOR_ATTRIBUTES


def _get_trace_export_result(result: ExportResult) -> SpanExportResult:
    if result == ExportResult.SUCCESS:
        return SpanExportResult.SUCCESS
    return SpanExportResult.FAILURE
