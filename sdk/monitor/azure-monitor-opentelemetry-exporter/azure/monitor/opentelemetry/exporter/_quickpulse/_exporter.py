# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import logging
from typing import Any, Optional
import weakref

from opentelemetry.context import (
    _SUPPRESS_INSTRUMENTATION_KEY,
    attach,
    detach,
    set_value,
)
from opentelemetry.sdk.metrics import (
    Counter,
    Histogram,
)
from opentelemetry.sdk.metrics._internal.point import MetricsData
from opentelemetry.sdk.metrics.export import (
    AggregationTemporality,
    MetricExporter,
    MetricExportResult,
    MetricsData as OTMetricsData,
    MetricReader,
)

from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.policies import ContentDecodePolicy
from azure.monitor.opentelemetry.exporter._quickpulse._constants import (
    _LONG_PING_INTERVAL_SECONDS,
    _POST_CANCEL_INTERVAL_SECONDS,
    _POST_INTERVAL_SECONDS,
    _QUICKPULSE_SUBSCRIBED_HEADER_NAME,
)
from azure.monitor.opentelemetry.exporter._quickpulse._generated._configuration import QuickpulseClientConfiguration
from azure.monitor.opentelemetry.exporter._quickpulse._generated._client import QuickpulseClient
from azure.monitor.opentelemetry.exporter._quickpulse._generated.models import MonitoringDataPoint
from azure.monitor.opentelemetry.exporter._quickpulse._policy import _QuickpulseRedirectPolicy
from azure.monitor.opentelemetry.exporter._quickpulse._state import (
    _get_global_quickpulse_state,
    _is_ping_state,
    _set_global_quickpulse_state,
    _get_and_clear_quickpulse_documents,
    _QuickpulseState,
)
from azure.monitor.opentelemetry.exporter._quickpulse._utils import (
    _metric_to_quick_pulse_data_points,
)
from azure.monitor.opentelemetry.exporter._connection_string_parser import ConnectionStringParser
from azure.monitor.opentelemetry.exporter._utils import _ticks_since_dot_net_epoch, PeriodicTask


_logger = logging.getLogger(__name__)


_QUICKPULSE_METRIC_TEMPORALITIES = {
    # Use DELTA temporalities because we want to reset the counts every collection interval
    Counter: AggregationTemporality.DELTA,
    Histogram: AggregationTemporality.DELTA,
}


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
        # Pass `None` for now until swagger definition is fixed
        config = QuickpulseClientConfiguration(credential=None)  # type: ignore
        qp_redirect_policy = _QuickpulseRedirectPolicy(permit_redirects=False)
        policies = [
            # Custom redirect policy for QP
            qp_redirect_policy,
            # Needed for serialization
            ContentDecodePolicy(),
            # Logging for client calls
            config.http_logging_policy,
            # TODO: Support AADaudience (scope)/credentials
            config.authentication_policy,
            # Explicitly disabling to avoid tracing live metrics calls
            # DistributedTracingPolicy(),
        ]
        self._client = QuickpulseClient(
            credential=None, # type: ignore
            endpoint=self._live_endpoint,
            policies=policies
        )
        # Create a weakref of the client to the redirect policy so the endpoint can be
        # dynamically modified if redirect does occur
        qp_redirect_policy._qp_client_ref = weakref.ref(self._client)

        MetricExporter.__init__(
            self,
            preferred_temporality=_QUICKPULSE_METRIC_TEMPORALITIES, # type: ignore
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
            documents=_get_and_clear_quickpulse_documents(),
        )

        token = attach(set_value(_SUPPRESS_INSTRUMENTATION_KEY, True))
        try:
            post_response = self._client.publish(  # type: ignore
                endpoint=self._live_endpoint,
                monitoring_data_points=data_points,
                ikey=self._instrumentation_key,
                transmission_time=_ticks_since_dot_net_epoch(),
                cls=_Response,
            )
            if not post_response:
                # If no response, assume unsuccessful
                result = MetricExportResult.FAILURE
            else:
                header = post_response._response_headers.get(_QUICKPULSE_SUBSCRIBED_HEADER_NAME)  # pylint: disable=protected-access
                if header != "true":
                    # User leaving the live metrics page will be treated as an unsuccessful
                    result = MetricExportResult.FAILURE
        except Exception:  # pylint: disable=broad-except,invalid-name
            _logger.exception("Exception occurred while publishing live metrics.")
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


    def _ping(self, monitoring_data_point: MonitoringDataPoint) -> Optional[_Response]:
        ping_response = None
        token = attach(set_value(_SUPPRESS_INSTRUMENTATION_KEY, True))
        try:
            ping_response = self._client.is_subscribed(  # type: ignore
                endpoint=self._live_endpoint,
                monitoring_data_point=monitoring_data_point,
                ikey=self._instrumentation_key,
                transmission_time=_ticks_since_dot_net_epoch(),
                machine_name=monitoring_data_point.machine_name,
                instance_name=monitoring_data_point.instance,
                stream_id=monitoring_data_point.stream_id,
                role_name=monitoring_data_point.role_name,
                invariant_version=monitoring_data_point.invariant_version,
                cls=_Response,
            )
            return ping_response  # type: ignore
        except HttpResponseError:
            _logger.exception("Exception occurred while pinging live metrics.")
        detach(token)
        return ping_response


