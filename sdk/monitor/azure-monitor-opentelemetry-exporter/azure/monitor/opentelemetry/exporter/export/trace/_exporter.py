# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import json
import logging
from typing import Optional, Sequence, Any
from urllib.parse import urlparse

from opentelemetry.util.types import Attributes
from opentelemetry.semconv.trace import DbSystemValues, SpanAttributes
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from opentelemetry.trace import SpanKind

from azure.monitor.opentelemetry.exporter._constants import _SAMPLE_RATE_KEY
from azure.monitor.opentelemetry.exporter import _utils
from azure.monitor.opentelemetry.exporter._generated.models import (
    MessageData,
    MonitorBase,
    RemoteDependencyData,
    RequestData,
    TelemetryExceptionData,
    TelemetryExceptionDetails,
    TelemetryItem
)
from azure.monitor.opentelemetry.exporter.export._base import (
    BaseExporter,
    ExportResult,
)

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

    def export(self, spans: Sequence[ReadableSpan], **kwargs: Any) -> SpanExportResult: # pylint: disable=unused-argument
        """Export span data
        :param spans: Open Telemetry Spans to export.
        :type spans: Sequence[~opentelemetry.trace.Span]
        :rtype: ~opentelemetry.sdk.trace.export.SpanExportResult
        """
        envelopes = []
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
        self.storage.close()

    def _span_to_envelope(self, span: ReadableSpan) -> TelemetryItem:
        if not span:
            return None
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

    @classmethod
    def from_connection_string(cls, conn_str: str, **kwargs: Any) -> "AzureMonitorTraceExporter":
        """
        Create an AzureMonitorTraceExporter from a connection string.

        This is the recommended way of instantation if a connection string is passed in explicitly.
        If a user wants to use a connection string provided by environment variable, the constructor
        of the exporter can be called directly.

        :param str conn_str: The connection string to be used for authentication.
        :keyword str api_version: The service API version used. Defaults to latest.
        :returns an instance of ~AzureMonitorTraceExporter
        """
        return cls(connection_string=conn_str, **kwargs)

