# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import logging
from typing import Sequence

from opentelemetry.sdk.metrics.export import (
    ExportRecord,
    MetricsExporter,
    MetricsExportResult,
)
from opentelemetry.sdk.metrics.export.aggregate import (
    HistogramAggregator,
    MinMaxSumCountAggregator,
    ValueObserverAggregator,
)
from opentelemetry.sdk.util import ns_to_iso_str

from azure.monitor.opentelemetry.exporter import _utils
from azure.monitor.opentelemetry.exporter._generated.models import (
    MetricDataPoint,
    MetricsData,
    MonitorBase,
    TelemetryItem
)
from azure.monitor.opentelemetry.exporter.export._base import (
    BaseExporter,
    ExportResult,
    get_metrics_export_result,
)

logger = logging.getLogger(__name__)

__all__ = ["AzureMonitorMetricsExporter"]


class AzureMonitorMetricsExporter(BaseExporter, MetricsExporter):
    """Azure Monitor metrics exporter for OpenTelemetry."""

    def export(
        self, export_records: Sequence[ExportRecord]
    ) -> MetricsExportResult:
        """Export data
        :param export_records: Open Telemetry metric records to export.
        :type ExportRecord: ~opentelemetry.sdk.metrics.export.ExportRecord
        """
        envelopes = [self._metric_to_envelope(record) for record in export_records]
        try:
            result = self._transmit(envelopes)
            if result == ExportResult.FAILED_RETRYABLE:
                envelopes_to_store = [x.as_dict() for x in envelopes]
                self.storage.put(envelopes_to_store, 1)
            if result == ExportResult.SUCCESS:
                # Try to send any cached events
                self._transmit_from_storage()
            return get_metrics_export_result(result)
        except Exception:  # pylint: disable=broad-except
            logger.exception("Exception occurred while exporting the data.")
            return get_metrics_export_result(ExportResult.FAILED_NOT_RETRYABLE)

    def shutdown(self):
        """Shuts down the exporter.

        Called when the SDK is shut down.
        """
        self.storage.close()

    def _metric_to_envelope(self, export_record: ExportRecord) -> TelemetryItem:
        if not export_record:
            return None
        envelope = convert_metric_to_envelope(export_record)
        envelope.instrumentation_key = self._instrumentation_key
        # print(envelope.instrumentation_key)
        return envelope


# pylint: disable=too-many-statements
# pylint: disable=too-many-branches
def convert_metric_to_envelope(export_record: ExportRecord) -> TelemetryItem:
    envelope = TelemetryItem(
        name="Microsoft.ApplicationInsights.Metric",
        instrumentation_key="",
        tags=dict(_utils.azure_monitor_context),
        time=ns_to_iso_str(export_record.aggregator.last_update_timestamp),
    )
    if export_record.resource and export_record.resource.attributes:
        # TODO: Get Resource attributes from OpenTelemetry SDK when available
        service_name = export_record.resource.attributes.get("service.name")
        service_namespace = export_record.resource.attributes.get("service.namespace")
        service_instance_id = export_record.resource.attributes.get("service.instance.id")
        if service_name:
            if service_namespace:
                envelope.tags["ai.cloud.role"] = service_namespace + \
                    "." + service_name
            else:
                envelope.tags["ai.cloud.role"] = service_name
        if service_instance_id:
            envelope.tags["ai.cloud.roleInstance"] = service_instance_id

    value = 0
    _min = None
    _max = None
    count = None
    metric = export_record.instrument
    aggregator = export_record.aggregator
    if isinstance(aggregator, ValueObserverAggregator):
        # mmscl
        value = aggregator.checkpoint.last
    elif isinstance(aggregator, MinMaxSumCountAggregator):
        # mmsc
        value = aggregator.checkpoint.sum
        _min = aggregator.checkpoint.min
        _max = aggregator.checkpoint.max
        count = aggregator.checkpoint.count
    elif isinstance(aggregator, HistogramAggregator):
        # TODO
        value = 0
    else:
        # sum or lv
        value = aggregator.checkpoint
    if value is None:
        logger.warning("Value is none. Default to 0.")
        value = 0
    data_point = MetricDataPoint(
        namespace=metric.description,
        name=metric.name,
        value=value,
        min=_min,
        max=_max,
        count=count,
        data_point_type="Aggregation",
    )

    properties = {}
    for label_tuple in export_record.labels:
        properties[label_tuple[0]] = label_tuple[1]
    data = MetricsData(metrics=[data_point], properties=properties)
    envelope.data = MonitorBase(base_data=data, base_type="MetricData")
    return envelope
