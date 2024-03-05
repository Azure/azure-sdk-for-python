# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from datetime import datetime, timezone
from enum import Enum
from typing import Any, List, Optional

from opentelemetry.context import (
    _SUPPRESS_INSTRUMENTATION_KEY,
    attach,
    detach,
    set_value,
)
from opentelemetry.sdk.metrics import (
    Counter,
    Histogram,
    ObservableCounter,
    ObservableGauge,
    ObservableUpDownCounter,
    UpDownCounter,
)
from opentelemetry.sdk.metrics._internal.point import (
    NumberDataPoint,
    HistogramDataPoint,
    MetricsData,
)
from opentelemetry.sdk.metrics.export import (
    AggregationTemporality,
    MetricExporter,
    MetricExportResult,
    MetricsData as OTMetricsData,
    MetricReader,
)

from azure.core.exceptions import HttpResponseError
from azure.monitor.opentelemetry.exporter._quickpulse._constants import _QUICKPULSE_METRIC_NAME_MAPPINGS
from azure.monitor.opentelemetry.exporter._quickpulse._generated._client import QuickpulseClient
from azure.monitor.opentelemetry.exporter._quickpulse._generated.models import (
    DocumentIngress,
    MetricPoint,
    MonitoringDataPoint,
)
from azure.monitor.opentelemetry.exporter._connection_string_parser import ConnectionStringParser
from azure.monitor.opentelemetry.exporter._utils import _ticks_since_dot_net_epoch, PeriodicTask


_APPLICATION_INSIGHTS_METRIC_TEMPORALITIES = {
    Counter: AggregationTemporality.DELTA,
    Histogram: AggregationTemporality.DELTA,
    ObservableCounter: AggregationTemporality.DELTA,
    ObservableGauge: AggregationTemporality.CUMULATIVE,
    ObservableUpDownCounter: AggregationTemporality.CUMULATIVE,
    UpDownCounter: AggregationTemporality.CUMULATIVE,
}

_SHORT_PING_INTERVAL_SECONDS = 5
_POST_INTERVAL_SECONDS = 1
_LONG_PING_INTERVAL_SECONDS = 60
_POST_CANCEL_INTERVAL_SECONDS = 20


class _Response:
    """Response that encapsulates pipeline response and response headers from
    QuickPulse client.
    """
    def __init__(self, pipeline_response, deserialized, response_headers):
        self._pipeline_response = pipeline_response
        self._deserialized = deserialized
        self._response_headers = response_headers


class _UnsuccessfulQuickPulsePostError(Exception):
    """Exception raised to indicate unsuccessful QuickPulse post for backoff logic."""