# pylint: disable=too-many-statements
# pylint: disable=too-many-branches
# pylint: disable=too-many-locals
# pylint: disable=protected-access
def _convert_span_to_envelope(span: ReadableSpan) -> TelemetryItem:
    # Update instrumentation bitmap if span was generated from instrumentation
    _check_instrumentation_span(span)
    envelope = _utils._create_telemetry_item(span.start_time)
    envelope.tags.update(_utils._populate_part_a_fields(span.resource))
    envelope.tags["ai.operation.id"] = "{:032x}".format(span.context.trace_id)
    if SpanAttributes.ENDUSER_ID in span.attributes:
        envelope.tags["ai.user.id"] = span.attributes[SpanAttributes.ENDUSER_ID]
    if span.parent and span.parent.span_id:
        envelope.tags["ai.operation.parentId"] = "{:016x}".format(
            span.parent.span_id
        )
    # pylint: disable=too-many-nested-blocks
    if span.kind in (SpanKind.CONSUMER, SpanKind.SERVER):
        envelope.name = "Microsoft.ApplicationInsights.Request"
        data = RequestData(
            name=span.name,
            id="{:016x}".format(span.context.span_id),
            duration=_utils.ns_to_duration(span.end_time - span.start_time),
            response_code="0",
            success=span.status.is_ok,
            properties={},
            measurements={},
        )
        envelope.data = MonitorBase(base_data=data, base_type="RequestData")
        envelope.tags["ai.operation.name"] = span.name
        if SpanAttributes.NET_PEER_IP in span.attributes:
            envelope.tags["ai.location.ip"] = span.attributes[SpanAttributes.NET_PEER_IP]
        if "az.namespace" in span.attributes:  # Azure specific resources
            # Currently only eventhub and servicebus are supported (kind CONSUMER)
            data.source = _get_azure_sdk_target_source(span.attributes)
            if span.links:
                total = 0
                for link in span.links:
                    attributes = link.attributes
                    enqueued_time  = attributes.get("enqueuedTime")
                    if enqueued_time:
                        difference = (span.start_time / 1000000) - int(enqueued_time)
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
                envelope.tags["ai.location.ip"] = span.attributes[SpanAttributes.HTTP_CLIENT_IP]
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
                envelope.tags["ai.operation.name"] = "{} {}".format(
                    span.attributes[SpanAttributes.HTTP_METHOD],
                    span.attributes[SpanAttributes.HTTP_ROUTE],
                )
            elif url:
                try:
                    parse_url = urlparse(url)
                    path = parse_url.path
                    if not path:
                        path = "/"
                    envelope.tags["ai.operation.name"] = "{} {}".format(
                        span.attributes[SpanAttributes.HTTP_METHOD],
                        path,
                    )
                except Exception:  # pylint: disable=broad-except
                    pass
            if SpanAttributes.HTTP_STATUS_CODE in span.attributes:
                status_code = span.attributes[SpanAttributes.HTTP_STATUS_CODE]
                data.response_code = str(status_code)
        elif SpanAttributes.MESSAGING_SYSTEM in span.attributes:  # Messaging
            if SpanAttributes.NET_PEER_IP in span.attributes:
                envelope.tags["ai.location.ip"] = span.attributes[SpanAttributes.NET_PEER_IP]
            if SpanAttributes.MESSAGING_DESTINATION in span.attributes:
                if SpanAttributes.NET_PEER_NAME in span.attributes:
                    data.source = "{}/{}".format(
                        span.attributes[SpanAttributes.NET_PEER_NAME],
                        span.attributes[SpanAttributes.MESSAGING_DESTINATION],
                    )
                elif SpanAttributes.NET_PEER_IP in span.attributes:
                    data.source = "{}/{}".format(
                        span.attributes[SpanAttributes.NET_PEER_IP],
                        span.attributes[SpanAttributes.MESSAGING_DESTINATION],
                    )
                else:
                    data.source = span.attributes[SpanAttributes.MESSAGING_DESTINATION]
        # Apply truncation
        # See https://github.com/MohanGsk/ApplicationInsights-Home/tree/master/EndpointSpecs/Schemas/Bond
        if envelope.tags.get("ai.operation.name"):
            data.name = envelope.tags["ai.operation.name"][:1024]
        if data.response_code:
            data.response_code = data.response_code[:1024]
        if data.source:
            data.source = data.source[:1024]
        if data.url:
            data.url = data.url[:2048]
    else:  # INTERNAL, CLIENT, PRODUCER
        envelope.name = "Microsoft.ApplicationInsights.RemoteDependency"
        # TODO: ai.operation.name for non-server spans
        data = RemoteDependencyData(
            name=span.name,
            id="{:016x}".format(span.context.span_id),
            result_code="0",
            duration=_utils.ns_to_duration(span.end_time - span.start_time),
            success=span.status.is_ok,
            properties={},
        )
        envelope.data = MonitorBase(
            base_data=data, base_type="RemoteDependencyData"
        )
        target = None
        if SpanAttributes.PEER_SERVICE in span.attributes:
            target = span.attributes[SpanAttributes.PEER_SERVICE]
        else:
            if SpanAttributes.NET_PEER_NAME in span.attributes:
                target = span.attributes[SpanAttributes.NET_PEER_NAME]
            elif SpanAttributes.NET_PEER_IP in span.attributes:
                target = span.attributes[SpanAttributes.NET_PEER_IP]
            if SpanAttributes.NET_PEER_PORT in span.attributes:
                port = span.attributes[SpanAttributes.NET_PEER_PORT]
                # TODO: check default port for rpc
                # This logic assumes default ports never conflict across dependency types
                if port != _get_default_port_http(span.attributes.get(SpanAttributes.HTTP_SCHEME)) and \
                    port != _get_default_port_db(span.attributes.get(SpanAttributes.DB_SYSTEM)):
                    target = "{}:{}".format(target, port)
        if span.kind is SpanKind.CLIENT:
            if "az.namespace" in span.attributes:  # Azure specific resources
                # Currently only eventhub and servicebus are supported
                # https://github.com/Azure/azure-sdk-for-python/issues/9256
                data.type = span.attributes["az.namespace"]
                data.target = _get_azure_sdk_target_source(span.attributes)
            elif SpanAttributes.HTTP_METHOD in span.attributes:  # HTTP
                data.type = "HTTP"
                if SpanAttributes.HTTP_USER_AGENT in span.attributes:
                    # TODO: Not exposed in Swagger, need to update def
                    envelope.tags["ai.user.userAgent"] = span.attributes[SpanAttributes.HTTP_USER_AGENT]
                scheme = span.attributes.get(SpanAttributes.HTTP_SCHEME)
                # url
                url = ""
                if SpanAttributes.HTTP_URL in span.attributes:
                    url = span.attributes[SpanAttributes.HTTP_URL]
                elif scheme and SpanAttributes.HTTP_TARGET in span.attributes:
                    http_target = span.attributes[SpanAttributes.HTTP_TARGET]
                    if SpanAttributes.HTTP_HOST in span.attributes:
                        url = "{}://{}{}".format(
                            scheme,
                            span.attributes[SpanAttributes.HTTP_HOST],
                            http_target,
                        )
                    elif SpanAttributes.NET_PEER_PORT in span.attributes:
                        peer_port = span.attributes[SpanAttributes.NET_PEER_PORT]
                        if SpanAttributes.NET_PEER_NAME in span.attributes:
                            peer_name = span.attributes[SpanAttributes.NET_PEER_NAME]
                            url = "{}://{}:{}{}".format(
                                scheme,
                                peer_name,
                                peer_port,
                                http_target,
                            )
                        elif SpanAttributes.NET_PEER_IP in span.attributes:
                            peer_ip = span.attributes[SpanAttributes.NET_PEER_IP]
                            url = "{}://{}:{}{}".format(
                                scheme,
                                peer_ip,
                                peer_port,
                                http_target,
                            )
                target_from_url = ""
                path = ""
                if url:
                    try:
                        parse_url = urlparse(url)
                        path = parse_url.path
                        if not path:
                            path = "/"
                        if parse_url.port == _get_default_port_http(scheme):
                            target_from_url = parse_url.hostname
                        else:
                            target_from_url = parse_url.netloc
                    except Exception:  # pylint: disable=broad-except
                        pass
                # http specific logic for name
                if path:
                    data.name = "{} {}".format(
                        span.attributes[SpanAttributes.HTTP_METHOD],
                        path,
                    )
                # http specific logic for target
                if SpanAttributes.PEER_SERVICE not in span.attributes:
                    if SpanAttributes.HTTP_HOST in span.attributes:
                        host = span.attributes[SpanAttributes.HTTP_HOST]
                        try:
                            # urlparse insists on absolute URLs starting with "//"
                            # This logic assumes host does not include a "//"
                            host_name = urlparse("//" + host)
                            if host_name.port == _get_default_port_http(scheme):
                                target = host_name.hostname
                            else:
                                target = host
                        except Exception:  # pylint: disable=broad-except
                            _logger.warning("Error while parsing hostname.")
                    elif target_from_url:
                        target = target_from_url
                # data is url
                data.data = url
                if SpanAttributes.HTTP_STATUS_CODE in span.attributes:
                    status_code = span.attributes[SpanAttributes.HTTP_STATUS_CODE]
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
                elif _is_sql_db(db_system):
                    data.type = "SQL"
                else:
                    data.type = db_system
                # data is the full statement or operation
                if SpanAttributes.DB_STATEMENT in span.attributes:
                    data.data = span.attributes[SpanAttributes.DB_STATEMENT]
                elif SpanAttributes.DB_OPERATION in span.attributes:
                    data.data = span.attributes[SpanAttributes.DB_OPERATION]
                # db specific logic for target
                if SpanAttributes.DB_NAME in span.attributes:
                    db_name = span.attributes[SpanAttributes.DB_NAME]
                    if target is None:
                        target = db_name
                    else:
                        target = "{}|{}".format(target, db_name)
                if target is None:
                    target = db_system
            elif SpanAttributes.MESSAGING_SYSTEM in span.attributes:  # Messaging
                data.type = span.attributes[SpanAttributes.MESSAGING_SYSTEM]
                if target is None:
                    if SpanAttributes.MESSAGING_DESTINATION in span.attributes:
                        target = span.attributes[SpanAttributes.MESSAGING_DESTINATION]
                    else:
                        target = span.attributes[SpanAttributes.MESSAGING_SYSTEM]
            elif SpanAttributes.RPC_SYSTEM in span.attributes:  # Rpc
                data.type = SpanAttributes.RPC_SYSTEM
                if target is None:
                    target = span.attributes[SpanAttributes.RPC_SYSTEM]
            else:
                data.type = "N/A"
        elif span.kind is SpanKind.PRODUCER:  # Messaging
            # Currently only eventhub and servicebus are supported that produce PRODUCER spans
            if "az.namespace" in span.attributes:
                data.type = "Queue Message | {}".format(span.attributes["az.namespace"])
                data.target = _get_azure_sdk_target_source(span.attributes)
            else:
                data.type = "Queue Message"
                msg_system = span.attributes.get(SpanAttributes.MESSAGING_SYSTEM)
                if msg_system:
                    data.type += " | {}".format(msg_system)
                if target is None:
                    if SpanAttributes.MESSAGING_DESTINATION in span.attributes:
                        target = span.attributes[SpanAttributes.MESSAGING_DESTINATION]
                    else:
                        target = msg_system
        else:  # SpanKind.INTERNAL
            data.type = "InProc"
            if "az.namespace" in span.attributes:
                data.type += " | {}".format(span.attributes["az.namespace"])
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
        span.attributes,
        lambda key, val: not _is_standard_attribute(key)
    )
    if span.links:
        # Max length for value is 8192
        # Since links are a fixed length (80) in json, max number of links would be 102
        links = []
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
        envelope.tags["ai.operation.id"] = "{:032x}".format(span.context.trace_id)
        if span.context and span.context.span_id:
            envelope.tags["ai.operation.parentId"] = "{:016x}".format(
                span.context.span_id
            )
        properties = _utils._filter_custom_properties(
            event.attributes,
            lambda key, val: not _is_standard_attribute(key)
        )
        if event.name == "exception":
            envelope.name = 'Microsoft.ApplicationInsights.Exception'
            exc_type = event.attributes.get(SpanAttributes.EXCEPTION_TYPE)
            exc_message = event.attributes.get(SpanAttributes.EXCEPTION_MESSAGE)
            if exc_message is None or not exc_message:
                exc_message = "Exception"
            stack_trace = event.attributes.get(SpanAttributes.EXCEPTION_STACKTRACE)
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
            envelope.data = MonitorBase(base_data=data, base_type='ExceptionData')
        else:
            envelope.name = 'Microsoft.ApplicationInsights.Message'
            data = MessageData(
                message=str(event.name)[:32768],
                properties=properties,
            )
            envelope.data = MonitorBase(base_data=data, base_type='MessageData')

        envelopes.append(envelope)

    return envelopes

