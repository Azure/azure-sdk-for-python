# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import unittest
from unittest import mock

from opentelemetry.sdk.metrics.export import (
    AggregationTemporality,
    Metric,
    MetricExportResult,
    MetricsData as OTMetricsData,
    NumberDataPoint,
    ResourceMetrics,
    ScopeMetrics,
    Sum,
)
from opentelemetry.sdk.util.instrumentation import InstrumentationScope
from opentelemetry.sdk.resources import Resource, ResourceAttributes
from azure.core.exceptions import HttpResponseError
from azure.monitor.opentelemetry.exporter._quickpulse._generated._client import QuickpulseClient
from azure.monitor.opentelemetry.exporter._quickpulse._generated.models import MonitoringDataPoint
from azure.monitor.opentelemetry.exporter._quickpulse._exporter import (
    _POST_INTERVAL_SECONDS,
    _QuickpulseExporter,
    _QuickpulseMetricReader,
    _QuickpulseState,
    _Response,
    _UnsuccessfulQuickPulsePostError,
)
from azure.monitor.opentelemetry.exporter._quickpulse._state import (
    _get_global_quickpulse_state,
    _set_global_quickpulse_state,
    _QuickpulseState,
)


def throw(exc_type, *args, **kwargs):
    def func(*_args, **_kwargs):
        raise exc_type(*args, **kwargs)

    return func


