# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import logging

from typing import Any

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
from azure.monitor.opentelemetry.exporter.quickpulse._generated._client import QuickpulseClient
from azure.monitor.opentelemetry.exporter._connection_string_parser import ConnectionStringParser

_logger = logging.getLogger(__name__)

__all__ = ["QuickPulseExporter"]


APPLICATION_INSIGHTS_METRIC_TEMPORALITIES = {
    Counter: AggregationTemporality.DELTA,
    Histogram: AggregationTemporality.DELTA,
    ObservableCounter: AggregationTemporality.DELTA,
    ObservableGauge: AggregationTemporality.CUMULATIVE,
    ObservableUpDownCounter: AggregationTemporality.CUMULATIVE,
    UpDownCounter: AggregationTemporality.CUMULATIVE,
}


class QuickPulseExporter(MetricExporter):
    """Azure Monitor Metric exporter for OpenTelemetry."""

    def __init__(self, **kwargs: Any) -> None:
        """Azure Monitor base exporter for OpenTelemetry.

        :keyword str connection_string: The connection string used for your Application Insights resource.
        :rtype: None
        """
        parsed_connection_string = ConnectionStringParser(kwargs.get('connection_string'))

        self._endpoint = parsed_connection_string.endpoint
        # TODO: Support AADaudience (scope)/credentials

        self.client = QuickpulseClient(host=self._endpoint, **kwargs)
        # TODO: Support redirect

        MetricExporter.__init__(
            self,
            preferred_temporality=APPLICATION_INSIGHTS_METRIC_TEMPORALITIES, # type: ignore
            preferred_aggregation=kwargs.get("preferred_aggregation"), # type: ignore
        )

    def export(
        self,
        metrics_data: OTMetricsData,
        timeout_millis: float = 10_000,  # pylint: disable=unused-argument
        **kwargs: Any,  # pylint: disable=unused-argument
    ) -> MetricExportResult:
        # TODO
        return None

    def force_flush(
        self,
        timeout_millis: float = 10_000,
    ) -> bool:
        """
        Ensure that export of any metrics currently received by the exporter
        are completed as soon as possible. Called when SDK is flushed.

        :param timeout_millis: The maximum amount of time to wait for shutdown. Not currently used.
        :type timeout_millis: float
        """
        return True


    def shutdown(
        self,
        timeout_millis: float = 30_000,  # pylint: disable=unused-argument
        **kwargs: Any,  # pylint: disable=unused-argument
    ) -> None:
        """Shuts down the exporter.

        Called when the SDK is shut down.

        :param timeout_millis: The maximum amount of time to wait for shutdown. Not currently used.
        :type timeout_millis: float
        """
