# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import logging

from enum import Enum
from typing import Any, Optional

from azure.core.exceptions import HttpResponseError
from azure.monitor.opentelemetry.exporter._quickpulse._generated._client import QuickpulseClient
from azure.monitor.opentelemetry.exporter._quickpulse._generated.models import (
    CollectionConfigurationInfo,
    MonitoringDataPoint,
)
from azure.monitor.opentelemetry.exporter._connection_string_parser import ConnectionStringParser
from azure.monitor.opentelemetry.exporter._utils import _ticks_since_dot_net_epoch

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
    MetricExporter,
    MetricExportResult,
    MetricsData as OTMetricsData,
    PeriodicExportingMetricReader,
)

_logger = logging.getLogger(__name__)


_APPLICATION_INSIGHTS_METRIC_TEMPORALITIES = {
    Counter: AggregationTemporality.DELTA,
    Histogram: AggregationTemporality.DELTA,
    ObservableCounter: AggregationTemporality.DELTA,
    ObservableGauge: AggregationTemporality.CUMULATIVE,
    ObservableUpDownCounter: AggregationTemporality.CUMULATIVE,
    UpDownCounter: AggregationTemporality.CUMULATIVE,
}

_SHORT_PING_INTERVAL_SECONDS = 5
_SHORT_POST_INTERVAL_SECONDS = 1
_LONG_PING_INTERVAL_SECONDS = 60
_LONG_POST_INTERVAL_SECONDS = 20


class _QuickpulseExporter(MetricExporter):

    def __init__(self, connection_string: str) -> None:
        """Metric exporter for Quickpulse.

        :param str connection_string: The connection string used for your Application Insights resource.
        :rtype: None
        """
        parsed_connection_string = ConnectionStringParser(connection_string)

        self._endpoint = parsed_connection_string.endpoint
        self._instrumentation_key = parsed_connection_string.instrumentation_key
        # TODO: Support AADaudience (scope)/credentials

        self._client = QuickpulseClient(host=self._endpoint)
        # TODO: Support redirect

        MetricExporter.__init__(
            self,
            preferred_temporality=_APPLICATION_INSIGHTS_METRIC_TEMPORALITIES, # type: ignore
        )

    def export(
        self,
        metrics_data: OTMetricsData,
        timeout_millis: float = 10_000,  # pylint: disable=unused-argument
        **kwargs: Any,  # pylint: disable=unused-argument
    ) -> MetricExportResult:
        """Exports a batch of metric data

        :param metrics_data: OpenTelemetry Metric(s) to export.
        :type metrics_data: Sequence[~opentelemetry.sdk.metrics._internal.point.MetricsData]
        :param timeout_millis: The maximum amount of time to wait for each export. Not currently used.
        :type timeout_millis: float
        :return: The result of the export.
        :rtype: ~opentelemetry.sdk.metrics.export.MetricExportResult
        """
        # TODO
        return MetricExportResult.SUCCESS

    def force_flush(
        self,
        timeout_millis: float = 10_000,
    ) -> bool:
        """
        Ensure that export of any metrics currently received by the exporter
        are completed as soon as possible. Called when SDK is flushed.

        :param timeout_millis: The maximum amount of time to wait for shutdown. Not currently used.
        :type timeout_millis: float
        :return: The result of the export.
        :rtype: bool
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


    def _ping(self, monitoring_data_point) -> Optional[CollectionConfigurationInfo]:
        try:
            ping_response = self._client.ping(
                monitoring_data_point=monitoring_data_point,
                ikey=self._instrumentation_key,
                x_ms_qps_transmission_time=_ticks_since_dot_net_epoch()
            )
            if isinstance(ping_response, CollectionConfigurationInfo):
                pass
            else:
                # Responses that are not 200s are ignored
                return None
        except HttpResponseError as response_error:
            # Errors are not reported
            return None


class QuickpulseState(Enum):
    """Current state of quickpulse service.
    The numerical value represents the ping/post interval in ms for those states.
    """

    PING_SHORT = _SHORT_PING_INTERVAL_SECONDS
    PING_LONG = _LONG_PING_INTERVAL_SECONDS
    POST_SHORT = _SHORT_POST_INTERVAL_SECONDS
    POST_LONG = _LONG_POST_INTERVAL_SECONDS


class _QuickpulseMetricReader(PeriodicExportingMetricReader):

    def __init__(
        self,
        exporter: _QuickpulseExporter,
        base_monitoring_data_point: MonitoringDataPoint,
    ) -> None:
        self._exporter = exporter
        self._quick_pulse_state = QuickpulseState.PING_SHORT
        self._base_monitoring_data_point = base_monitoring_data_point
        self._elapsed_num_seconds = 0
        super().__init__(
            exporter=exporter,
            export_interval_millis=_SHORT_POST_INTERVAL_SECONDS * 1000,
        )

    def _ticker(self) -> None:
        if self._is_ping_state():
            # Send a ping if elapsed number of request meets the threshold
            if self._elapsed_num_seconds % int(self._quick_pulse_state.value) == 0:
                print("pinging...")
                ping_response = self._exporter._ping(
                    self._base_monitoring_data_point,
                )
                if ping_response and ping_response.response_headers:
                    if ping_response.response_headers.get("x-ms-qps-subscribed"):
                        # Switch state to post if subscribed
                        self._quick_pulse_state = QuickpulseState.POST_SHORT
                # TODO: Implement redirect
                # TODO: Implement interval hint
                else:
                    # Erroroneous responses instigate backoff logic
                    # Backoff after _LONG_PING_INTERVAL_SECONDS (60s) of no successful requests
                    if self._elapsed_num_seconds >= _LONG_PING_INTERVAL_SECONDS:
                        self._quick_pulse_state = QuickpulseState.PING_LONG
                    pass
        else:
            print("posting")
            pass

    def _is_ping_state(self):
        return self._quick_pulse_state in (QuickpulseState.PING_SHORT, QuickpulseState.PING_LONG)
    