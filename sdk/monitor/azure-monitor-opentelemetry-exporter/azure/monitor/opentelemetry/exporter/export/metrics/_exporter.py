# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import logging
from typing import Sequence, Any

from opentelemetry.sdk._metrics.export import MetricExporter, MetricExportResult
from opentelemetry.sdk._metrics.point import (
    Gauge,
    Histogram,
    Metric,
    Sum,
)

from azure.monitor.opentelemetry.exporter import _utils
from azure.monitor.opentelemetry.exporter._generated.models import (
    MetricDataPoint,
    MetricsData,
    MonitorBase,
    TelemetryItem,
)
from azure.monitor.opentelemetry.exporter.export._base import (
    BaseExporter,
    ExportResult,
)

_logger = logging.getLogger(__name__)

__all__ = ["AzureMonitorMetricExporter"]


class AzureMonitorMetricExporter(BaseExporter, MetricExporter):
    """Azure Monitor Metric exporter for OpenTelemetry."""

    def export(
        self, metrics: Sequence[Metric], **kwargs: Any  # pylint: disable=unused-argument
    ) -> MetricExportResult:
        """Exports a batch of metric data
        :param metrics: Open Telemetry Metric(s) to export.
        :type metrics: Sequence[~opentelemetry._metrics.point.Metric]
        :rtype: ~opentelemetry.sdk._metrics.export.MetricExportResult
        """
        envelopes = [self._metric_to_envelope(metric) for metric in metrics]
        try:
            result = self._transmit(envelopes)
            if result == ExportResult.FAILED_RETRYABLE:
                envelopes_to_store = [x.as_dict() for x in envelopes]
                self.storage.put(envelopes_to_store, 1)
            if result == ExportResult.SUCCESS:
                # Try to send any cached events
                self._transmit_from_storage()
            return _get_metric_export_result(result)
        except Exception:  # pylint: disable=broad-except
            _logger.exception("Exception occurred while exporting the data.")
            return _get_metric_export_result(ExportResult.FAILED_NOT_RETRYABLE)

    def shutdown(self) -> None:
        """Shuts down the exporter.

        Called when the SDK is shut down.
        """
        self.storage.close()

    def _metric_to_envelope(self, metric: Metric) -> TelemetryItem:
        if not metric:
            return None
        envelope = _convert_metric_to_envelope(metric)
        envelope.instrumentation_key = self._instrumentation_key
        return envelope

    @classmethod
    def from_connection_string(
        cls, conn_str: str, **kwargs: Any
    ) -> "AzureMonitorMetricExporter":
        """
        Create an AzureMonitorMetricExporter from a connection string.

        This is the recommended way of instantation if a connection string is passed in explicitly.
        If a user wants to use a connection string provided by environment variable, the constructor
        of the exporter can be called directly.

        :param str conn_str: The connection string to be used for authentication.
        :keyword str api_version: The service API version used. Defaults to latest.
        :returns an instance of ~AzureMonitorMetricExporter
        """
        return cls(connection_string=conn_str, **kwargs)


# pylint: disable=protected-access
def _convert_metric_to_envelope(metric: Metric) -> TelemetryItem:
    point = metric.point
    envelope = _utils._create_telemetry_item(point.time_unix_nano)
    envelope.name = "Microsoft.ApplicationInsights.Metric"
    envelope.tags.update(_utils._populate_part_a_fields(metric.resource))
    properties = metric.attributes
    value = 0
    # TODO
    count = 1
    # min = None
    # max = None
    # std_dev = None

    if isinstance(point, (Gauge, Sum)):
        value = point.value
    elif isinstance(point, Histogram):
        value = sum(point.bucket_counts)
        count = sum(point.bucket_counts)

    data_point = MetricDataPoint(
        name=metric.name,
        value=value,
        data_point_type="Aggregation",
        count=count,
    )
    data = MetricsData(
        properties=properties,
        metrics=[data_point],
    )

    envelope.data = MonitorBase(base_data=data, base_type="MetricData")

    return envelope


def _get_metric_export_result(result: ExportResult) -> MetricExportResult:
    if result == ExportResult.SUCCESS:
        return MetricExportResult.SUCCESS
    if result in (
        ExportResult.FAILED_RETRYABLE,
        ExportResult.FAILED_NOT_RETRYABLE,
    ):
        return MetricExportResult.FAILURE
    return None
