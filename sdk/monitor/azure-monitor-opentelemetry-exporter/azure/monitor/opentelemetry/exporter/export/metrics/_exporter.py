# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import logging

from typing import Optional, Any

from opentelemetry.sdk.metrics.export import (
    DataPointT,
    HistogramDataPoint,
    MetricExporter,
    MetricExportResult,
    MetricsData as OTMetricsData,
    NumberDataPoint,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.util.instrumentation import InstrumentationScope

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
        self,
        metrics_data: OTMetricsData,
        timeout_millis: float = 10_000,  # pylint: disable=unused-argument
        **kwargs: Any,  # pylint: disable=unused-argument
    ) -> MetricExportResult:
        """Exports a batch of metric data
        :param metrics: Open Telemetry Metric(s) to export.
        :type metrics_data: Sequence[~opentelemetry.sdk.metrics._internal.point.MetricsData]
        :rtype: ~opentelemetry.sdk.metrics.export.MetricExportResult
        """
        envelopes = []
        if metrics_data is None:
            return MetricExportResult.SUCCESS
        for resource_metric in metrics_data.resource_metrics:
            for scope_metric in resource_metric.scope_metrics:
                for metric in scope_metric.metrics:
                    for point in metric.data.data_points:
                        if point is not None:
                            envelopes.append(
                                self._point_to_envelope(
                                    point,
                                    metric.name,
                                    resource_metric.resource,
                                    scope_metric.scope
                                )
                            )
        try:
            result = self._transmit(envelopes)
            self._handle_transmit_from_storage(envelopes, result)
            return _get_metric_export_result(result)
        except Exception:  # pylint: disable=broad-except
            _logger.exception("Exception occurred while exporting the data.")
            return _get_metric_export_result(ExportResult.FAILED_NOT_RETRYABLE)

    def shutdown(
        self,
        timeout_millis: float = 30_000,  # pylint: disable=unused-argument
        **kwargs: Any,  # pylint: disable=unused-argument
    ) -> None:
        """Shuts down the exporter.

        Called when the SDK is shut down.
        """
        self.storage.close()

    def _point_to_envelope(
        self,
        point: DataPointT,
        name: str,
        resource: Optional[Resource] = None,
        scope: Optional[InstrumentationScope] = None
    ) -> TelemetryItem:
        envelope = _convert_point_to_envelope(point, name, resource, scope)
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
def _convert_point_to_envelope(
    point: DataPointT,
    name: str,
    resource: Optional[Resource] = None,
    scope: Optional[InstrumentationScope] = None  # pylint: disable=unused-argument
) -> TelemetryItem:
    envelope = _utils._create_telemetry_item(point.time_unix_nano)
    envelope.name = "Microsoft.ApplicationInsights.Metric"
    envelope.tags.update(_utils._populate_part_a_fields(resource))
    value = 0
    count = 1
    min_ = None
    max_ = None
    # std_dev = None

    if isinstance(point, NumberDataPoint):
        value = point.value
    elif isinstance(point, HistogramDataPoint):
        value = point.sum
        count = point.count
        min_ = point.min
        max_ = point.max

    data_point = MetricDataPoint(
        name=name,
        value=value,
        data_point_type="Aggregation",
        count=count,
        min=min_,
        max=max_,
    )
    data = MetricsData(
        properties=dict(point.attributes),
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