class TestQuickpulse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _set_global_quickpulse_state(_QuickpulseState.PING_SHORT)
        cls._resource = Resource.create(
            {
                ResourceAttributes.SERVICE_INSTANCE_ID: "test_instance",
                ResourceAttributes.SERVICE_NAME: "test_service",
            }
        )
        cls._metrics_data = OTMetricsData(
            resource_metrics=ResourceMetrics(
                resource=cls._resource,
                scope_metrics=ScopeMetrics(
                    scope=InstrumentationScope("test_scope"),
                    metrics=[
                        Metric(
                            name="azureMonitor.memoryCommittedBytes",
                            description="test_desc",
                            unit="test_unit",
                            data=Sum(
                                data_points=[
                                    NumberDataPoint(
                                        attributes={},
                                        start_time_unix_nano=0,
                                        time_unix_nano=0,
                                        value=5,
                                    )
                                ],
                                aggregation_temporality=AggregationTemporality.DELTA,
                                is_monotonic=True,
                            )
                        )
                    ],
                    schema_url="test_url",
                ),
                schema_url="test_url",
            )
        )
        cls._data_point = MonitoringDataPoint(
            version="test_version",
            invariant_version=1,
            instance="test_instance",
            role_name="test_role_name",
            machine_name="test_machine_name",
            stream_id="test_stream_id",
            is_web_app=False,
            performance_collection_supported=True,
        )
        cls._exporter = _QuickpulseExporter(
            "InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ac;LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/"
        )
        cls._reader = _QuickpulseMetricReader(
            cls._exporter,
            cls._data_point,
        )


    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._generated._client.QuickpulseClient")
    def test_init(self, client_mock):
        exporter = _QuickpulseExporter(
            connection_string="InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab;LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/"
        )
        self.assertEqual(exporter._live_endpoint, "https://eastus.livediagnostics.monitor.azure.com/")
        self.assertEqual(exporter._instrumentation_key, "4321abcd-5678-4efa-8abc-1234567890ab")
        self.assertTrue(isinstance(exporter._client, QuickpulseClient))


    def test_export_missing_data_point(self):
        result = self._exporter.export(OTMetricsData(resource_metrics=[]))
        self.assertEqual(result, MetricExportResult.FAILURE)


    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._generated._client.QuickpulseClient.publish")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._exporter._metric_to_quick_pulse_data_points")
    def test_export_subscribed_false(self, convert_mock, post_mock):
        post_response = _Response(
            mock.Mock(),
            None,
            {
                "x-ms-qps-subscribed": "false",
            }
        )
        convert_mock.return_value = [self._data_point]
        post_mock.return_value = post_response
        result = self._exporter.export(
            self._metrics_data,
            base_monitoring_data_point=self._data_point
        )
        self.assertEqual(result, MetricExportResult.FAILURE)

    
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._generated._client.QuickpulseClient.publish")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._exporter._metric_to_quick_pulse_data_points")
    def test_export_subscribed_none(self, convert_mock, post_mock):
        post_response = None
        convert_mock.return_value = [self._data_point]
        post_mock.return_value = post_response
        result = self._exporter.export(
            self._metrics_data,
            base_monitoring_data_point=self._data_point
        )
        self.assertEqual(result, MetricExportResult.FAILURE)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._exporter._metric_to_quick_pulse_data_points")
    def test_export_exception(self, convert_mock):
        post_response = _Response(
            mock.Mock(),
            None,
            {},
        )
        convert_mock.return_value = [self._data_point]
        with mock.patch(
            "azure.monitor.opentelemetry.exporter._quickpulse._generated._client.QuickpulseClient.publish",
            throw(Exception),
        ):  # noqa: E501
            result = self._exporter.export(
                self._metrics_data,
                base_monitoring_data_point=self._data_point
            )
            self.assertEqual(result, MetricExportResult.FAILURE)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._generated._client.QuickpulseClient.publish")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._exporter._metric_to_quick_pulse_data_points")
    def test_export_subscribed_true(self, convert_mock, post_mock):
        post_response = _Response(
            mock.Mock(),
            None,
            {
                "x-ms-qps-subscribed": "true",
            }
        )
        convert_mock.return_value = [self._data_point]
        post_mock.return_value = post_response
        result = self._exporter.export(
            self._metrics_data,
            base_monitoring_data_point=self._data_point
        )
        self.assertEqual(result, MetricExportResult.SUCCESS)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._generated._client.QuickpulseClient.is_subscribed")
    def test_ping(self, ping_mock):
        ping_response = _Response(
            mock.Mock(),
            None,
            {
                "x-ms-qps-subscribed": "false",
            }
        )
        ping_mock.return_value = ping_response
        response = self._exporter._ping(
            monitoring_data_point=self._data_point
        )
        self.assertEqual(response, ping_response)

    def test_ping_exception(self):
        with mock.patch(
            "azure.monitor.opentelemetry.exporter._quickpulse._generated._client.QuickpulseClient.is_subscribed",
            throw(HttpResponseError),
        ):  # noqa: E501
            response = self._exporter._ping(
                monitoring_data_point=self._data_point
            )
            self.assertIsNone(response)


    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._exporter.PeriodicTask")
    def test_quickpulsereader_init(self, task_mock):
        task_inst_mock = mock.Mock()
        task_mock.return_value = task_inst_mock
        reader = _QuickpulseMetricReader(
            self._exporter,
            self._data_point,
        )
        self.assertEqual(reader._exporter, self._exporter)
        self.assertEqual(_get_global_quickpulse_state(), _QuickpulseState.PING_SHORT)
        self.assertEqual(reader._base_monitoring_data_point, self._data_point)
        self.assertEqual(reader._elapsed_num_seconds, 0)
        self.assertEqual(reader._worker, task_inst_mock)
        task_mock.assert_called_with(
            interval=_POST_INTERVAL_SECONDS,
            function=reader._ticker,
            name="QuickpulseMetricReader",
        )
        self.assertTrue(reader._worker.daemon)
        task_inst_mock.start.assert_called_once()

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._exporter._QuickpulseExporter._ping")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._exporter.PeriodicTask")
    def test_quickpulsereader_ticker_ping_true(self, task_mock, ping_mock):
        task_inst_mock = mock.Mock()
        task_mock.return_value = task_inst_mock
        reader = _QuickpulseMetricReader(
            self._exporter,
            self._data_point,
        )
        _set_global_quickpulse_state(_QuickpulseState.PING_SHORT)
        reader._elapsed_num_seconds = _QuickpulseState.PING_SHORT.value
        ping_mock.return_value = _Response(
            None,
            None,
            {
                "x-ms-qps-subscribed": "true"
            }
        )
        reader._ticker()
        ping_mock.assert_called_once_with(
            self._data_point,
        )
        self.assertEqual(_get_global_quickpulse_state(), _QuickpulseState.POST_SHORT)
        self.assertEqual(reader._elapsed_num_seconds, 1)

    # TODO: Other ticker cases

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._exporter._QuickpulseExporter.export")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._exporter.PeriodicTask")
    def test_quickpulsereader_receive_metrics(self, task_mock, export_mock):
        task_inst_mock = mock.Mock()
        task_mock.return_value = task_inst_mock
        reader = _QuickpulseMetricReader(
            self._exporter,
            self._data_point,
        )
        export_mock.return_value = MetricExportResult.SUCCESS
        reader._receive_metrics(
            self._metrics_data,
            20_000,
        )
        export_mock.assert_called_once_with(
            self._metrics_data,
            timeout_millis=20_000,
            base_monitoring_data_point=self._data_point,
        )

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._exporter._QuickpulseExporter.export")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._exporter.PeriodicTask")
    def test_quickpulsereader_receive_metrics_exception(self, task_mock, export_mock):
        task_inst_mock = mock.Mock()
        task_mock.return_value = task_inst_mock
        reader = _QuickpulseMetricReader(
            self._exporter,
            self._data_point,
        )
        export_mock.return_value = MetricExportResult.FAILURE
        with self.assertRaises(_UnsuccessfulQuickPulsePostError):
            reader._receive_metrics(
                self._metrics_data,
                20_000,
            )
            export_mock.assert_called_once_with(
                self._metrics_data,
                timeout_millis=20_000,
                base_monitoring_data_point=self._data_point,
                documents=[],
            )
