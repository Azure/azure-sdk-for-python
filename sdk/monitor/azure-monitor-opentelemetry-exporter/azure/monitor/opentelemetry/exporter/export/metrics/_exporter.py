# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import logging

from typing import Mapping, Optional, Any

from opentelemetry.util.types import AttributeValue
from opentelemetry.sdk.metrics import (
    Counter,
    Histogram,
    ObservableCounter,
    ObservableGauge,
    ObservableUpDownCounter,
    UpDownCounter,
)
from opentelemetry.sdk.metrics.export import (
    AggregationTemporality,
    DataPointT,
    HistogramDataPoint,
    MetricExporter,
    MetricExportResult,
    MetricsData as OTMetricsData,
    NumberDataPoint,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.util.instrumentation import InstrumentationScope

from azure.monitor.opentelemetry.exporter._constants import _AUTOCOLLECTED_INSTRUMENT_NAMES
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


APPLICATION_INSIGHTS_METRIC_TEMPORALITIES = {
    Counter: AggregationTemporality.DELTA,
    Histogram: AggregationTemporality.DELTA,
    ObservableCounter: AggregationTemporality.DELTA,
    ObservableGauge: AggregationTemporality.CUMULATIVE,
    ObservableUpDownCounter: AggregationTemporality.CUMULATIVE,
    UpDownCounter: AggregationTemporality.CUMULATIVE,
}


class AzureMonitorMetricExporter(BaseExporter, MetricExporter):
    """Azure Monitor Metric exporter for OpenTelemetry."""

    def __init__(self, **kwargs: Any) -> None:
        BaseExporter.__init__(self, **kwargs)
        MetricExporter.__init__(
            self,
            preferred_temporality=APPLICATION_INSIGHTS_METRIC_TEMPORALITIES,
            preferred_aggregation=kwargs.get("preferred_aggregation"),
        )

    # pylint: disable=R1702
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
                            envelope = self._point_to_envelope(
                                point,
                                metric.name,
                                resource_metric.resource,
                                scope_metric.scope
                            )
                            if envelope is not None:
                                envelopes.append(envelope)
        try:
            result = self._transmit(envelopes)
            self._handle_transmit_from_storage(envelopes, result)
            return _get_metric_export_result(result)
        except Exception:  # pylint: disable=broad-except
            _logger.exception("Exception occurred while exporting the data.")
            return _get_metric_export_result(ExportResult.FAILED_NOT_RETRYABLE)

    def force_flush(
        self,
        timeout_millis: float = 10_000,
    ) -> bool:
        """
        Ensure that export of any metrics currently received by the exporter
        are completed as soon as possible.
        """
        return True

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
    ) -> Optional[TelemetryItem]:
        envelope = _convert_point_to_envelope(point, name, resource, scope)
        if name in _AUTOCOLLECTED_INSTRUMENT_NAMES:
            envelope = _handle_std_metric_envelope(envelope, name, point.attributes)
        if envelope is not None:
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
    scope: Optional[InstrumentationScope] = None
) -> TelemetryItem:
    envelope = _utils._create_telemetry_item(point.time_unix_nano)
    envelope.name = "Microsoft.ApplicationInsights.Metric"
    envelope.tags.update(_utils._populate_part_a_fields(resource))
    namespace = None
    if scope is not None:
        namespace = scope.name
    value = 0
    count = 1
    min_ = None
    max_ = None
    # std_dev = None

    if isinstance(point, NumberDataPoint):
        value = point.value
    elif isinstance(point, HistogramDataPoint):
        value = point.sum
        count = int(point.count)
        min_ = point.min
        max_ = point.max

    # truncation logic
    properties = _utils._filter_custom_properties(point.attributes)

    if namespace is not None:
        namespace = str(namespace)[:256]
    data_point = MetricDataPoint(
        name=str(name)[:1024],
        namespace=namespace,
        value=value,
        count=count,
        min=min_,
        max=max_,
    )

    data = MetricsData(
        properties=properties,
        metrics=[data_point],
    )

    envelope.data = MonitorBase(base_data=data, base_type="MetricData")

    return envelope


# pylint: disable=protected-access
def _handle_std_metric_envelope(
    envelope: TelemetryItem,
    name: str,
    attributes:Mapping[str, AttributeValue]
) -> Optional[TelemetryItem]:
    properties = {}
    tags = envelope.tags
    # TODO: switch to semconv constants
    status_code = attributes.get("http.status_code", None)
    if name == "http.client.duration":
        properties["_MS.MetricId"] = "dependencies/duration"
        properties["_MS.IsAutocollected"] = "True"
        properties["Dependency.Type"] = "http"
        properties["Dependency.Success"] = str(_is_status_code_success(status_code, 400))
        target = None
        if "peer.service" in attributes:
            target = attributes["peer.service"]
        elif "net.peer.name" in attributes:
            if attributes["net.peer.name"] is None:
                target = None
            elif "net.host.port" in attributes and \
                attributes["net.host.port"] is not None:
                target = "{}:{}".format(
                    attributes["net.peer.name"],
                    attributes["net.host.port"],
                )
            else:
                target = attributes["net.peer.name"]
        properties["dependency/target"] = target
        properties["dependency/resultCode"] = str(status_code)
        # TODO: operation/synthetic
        properties["cloud/roleInstance"] = tags["ai.cloud.roleInstance"]
        properties["cloud/roleName"] = tags["ai.cloud.role"]
    elif name == "http.server.duration":
        properties["_MS.MetricId"] = "requests/duration"
        properties["_MS.IsAutocollected"] = "True"
        properties["request/resultCode"] = str(status_code)
        # TODO: operation/synthetic
        properties["cloud/roleInstance"] = tags["ai.cloud.roleInstance"]
        properties["cloud/roleName"] = tags["ai.cloud.role"]
        properties["Request.Success"] = str(_is_status_code_success(status_code, 500))
    else:
        # Any other autocollected metrics are not supported yet for standard metrics
        # We ignore these envelopes in these cases
        return None

    # TODO: rpc, database, messaging

    envelope.data.base_data.properties = properties

    return envelope


def _is_status_code_success(status_code: Optional[str], threshold: int) -> bool:
    return status_code is not None and int(status_code) < threshold


def _get_metric_export_result(result: ExportResult) -> MetricExportResult:
    if result == ExportResult.SUCCESS:
        return MetricExportResult.SUCCESS
    if result in (
        ExportResult.FAILED_RETRYABLE,
        ExportResult.FAILED_NOT_RETRYABLE,
    ):
        return MetricExportResult.FAILURE
    return None
