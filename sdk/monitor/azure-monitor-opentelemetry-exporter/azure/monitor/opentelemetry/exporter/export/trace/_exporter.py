# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import json
import logging
import platform
from typing import Sequence, Any
from urllib.parse import urlparse

from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from opentelemetry.sdk.util import ns_to_iso_str
from opentelemetry.trace import Span, SpanKind

from azure.monitor.opentelemetry.exporter import _utils
from azure.monitor.opentelemetry.exporter._generated.models import (
    MonitorBase,
    RemoteDependencyData,
    RequestData,
    TelemetryItem
)
from azure.monitor.opentelemetry.exporter.export._base import (
    BaseExporter,
    ExportResult,
    get_trace_export_result,
)

logger = logging.getLogger(__name__)

__all__ = ["AzureMonitorTraceExporter"]


class AzureMonitorTraceExporter(BaseExporter, SpanExporter):
    """Azure Monitor base exporter for OpenTelemetry."""

    def export(self, spans: Sequence[Span], **kwargs: Any) -> SpanExportResult: # pylint: disable=unused-argument
        """Export data
        :param spans: Open Telemetry Spans to export.
        :type spans: Sequence[~opentelemetry.trace.Span]
        :rtype: ~opentelemetry.sdk.trace.export.SpanExportResult
        """
        envelopes = [self._span_to_envelope(span) for span in spans]
        try:
            result = self._transmit(envelopes)
            if result == ExportResult.FAILED_RETRYABLE:
                envelopes_to_store = [x.as_dict() for x in envelopes]
                self.storage.put(envelopes_to_store, 1)
            if result == ExportResult.SUCCESS:
                # Try to send any cached events
                self._transmit_from_storage()
            return get_trace_export_result(result)
        except Exception:  # pylint: disable=broad-except
            logger.exception("Exception occurred while exporting the data.")
            return get_trace_export_result(ExportResult.FAILED_NOT_RETRYABLE)

    def shutdown(self) -> None:
        """Shuts down the exporter.

        Called when the SDK is shut down.
        """
        self.storage.close()

    def _span_to_envelope(self, span: Span) -> TelemetryItem:
        if not span:
            return None
        envelope = _convert_span_to_envelope(span)
        envelope.instrumentation_key = self._instrumentation_key
        return envelope

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
def _convert_span_to_envelope(span: Span) -> TelemetryItem:
    envelope = TelemetryItem(
        name="",
        instrumentation_key="",
        tags=dict(_utils.azure_monitor_context),
        time=ns_to_iso_str(span.start_time),
    )
    if span.resource and span.resource.attributes:
        service_name = span.resource.attributes.get("service.name")
        service_namespace = span.resource.attributes.get("service.namespace")
        service_instance_id = span.resource.attributes.get("service.instance.id")
        user_id = span.resource.attributes.get("enduser.id")
        if service_name:
            if service_namespace:
                envelope.tags["ai.cloud.role"] = service_namespace + \
                    "." + service_name
            else:
                envelope.tags["ai.cloud.role"] = service_name
        if service_instance_id:
            envelope.tags["ai.cloud.roleInstance"] = service_instance_id
        else:
            envelope.tags["ai.cloud.roleInstance"] = platform.node()  # hostname default
        envelope.tags["ai.internal.nodeName"] = envelope.tags["ai.cloud.roleInstance"]
        if user_id:
            envelope.tags["ai.user.id"] = user_id

    envelope.tags["ai.operation.id"] = "{:032x}".format(span.context.trace_id)
    parent = span.parent
    if parent:
        envelope.tags["ai.operation.parentId"] = "{:016x}".format(
            parent.span_id
        )
    if span.kind in (SpanKind.CONSUMER, SpanKind.SERVER):
        envelope.name = "Microsoft.ApplicationInsights.Request"
        data = RequestData(
            name=span.name[:1024],  # Breeze max length
            id="{:016x}".format(span.context.span_id),
            duration=_utils.ns_to_duration(span.end_time - span.start_time),
            response_code="0",
            success=span.status.is_ok,
            properties={},
        )
        envelope.data = MonitorBase(base_data=data, base_type="RequestData")
        if "http.method" in span.attributes:  # HTTP
            if span.name and span.name.startswith("/"):
                envelope.tags["ai.operation.name"] = "{} {}".format(
                    span.attributes["http.method"],
                    span.name,
                )
            else:
                envelope.tags["ai.operation.name"] = span.name
            if "http.client_ip" in span.attributes:
                envelope.tags["ai.location.ip"] = span.attributes["http.client_ip"]
            elif "net.peer.ip" in span.attributes:
                envelope.tags["ai.location.ip"] = span.attributes["net.peer.ip"]
            if "http.url" in span.attributes:
                data.url = span.attributes["http.url"][:2048]  # Breeze max length
                data.properties["request.url"] = span.attributes["http.url"]
            if "http.status_code" in span.attributes:
                status_code = span.attributes["http.status_code"]
                data.response_code = str(status_code)
        elif "messaging.system" in span.attributes:  # Messaging
            envelope.tags["ai.operation.name"] = span.name
            if "net.peer.ip" in span.attributes:
                envelope.tags["ai.location.ip"] = span.attributes["net.peer.ip"]
            if "messaging.destination" in span.attributes:
                if "net.peer.name" in span.attributes:
                    data.properties["source"] = "{}/{}".format(
                        span.attributes["net.peer.name"],
                        span.attributes["messaging.destination"],
                    )
                elif "net.peer.ip" in span.attributes:
                    data.properties["source"] = "{}/{}".format(
                        span.attributes["net.peer.ip"],
                        span.attributes["messaging.destination"],
                    )
                else:
                    data.properties["source"] = span.attributes["messaging.destination"]
        else:  # Other
            envelope.tags["ai.operation.name"] = span.name
            if "net.peer.ip" in span.attributes:
                envelope.tags["ai.location.ip"] = span.attributes["net.peer.ip"]
        data.response_code = data.response_code[:1024]  # Breeze max length
    else:  # INTERNAL, CLIENT, PRODUCER
        envelope.name = "Microsoft.ApplicationInsights.RemoteDependency"
        # TODO: ai.operation.name for non-server spans
        data = RemoteDependencyData(
            name=span.name[:1024],  # Breeze max length
            id="{:016x}".format(span.context.span_id),
            result_code=str(span.status.status_code.value),
            duration=_utils.ns_to_duration(span.end_time - span.start_time),
            success=span.status.is_ok,
            properties={},
        )
        envelope.data = MonitorBase(
            base_data=data, base_type="RemoteDependencyData"
        )
        target = None
        if "peer.service" in span.attributes:
            target = span.attributes["peer.service"]
        if span.kind in (SpanKind.CLIENT, SpanKind.PRODUCER):
            if "http.method" in span.attributes:  # HTTP
                data.type = "HTTP"
                scheme = span.attributes["http.scheme"]
                if "http.host" in span.attributes:
                    host = span.attributes["http.host"]
                    try:
                        # urlparse insists on absolute URLs starting with "//"
                        host_name = urlparse("//" + host)
                        if host_name.port == _get_default_port_http(scheme):
                            target = host_name.hostname
                        else:
                            target = host
                    except Exception:  # pylint: disable=broad-except
                        logger.warning("Error while parsing hostname.")
                elif "http.url" in span.attributes:
                    url = span.attributes["http.url"]
                    # data is the url
                    data.data = url
                    try:
                        parse_url = urlparse(url)
                        if parse_url.port == _get_default_port_http(scheme):
                            target = parse_url.hostname
                        else:
                            target = parse_url.netloc
                    except Exception:  # pylint: disable=broad-except
                        logger.warning("Error while parsing url.")
                if "http.status_code" in span.attributes:
                    status_code = span.attributes["http.status_code"]
                    data.result_code = str(status_code)
            if target is None:
                if "net.peer.name" in span.attributes:
                    target = span.attributes["net.peer.name"]
                elif "net.peer.ip" in span.attributes:
                    target = span.attributes["net.peer.ip"]
                if "net.peer.port" in span.attributes:
                    port = span.attributes["net.peer.port"]
                    # TODO: check default port for rpc
                    # This logic assumes default ports never conflict across dependency types
                    if port != _get_default_port_http(span.attributes["http.scheme"]) and \
                        port != _get_default_port_db(span.attributes["db.system"]):
                        target = "{}:{}".format(target,port)
            if "db.system" in span.attributes:  # Database
                db = span.attributes["db.system"]
                if _is_relational_db(db):
                    data.type = "SQL"
                else:
                    data.type = db
                # data is the full statement
                if "db.statement" in span.attributes:
                    data.data = span.attributes["db.statement"]
                if "db.name" in span.attributes:
                    db_name = span.attributes
                    if target is None:
                        target = db_name
                    else:
                        target = "{}/{}".format(target, db_name)
            elif "rpc.system" in span.attributes:  # Rpc
                data.type = "rpc.system"
                if target is None:
                    target = span.attributes["rpc.system"]
            else:
                # TODO: Azure specific types
                data.type = "N/A"
        elif span.kind is SpanKind.PRODUCER:  # Messaging
            data.type = "Queue Message"
            if "net.peer.ip" in span.attributes and \
                    "messaging.destination" in span.attributes:
                data.target = "{}/{}".format(
                    span.attributes["net.peer.ip"],
                    span.attributes["messaging.destination"]
                )
            else:
                data.target = span.attributes["messaging.system"]
        else:  # SpanKind.INTERNAL
            data.type = "InProc"
            data.success = True
        data.result_code = data.result_code[:1024]  # Breeze max length
        data.target = target
    for key in span.attributes:
        # Remove Opentelemetry related span attributes from custom dimensions
        if key.startswith("http.") or \
                key.startswith("db.") or \
                key.startswith("rpc.") or \
                key.startswith("net.") or \
                key.startswith("messaging."):
            continue
        data.properties[key] = span.attributes[key]
    if span.links:
        links = []
        for link in span.links:
            operation_id = "{:032x}".format(link.context.trace_id)
            span_id = "{:016x}".format(link.context.span_id)
            links.append({"operation_Id": operation_id, "id": span_id})
        data.properties["_MS.links"] = json.dumps(links)
    # TODO: tracestate, tags
    return envelope


def _get_default_port_db(dbsystem):
    if dbsystem == "postgresql":
        return 5432
    elif dbsystem == "mysql":
        return 3306
    elif dbsystem == "memcached":
        return 11211
    elif dbsystem == "mongodb":
        return 27017
    elif dbsystem == "redis":
        return 6379
    else:
        return 0


def _get_default_port_http(scheme):
    if scheme == "http":
        return 80
    elif scheme == "https":
        return 443
    else:
        return 0


def _is_relational_db(dbsystem):
    return dbsystem in ["postgresql", "mysql"]
