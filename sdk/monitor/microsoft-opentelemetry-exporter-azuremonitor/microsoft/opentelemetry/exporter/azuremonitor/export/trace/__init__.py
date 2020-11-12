# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import json
import logging
from typing import Sequence
from urllib.parse import urlparse

from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from opentelemetry.sdk.util import ns_to_iso_str
from opentelemetry.trace import Span, SpanKind
from opentelemetry.trace.status import StatusCode

from microsoft.opentelemetry.exporter.azuremonitor import utils
from microsoft.opentelemetry.exporter.azuremonitor._generated.models import (
    MonitorBase,
    RemoteDependencyData,
    RequestData,
    TelemetryItem
)
from microsoft.opentelemetry.exporter.azuremonitor.export import (
    BaseExporter,
    ExportResult,
    get_trace_export_result,
)

logger = logging.getLogger(__name__)


class AzureMonitorSpanExporter(BaseExporter, SpanExporter):
    """Azure Monitor span exporter for OpenTelemetry.

    Args:
        options: :doc:`export.options` to allow configuration for the exporter
    """

    def __init__(self, **options):
        super().__init__(**options)
        self.add_telemetry_processor(indicate_processed_by_metric_extractors)

    def export(self, spans: Sequence[Span]) -> SpanExportResult:
        envelopes = [self._span_to_envelope(span) for span in spans]
        envelopes = self._apply_telemetry_processors(envelopes)
        try:
            result = self._transmit(envelopes)
            if result == ExportResult.FAILED_RETRYABLE:
                self.storage.put(envelopes, result)
            if result == ExportResult.SUCCESS:
                # Try to send any cached events
                self._transmit_from_storage()
            return get_trace_export_result(result)
        except Exception:  # pylint: disable=broad-except
            logger.exception("Exception occurred while exporting the data.")
            return get_trace_export_result(ExportResult.FAILED_NOT_RETRYABLE)

    def _span_to_envelope(self, span: Span) -> TelemetryItem:
        if not span:
            return None
        envelope = convert_span_to_envelope(span)
        envelope.instrumentation_key = self.options.instrumentation_key
        return envelope


# pylint: disable=too-many-statements
# pylint: disable=too-many-branches
def convert_span_to_envelope(span: Span) -> TelemetryItem:
    envelope = TelemetryItem(
        name="",
        instrumentation_key="",
        tags=dict(utils.azure_monitor_context),
        time=ns_to_iso_str(span.start_time),
    )
    envelope.tags["ai.operation.id"] = "{:032x}".format(span.context.trace_id)
    parent = span.parent
    if parent:
        envelope.tags["ai.operation.parentId"] = "{:016x}".format(
            parent.span_id
        )
    if span.kind in (SpanKind.CONSUMER, SpanKind.SERVER):
        envelope.name = "Microsoft.ApplicationInsights.Request"
        data = RequestData(
            id="{:016x}".format(span.context.span_id),
            duration=utils.ns_to_duration(span.end_time - span.start_time),
            response_code=str(span.status.status_code.value),
            success=span.status.status_code
            == StatusCode.OK,  # Modify based off attributes or Status
            properties={},
        )
        envelope.data = MonitorBase(base_data=data, base_type="RequestData")
        if "http.method" in span.attributes:
            data.name = span.attributes["http.method"]
            if "http.route" in span.attributes:
                data.name = data.name + " " + span.attributes["http.route"]
                envelope.tags["ai.operation.name"] = data.name
                data.properties["request.name"] = data.name
            elif "http.path" in span.attributes:
                data.properties["request.name"] = (
                    data.name + " " + span.attributes["http.path"]
                )
        if "http.url" in span.attributes:
            data.url = span.attributes["http.url"]
            data.properties["request.url"] = span.attributes["http.url"]
        if "http.status_code" in span.attributes:
            status_code = span.attributes["http.status_code"]
            data.response_code = str(status_code)
            data.success = 200 <= status_code < 400
    else:
        envelope.name = "Microsoft.ApplicationInsights.RemoteDependency"
        data = RemoteDependencyData(
            name=span.name,
            id="{:016x}".format(span.context.span_id),
            result_code=str(span.status.status_code.value),
            duration=utils.ns_to_duration(span.end_time - span.start_time),
            success=span.status.status_code
            == StatusCode.OK,  # Modify based off attributes or Status
            properties={},
        )
        envelope.data = MonitorBase(
            base_data=data, base_type="RemoteDependencyData"
        )
        if span.kind in (SpanKind.CLIENT, SpanKind.PRODUCER):
            if (
                "component" in span.attributes
                and span.attributes["component"] == "http"
            ):
                # TODO: check other component types (e.g. db)
                data.type = "HTTP"
            if "http.url" in span.attributes:
                url = span.attributes["http.url"]
                # data is the url
                data.data = url
                parse_url = urlparse(url)
                # TODO: error handling, probably put scheme as well
                # target matches authority (host:port)
                data.target = parse_url.netloc
                if "http.method" in span.attributes:
                    # name is METHOD/path
                    data.name = (
                        span.attributes["http.method"] + "/" + parse_url.path
                    )
            if "http.status_code" in span.attributes:
                status_code = span.attributes["http.status_code"]
                data.result_code = str(status_code)
                data.success = 200 <= status_code < 400
        else:  # SpanKind.INTERNAL
            data.type = "InProc"
            data.success = True
    for key in span.attributes:
        # This removes redundant data from ApplicationInsights
        if key.startswith("http."):
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


def indicate_processed_by_metric_extractors(envelope):
    name = "Requests"
    if envelope.data.base_type == "RemoteDependencyData":
        name = "Dependencies"
    envelope.data.base_data.properties["_MS.ProcessedByMetricExtractors"] = (
        "(Name:'" + name + "',Ver:'1.1')"
    )
