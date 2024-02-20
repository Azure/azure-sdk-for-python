# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import unittest
from unittest import mock

from opentelemetry.sdk.metrics.export import (
    AggregationTemporality,
    Histogram,
    MetricExporter,
    Metric,
    MetricExportResult,
    MetricsData as OTMetricsData,
    MetricReader,
    NumberDataPoint,
    ResourceMetrics,
    ScopeMetrics,
    Sum,
)
from opentelemetry.sdk.util.instrumentation import InstrumentationScope
from opentelemetry.sdk.resources import Resource, ResourceAttributes
from azure.monitor.opentelemetry.exporter._quickpulse._generated._client import QuickpulseClient
from azure.monitor.opentelemetry.exporter._quickpulse._generated.models import MonitoringDataPoint
from azure.monitor.opentelemetry.exporter._quickpulse._exporter import (
    _metric_to_quick_pulse_data_points,
    _QuickpulseExporter,
    _QuickpulseMetricReader,
    _Response,
)


def throw(exc_type, *args, **kwargs):
    def func(*_args, **_kwargs):
        raise exc_type(*args, **kwargs)

    return func


class TestQuickpulseExporter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
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
        )
        cls._exporter = _QuickpulseExporter(
            "InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ac;LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/"
        )

    # @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._generated._client.QuickpulseClient.__new__")
    # def test_init(self, client_mock):
    #     client_inst_mock = mock.Mock()
    #     client_mock.return_value = client_inst_mock
    #     exporter = _QuickpulseExporter(
    #         connection_string="InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab;LiveEndpoint=https://eastus.livediagnostics.monitor.azure.com/"
    #     )
        
    #     self.assertEqual(exporter._live_endpoint, "https://eastus.livediagnostics.monitor.azure.com/")
    #     self.assertEqual(exporter._instrumentation_key, "4321abcd-5678-4efa-8abc-1234567890ab")
    #     self.assertEqual(exporter._client, client_inst_mock)
    #     client_mock.assert_called_with(
    #         QuickpulseClient,
    #         host="https://eastus.livediagnostics.monitor.azure.com/"
    #     )


    # def test_export_missing_data_point(self):
    #     result = self._exporter.export(OTMetricsData(resource_metrics=[]))
    #     self.assertEqual(result, MetricExportResult.FAILURE)


    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._generated._client.QuickpulseClient.post")
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

    
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._generated._client.QuickpulseClient.post")
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

    # @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._exporter._metric_to_quick_pulse_data_points")
    # def test_export_exception(self, convert_mock):
    #     post_response = _Response(
    #         mock.Mock(),
    #         None,
    #         {},
    #     )
    #     convert_mock.return_value = [self._data_point]
    #     with mock.patch(
    #         "azure.monitor.opentelemetry.exporter._quickpulse._generated._client.QuickpulseClient.post",
    #         throw(Exception),
    #     ):  # noqa: E501
    #         result = self._exporter.export(
    #             self._metrics_data,
    #             base_monitoring_data_point=self._data_point
    #         )
    #         self.assertEqual(result, MetricExportResult.FAILURE)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._generated._client.QuickpulseClient.post")
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