class _QuickpulseMetricReader(MetricReader):

    def __init__(
        self,
        exporter: _QuickpulseExporter,
        base_monitoring_data_point: MonitoringDataPoint,
    ) -> None:
        self._exporter = exporter
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
        if _is_ping_state():
            # Send a ping if elapsed number of request meets the threshold
            if self._elapsed_num_seconds % _get_global_quickpulse_state().value == 0:
                ping_response = self._exporter._ping(  # pylint: disable=protected-access
                    self._base_monitoring_data_point,
                )
                if ping_response:
                    header = ping_response._response_headers.get(_QUICKPULSE_SUBSCRIBED_HEADER_NAME)  # pylint: disable=protected-access
                    if header and header == "true":
                        # Switch state to post if subscribed
                        _set_global_quickpulse_state(_QuickpulseState.POST_SHORT)
                        self._elapsed_num_seconds = 0
                    else:
                        # Backoff after _LONG_PING_INTERVAL_SECONDS (60s) of no successful requests
                        if _get_global_quickpulse_state() is _QuickpulseState.PING_SHORT and \
                            self._elapsed_num_seconds >= _LONG_PING_INTERVAL_SECONDS:
                            _set_global_quickpulse_state(_QuickpulseState.PING_LONG)
                # TODO: Implement redirect
                else:
                    # Erroneous ping responses instigate backoff logic
                    # Backoff after _LONG_PING_INTERVAL_SECONDS (60s) of no successful requests
                    if _get_global_quickpulse_state() is _QuickpulseState.PING_SHORT and \
                        self._elapsed_num_seconds >= _LONG_PING_INTERVAL_SECONDS:
                        _set_global_quickpulse_state(_QuickpulseState.PING_LONG)
        else:
            try:
                self.collect()
            except _UnsuccessfulQuickPulsePostError:
                # Unsuccessful posts instigate backoff logic
                # Backoff after _POST_CANCEL_INTERVAL_SECONDS (20s) of no successful requests
                # And resume pinging
                if self._elapsed_num_seconds >= _POST_CANCEL_INTERVAL_SECONDS:
                    _set_global_quickpulse_state(_QuickpulseState.PING_SHORT)
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
        )
        if result is MetricExportResult.FAILURE:
            # There is currently no way to propagate unsuccessful metric post so
            # we raise an _UnsuccessfulQuickPulsePostError exception. MUST handle
            # this exception whenever `collect()` is called
            raise _UnsuccessfulQuickPulsePostError()

    def shutdown(self, timeout_millis: float = 30_000, **kwargs) -> None:
        self._worker.cancel()
        self._worker.join()