# pylint:disable=too-many-return-statements
def _get_default_port_db(db_system: str) -> int:
    if db_system == DbSystemValues.POSTGRESQL.value:
        return 5432
    if db_system == DbSystemValues.CASSANDRA.value:
        return 9042
    if db_system in (DbSystemValues.MARIADB.value, DbSystemValues.MYSQL.value):
        return 3306
    if db_system == DbSystemValues.MSSQL.value:
        return 1433
    # TODO: Add in memcached
    if db_system == "memcached":
        return 11211
    if db_system == DbSystemValues.DB2.value:
        return 50000
    if db_system == DbSystemValues.ORACLE.value:
        return 1521
    if db_system == DbSystemValues.H2.value:
        return 8082
    if db_system == DbSystemValues.DERBY.value:
        return 1527
    if db_system == DbSystemValues.REDIS.value:
        return 6379
    return 0


def _get_default_port_http(scheme: str) -> int:
    if scheme == "http":
        return 80
    if scheme == "https":
        return 443
    return 0


def _is_sql_db(db_system: str) -> bool:
    return db_system in (
        DbSystemValues.DB2.value,
        DbSystemValues.DERBY.value,
        DbSystemValues.MARIADB.value,
        DbSystemValues.MSSQL.value,
        DbSystemValues.ORACLE.value,
        DbSystemValues.SQLITE.value,
        DbSystemValues.OTHER_SQL.value,
        # spell-checker:ignore HSQLDB
        DbSystemValues.HSQLDB.value,
        DbSystemValues.H2.value,
      )


def _check_instrumentation_span(span: ReadableSpan) -> None:
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


def _get_azure_sdk_target_source(attributes: Attributes) -> Optional[str]:
    # Currently logic only works for ServiceBus and EventHub
    peer_address = attributes.get("peer.address")
    destination = attributes.get("message_bus.destination")
    if peer_address and destination:
        return peer_address + "/" + destination


def _get_trace_export_result(result: ExportResult) -> SpanExportResult:
    if result == ExportResult.SUCCESS:
        return SpanExportResult.SUCCESS
    if result in (
        ExportResult.FAILED_RETRYABLE,
        ExportResult.FAILED_NOT_RETRYABLE,
    ):
        return SpanExportResult.FAILURE
    return None
