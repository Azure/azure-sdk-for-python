# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import json
import logging
from typing import Sequence
from urllib.parse import urlparse

from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from opentelemetry.sdk.util import ns_to_iso_str
from opentelemetry.trace import Span, SpanKind

from azure.opentelemetry.exporter.azuremonitor import _utils
from azure.opentelemetry.exporter.azuremonitor._generated.models import (
    MonitorBase,
    RemoteDependencyData,
    RequestData,
    TelemetryItem
)
from azure.opentelemetry.exporter.azuremonitor.export._base import (
    BaseExporter,
    ExportResult,
    get_trace_export_result,
)

logger = logging.getLogger(__name__)

__all__ = ["AzureMonitorTraceExporter"]


class AzureMonitorTraceExporter(BaseExporter, SpanExporter):
    """Azure Monitor base exporter for OpenTelemetry.

    :param options: Exporter configuration options.
    :type options: ~azure.opentelemetry.exporter.azuremonitor.options.ExporterOptions
    """

    def export(self, spans: Sequence[Span]) -> SpanExportResult:
        """Export data
        :param spans: Open Telemetry Spans to export.
        :type spans: ~opentelemetry.trace.Span
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

    def shutdown(self):
        """Shuts down the exporter.

        Called when the SDK is shut down.
        """
        self.storage.close()

    def _span_to_envelope(self, span: Span) -> TelemetryItem:
        if not span:
            return None
        envelope = convert_span_to_envelope(span)
        envelope.instrumentation_key = self._instrumentation_key
        return envelope


# pylint: disable=too-many-statements
# pylint: disable=too-many-branches
def convert_span_to_envelope(span: Span) -> TelemetryItem:
    envelope = TelemetryItem(
        name="",
        instrumentation_key="",
        tags=dict(_utils.azure_monitor_context),
        time=ns_to_iso_str(span.start_time),
    )
    if span.resource and span.resource.attributes:
        # TODO: Get Resource attributes from OpenTelemetry SDK when available
        service_name = span.resource.attributes.get("service.name")
        service_namespace = span.resource.attributes.get("service.namespace")
        service_instance_id = span.resource.attributes.get("service.instance.id")
        if service_name:
            if service_namespace:
                envelope.tags["ai.cloud.role"] = service_namespace + \
                    "." + service_name
            else:
                envelope.tags["ai.cloud.role"] = service_name
        if service_instance_id:
            envelope.tags["ai.cloud.roleInstance"] = service_instance_id

    envelope.tags["ai.operation.id"] = "{:032x}".format(span.context.trace_id)
    parent = span.parent
    if parent:
        envelope.tags["ai.operation.parentId"] = "{:016x}".format(
            parent.span_id
        )
    if span.kind in (SpanKind.CONSUMER, SpanKind.SERVER):
        envelope.name = "Microsoft.ApplicationInsights.Request"
        data = RequestData(
            name=span.name,
            id="{:016x}".format(span.context.span_id),
            duration=_utils.ns_to_duration(span.end_time - span.start_time),
            response_code=str(span.status.status_code.value),
            success=span.status.is_ok,
            properties={},
        )
        envelope.data = MonitorBase(base_data=data, base_type="RequestData")
        if "http.method" in span.attributes:  # HTTP
            if "http.route" in span.attributes:
                envelope.tags["ai.operation.name"] = span.attributes["http.route"]
            elif "http.path" in span.attributes:
                envelope.tags["ai.operation.name"] = span.attributes["http.path"]
            else:
                envelope.tags["ai.operation.name"] = span.name

            if "http.url" in span.attributes:
                data.url = span.attributes["http.url"]
                data.properties["request.url"] = span.attributes["http.url"]
            if "http.status_code" in span.attributes:
                status_code = span.attributes["http.status_code"]
                data.response_code = str(status_code)
        elif "messaging.system" in span.attributes:  # Messaging
            envelope.tags["ai.operation.name"] = span.name

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
    else:
        envelope.name = "Microsoft.ApplicationInsights.RemoteDependency"
        data = RemoteDependencyData(
            name=span.name,
            id="{:016x}".format(span.context.span_id),
            result_code=str(span.status.status_code.value),
            duration=_utils.ns_to_duration(span.end_time - span.start_time),
            success=span.status.is_ok,
            properties={},
        )
        envelope.data = MonitorBase(
            base_data=data, base_type="RemoteDependencyData"
        )
        if span.kind in (SpanKind.CLIENT, SpanKind.PRODUCER):
            if "http.method" in span.attributes:  # HTTP
                data.type = "HTTP"
                if "net.peer.port" in span.attributes:
                    name = ""
                    if "net.peer.name" in span.attributes:
                        name = span.attributes["net.peer.name"]
                    elif "net.peer.ip" in span.attributes:
                        name = str(span.attributes["net.peer.ip"])
                    data.target = "{}:{}".format(
                        name,
                        str(span.attributes["net.peer.port"]),
                    )
                elif "http.url" in span.attributes:
                    url = span.attributes["http.url"]
                    # data is the url
                    data.data = url
                    parse_url = urlparse(url)
                    # target matches authority (host:port)
                    data.target = parse_url.netloc
                if "http.status_code" in span.attributes:
                    status_code = span.attributes["http.status_code"]
                    data.result_code = str(status_code)
            elif "db.system" in span.attributes:  # Database
                data.type = span.attributes["db.system"]
                # data is the full statement
                if "db.statement" in span.attributes:
                    data.data = span.attributes["db.statement"]
                if "db.name" in span.attributes:
                    data.target = span.attributes["db.name"]
                else:
                    data.target = span.attributes["db.system"]
            elif "rpc.system" in span.attributes:  # Rpc
                data.type = "rpc.system"
                if "rpc.service" in span.attributes:
                    data.target = span.attributes["rpc.service"]
                else:
                    data.target = span.attributes["rpc.system"]
            elif "messaging.system" in span.attributes:  # Messaging
                data.type = "Queue Message | {}" \
                    .format(span.attributes["messaging.system"])
                if "net.peer.ip" in span.attributes and \
                        "messaging.destination" in span.attributes:
                    data.target = "{}/{}".format(
                        span.attributes["net.peer.ip"],
                        span.attributes["messaging.destination"]
                    )
                else:
                    data.target = span.attributes["messaging.system"]
            else:
                # TODO: Azure specific types
                data.type = "N/A"
        else:  # SpanKind.INTERNAL
            data.type = "InProc"
            data.success = True
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