class _QuickpulseExporter(MetricExporter):

    def __init__(self, connection_string: Optional[str]) -> None:
        """Metric exporter for Quickpulse.

        :param str connection_string: The connection string used for your Application Insights resource.
        :rtype: None
        """
        parsed_connection_string = ConnectionStringParser(connection_string)

        self._live_endpoint = parsed_connection_string.live_endpoint
        self._instrumentation_key = parsed_connection_string.instrumentation_key
        # TODO: Support AADaudience (scope)/credentials

        self._client = QuickpulseClient(host=self._live_endpoint)
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
        :type metrics_data: ~opentelemetry.sdk.metrics._internal.point.MetricsData
        :param timeout_millis: The maximum amount of time to wait for each export. Not currently used.
        :type timeout_millis: float
        :return: The result of the export.
        :rtype: ~opentelemetry.sdk.metrics.export.MetricExportResult
        """
        result = MetricExportResult.SUCCESS
        base_monitoring_data_point = kwargs.get("base_monitoring_data_point")
        if base_monitoring_data_point is None:
            return MetricExportResult.FAILURE
        data_points = _metric_to_quick_pulse_data_points(
            metrics_data,
            base_monitoring_data_point=base_monitoring_data_point,
            documents=kwargs.get("documents"),
        )

        token = attach(set_value(_SUPPRESS_INSTRUMENTATION_KEY, True))
        try:
            post_response = self._client.post(  # type: ignore
                monitoring_data_points=data_points,
                ikey=self._instrumentation_key,
                x_ms_qps_transmission_time=_ticks_since_dot_net_epoch(),
                cls=_Response,
            )
            if not post_response:
                # If no response, assume unsuccessful
                result = MetricExportResult.FAILURE
            else:
                header = post_response._response_headers.get("x-ms-qps-subscribed")  # pylint: disable=protected-access
                if header != "true":
                    # User leaving the live metrics page will be treated as an unsuccessful
                    result = MetricExportResult.FAILURE
        except Exception:  # pylint: disable=broad-except,invalid-name
            # Errors are not reported and assumed as unsuccessful
            result = MetricExportResult.FAILURE
        finally:
            detach(token)
        return result

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


    def _ping(self, monitoring_data_point) -> Optional[_Response]:
        ping_response = None
        token = attach(set_value(_SUPPRESS_INSTRUMENTATION_KEY, True))
        try:
            ping_response = self._client.ping(  # type: ignore
                monitoring_data_point=monitoring_data_point,
                ikey=self._instrumentation_key,
                x_ms_qps_transmission_time=_ticks_since_dot_net_epoch(),
                cls=_Response,
            )
            return ping_response  # type: ignore
        except HttpResponseError:
            # Errors are not reported
            pass
        detach(token)
        return ping_response


class _QuickpulseState(Enum):
    """Current state of quickpulse service.
    The numerical value represents the ping/post interval in ms for those states.
    """

    PING_SHORT = _SHORT_PING_INTERVAL_SECONDS
    PING_LONG = _LONG_PING_INTERVAL_SECONDS
    POST_SHORT = _POST_INTERVAL_SECONDS


class _QuickpulseMetricReader(MetricReader):

    def __init__(
        self,
        exporter: _QuickpulseExporter,
        base_monitoring_data_point: MonitoringDataPoint,
    ) -> None:
        self._exporter = exporter
        self._quick_pulse_state = _QuickpulseState.PING_SHORT
        self._base_monitoring_data_point = base_monitoring_data_point
        self._elapsed_num_seconds = 0
        self._worker = PeriodicTask(
            interval=_POST_INTERVAL_SECONDS,
            function=self._ticker,
            name="QuickpulseMetricReader",
        )
        self._worker.daemon = True
        super().__init__(
            preferred_temporality=self._exporter._preferred_temporality,
            preferred_aggregation=self._exporter._preferred_aggregation,
        )
        self._worker.start()

    def _ticker(self) -> None:
        if self._is_ping_state():
            # Send a ping if elapsed number of request meets the threshold
            if self._elapsed_num_seconds % int(self._quick_pulse_state.value) == 0:
                print("pinging...")
                ping_response = self._exporter._ping(  # pylint: disable=protected-access
                    self._base_monitoring_data_point,
                )
                if ping_response:
                    header = ping_response._response_headers.get("x-ms-qps-subscribed")  # pylint: disable=protected-access
                    if header and header == "true":
                        print("ping succeeded: switching to post")
                        # Switch state to post if subscribed
                        self._quick_pulse_state = _QuickpulseState.POST_SHORT
                        self._elapsed_num_seconds = 0
                    else:
                        # Backoff after _LONG_PING_INTERVAL_SECONDS (60s) of no successful requests
                        if self._quick_pulse_state is _QuickpulseState.PING_SHORT and \
                            self._elapsed_num_seconds >= _LONG_PING_INTERVAL_SECONDS:
                            print("ping failed for 60s, switching to pinging every 60s")
                            self._quick_pulse_state = _QuickpulseState.PING_LONG
                # TODO: Implement redirect
                else:
                    # Erroneous ping responses instigate backoff logic
                    # Backoff after _LONG_PING_INTERVAL_SECONDS (60s) of no successful requests
                    if self._quick_pulse_state is _QuickpulseState.PING_SHORT and \
                        self._elapsed_num_seconds >= _LONG_PING_INTERVAL_SECONDS:
                        print("ping failed for 60s, switching to pinging every 60s")
                        self._quick_pulse_state = _QuickpulseState.PING_LONG
        else:
            print("posting...")
            try:
                self.collect()
            except _UnsuccessfulQuickPulsePostError:
                # Unsuccessful posts instigate backoff logic
                # Backoff after _POST_CANCEL_INTERVAL_SECONDS (20s) of no successful requests
                # And resume pinging
                if self._elapsed_num_seconds >= _POST_CANCEL_INTERVAL_SECONDS:
                    print("post failed for 20s, switching to pinging")
                    self._quick_pulse_state = _QuickpulseState.PING_SHORT
                    self._elapsed_num_seconds = 0

        self._elapsed_num_seconds += 1

    def _receive_metrics(
        self,
        metrics_data: MetricsData,
        timeout_millis: float = 10_000,
        **kwargs,
    ) -> None:
        result = self._exporter.export(
            metrics_data,
            timeout_millis=timeout_millis,
            base_monitoring_data_point=self._base_monitoring_data_point,
            documents=[],
        )
        if result is MetricExportResult.FAILURE:
            # There is currently no way to propagate unsuccessful metric post so
            # we raise an _UnsuccessfulQuickPulsePostError exception. MUST handle
            # this exception whenever `collect()` is called
            raise _UnsuccessfulQuickPulsePostError()

    def shutdown(self, timeout_millis: float = 30_000, **kwargs) -> None:
        self._worker.cancel()
        self._worker.join()

    def _is_ping_state(self):
        return self._quick_pulse_state in (_QuickpulseState.PING_SHORT, _QuickpulseState.PING_LONG)

def _metric_to_quick_pulse_data_points(  # pylint: disable=too-many-nested-blocks
    metrics_data: OTMetricsData,
    base_monitoring_data_point: MonitoringDataPoint,
    documents: Optional[List[DocumentIngress]],
) -> List[MonitoringDataPoint]:
    metric_points = []
    for resource_metric in metrics_data.resource_metrics:
        for scope_metric in resource_metric.scope_metrics:
            for metric in scope_metric.metrics:
                for point in metric.data.data_points:
                    if point is not None:
                        metric_point = MetricPoint(
                            name=_QUICKPULSE_METRIC_NAME_MAPPINGS[metric.name.lower()],
                            weight=1,
                        )
                        if isinstance(point, HistogramDataPoint):
                            metric_point.value = point.sum
                        elif isinstance(point, NumberDataPoint):
                            metric_point.value = point.value
                        else:
                            metric_point.value = 0
                        metric_points.append(metric_point)
    return [
        MonitoringDataPoint(
            version=base_monitoring_data_point.version,
            instance=base_monitoring_data_point.instance,
            role_name=base_monitoring_data_point.role_name,
            machine_name=base_monitoring_data_point.machine_name,
            stream_id=base_monitoring_data_point.stream_id,
            timestamp=datetime.now(tz=timezone.utc),
            metrics=metric_points,
            documents=documents,
        )
    ]
