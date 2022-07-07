# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import os
import platform
import shutil
import unittest
from unittest import mock

# pylint: disable=import-error
from opentelemetry.sdk.util.instrumentation import InstrumentationScope
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.metrics.export import (
    AggregationTemporality,
    Gauge,
    Histogram,
    HistogramDataPoint,
    Metric,
    MetricExportResult,
    MetricsData,
    NumberDataPoint,
    ResourceMetrics,
    ScopeMetrics,
    Sum,
)

from azure.monitor.opentelemetry.exporter.export._base import ExportResult
from azure.monitor.opentelemetry.exporter.export.metrics._exporter import (
    AzureMonitorMetricExporter,
    _get_metric_export_result,
)
from azure.monitor.opentelemetry.exporter._utils import (
    azure_monitor_context,
    ns_to_iso_str,
)


def throw(exc_type, *args, **kwargs):
    def func(*_args, **_kwargs):
        raise exc_type(*args, **kwargs)

    return func


# pylint: disable=import-error
# pylint: disable=protected-access
# pylint: disable=too-many-lines
class TestAzureMetricExporter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ.clear()
        os.environ[
            "APPINSIGHTS_INSTRUMENTATIONKEY"
        ] = "1234abcd-5678-4efa-8abc-1234567890ab"
        cls._exporter = AzureMonitorMetricExporter()
        cls._metrics_data = MetricsData(
            resource_metrics=[
                ResourceMetrics(
                    resource = Resource.create(
                        attributes={"asd":"test_resource"}
                    ),
                    scope_metrics=[
                        ScopeMetrics(
                            scope=InstrumentationScope("test_name"),
                            metrics=[
                                Metric(
                                    name="test name",
                                    description="test description",
                                    unit="ms",
                                    data=Sum(
                                        data_points=[
                                            NumberDataPoint(
                                                attributes={
                                                    "test": "attribute",
                                                },
                                                start_time_unix_nano=1646865018558419456,
                                                time_unix_nano=1646865018558419457,
                                                value=10,
                                            )
                                        ],
                                        aggregation_temporality=AggregationTemporality.CUMULATIVE,
                                        is_monotonic=False,
                                    )
                                )
                            ],
                            schema_url="test url",
                        )
                    ],
                    schema_url="test url",
                )
            ]
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._exporter.storage._path, True)

    def test_constructor(self):
        """Test the constructor."""
        exporter = AzureMonitorMetricExporter(
            connection_string="InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab",
        )
        self.assertEqual(
            exporter._instrumentation_key,
            "4321abcd-5678-4efa-8abc-1234567890ab",
        )

    def test_from_connection_string(self):
        exporter = AzureMonitorMetricExporter.from_connection_string(
            "InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab"
        )
        self.assertTrue(isinstance(exporter, AzureMonitorMetricExporter))
        self.assertEqual(
            exporter._instrumentation_key,
            "4321abcd-5678-4efa-8abc-1234567890ab",
        )

    def test_export_none(self):
        exporter = self._exporter
        result = exporter.export(None)
        self.assertEqual(result, MetricExportResult.SUCCESS)

    def test_export_failure(self):
        exporter = self._exporter
        with mock.patch(
            "azure.monitor.opentelemetry.exporter.AzureMonitorMetricExporter._transmit"
        ) as transmit:  # noqa: E501
            transmit.return_value = ExportResult.FAILED_RETRYABLE
            storage_mock = mock.Mock()
            exporter.storage.put = storage_mock
            result = exporter.export(self._metrics_data)
        self.assertEqual(result, MetricExportResult.FAILURE)
        self.assertEqual(storage_mock.call_count, 1)

    def test_export_success(self):
        exporter = self._exporter
        with mock.patch(
            "azure.monitor.opentelemetry.exporter.AzureMonitorMetricExporter._transmit"
        ) as transmit:  # noqa: E501
            transmit.return_value = ExportResult.SUCCESS
            storage_mock = mock.Mock()
            exporter._transmit_from_storage = storage_mock
            result = exporter.export(self._metrics_data)
            self.assertEqual(result, MetricExportResult.SUCCESS)
            self.assertEqual(storage_mock.call_count, 1)

    @mock.patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter._logger")
    def test_export_exception(self, logger_mock):
        exporter = self._exporter
        with mock.patch(
            "azure.monitor.opentelemetry.exporter.AzureMonitorMetricExporter._transmit",
            throw(Exception),
        ):  # noqa: E501
            result = exporter.export(self._metrics_data)
            self.assertEqual(result, MetricExportResult.FAILURE)
            self.assertEqual(logger_mock.exception.called, True)

    def test_export_not_retryable(self):
        exporter = self._exporter
        with mock.patch(
            "azure.monitor.opentelemetry.exporter.AzureMonitorMetricExporter._transmit"
        ) as transmit:  # noqa: E501
            transmit.return_value = ExportResult.FAILED_NOT_RETRYABLE
            result = exporter.export(self._metrics_data)
            self.assertEqual(result, MetricExportResult.FAILURE)

    def test_point_to_envelope_partA(self):
        exporter = self._exporter
        resource = Resource(
            {"service.name": "testServiceName",
             "service.namespace": "testServiceNamespace",
             "service.instance.id": "testServiceInstanceId"})
        point=NumberDataPoint(
            attributes={
                "test": "attribute",
            },
            start_time_unix_nano=1646865018558419456,
            time_unix_nano=1646865018558419457,
            value=10,
        )
        envelope = exporter._point_to_envelope(point, "test name", resource)

        self.assertEqual(envelope.instrumentation_key,
                         "1234abcd-5678-4efa-8abc-1234567890ab")
        self.assertIsNotNone(envelope.tags)
        self.assertEqual(envelope.tags.get("ai.device.id"), azure_monitor_context["ai.device.id"])
        self.assertEqual(envelope.tags.get("ai.device.locale"), azure_monitor_context["ai.device.locale"])
        self.assertEqual(envelope.tags.get("ai.device.osVersion"), azure_monitor_context["ai.device.osVersion"])
        self.assertEqual(envelope.tags.get("ai.device.type"), azure_monitor_context["ai.device.type"])
        self.assertEqual(envelope.tags.get("ai.internal.sdkVersion"), azure_monitor_context["ai.internal.sdkVersion"])

        self.assertEqual(envelope.tags.get("ai.cloud.role"), "testServiceNamespace.testServiceName")
        self.assertEqual(envelope.tags.get("ai.cloud.roleInstance"), "testServiceInstanceId")
        self.assertEqual(envelope.tags.get("ai.internal.nodeName"), "testServiceInstanceId")

    def test_point_to_envelope_partA_default(self):
        exporter = self._exporter
        resource = Resource(
            {"service.name": "testServiceName"})
        point=NumberDataPoint(
            attributes={
                "test": "attribute",
            },
            start_time_unix_nano=1646865018558419456,
            time_unix_nano=1646865018558419457,
            value=10,
        )
        envelope = exporter._point_to_envelope(point, "test name", resource)
        self.assertEqual(envelope.tags.get("ai.cloud.role"), "testServiceName")
        self.assertEqual(envelope.tags.get("ai.cloud.roleInstance"), platform.node())
        self.assertEqual(envelope.tags.get("ai.internal.nodeName"), envelope.tags.get("ai.cloud.roleInstance"))

    def test_point_to_envelope_number(self):
        exporter = self._exporter
        resource = Resource.create(attributes={"asd":"test_resource"})
        scope = InstrumentationScope("test_scope"),
        point=NumberDataPoint(
            attributes={
                "test": "attribute",
            },
            start_time_unix_nano=1646865018558419456,
            time_unix_nano=1646865018558419457,
            value=10,
        )
        envelope = exporter._point_to_envelope(point, "test name", resource, scope)
        self.assertEqual(envelope.name, 'Microsoft.ApplicationInsights.Metric')
        self.assertEqual(envelope.time, ns_to_iso_str(point.time_unix_nano))
        self.assertEqual(envelope.data.base_type, 'MetricData')
        self.assertEqual(len(envelope.data.base_data.properties), 1)
        self.assertEqual(envelope.data.base_data.properties['test'], 'attribute')
        self.assertEqual(len(envelope.data.base_data.metrics), 1)
        self.assertEqual(envelope.data.base_data.metrics[0].name, "test name")
        self.assertEqual(envelope.data.base_data.metrics[0].value, 10)
        self.assertEqual(envelope.data.base_data.metrics[0].data_point_type, "Aggregation")
        self.assertEqual(envelope.data.base_data.metrics[0].count, 1)

    def test_point_to_envelope_histogram(self):
        exporter = self._exporter
        resource = Resource.create(attributes={"asd":"test_resource"})
        scope = InstrumentationScope("test_scope"),
        point=HistogramDataPoint(
            attributes={
                "test": "attribute",
            },
            bucket_counts=[0,3,4],
            count=7,
            explicit_bounds=[0,5,10,0],
            max=18,
            min=1,
            start_time_unix_nano=1646865018558419456,
            time_unix_nano=1646865018558419457,
            sum=31,
        )
        envelope = exporter._point_to_envelope(point, "test name", resource, scope)
        self.assertEqual(envelope.name, 'Microsoft.ApplicationInsights.Metric')
        self.assertEqual(envelope.time, ns_to_iso_str(point.time_unix_nano))
        self.assertEqual(envelope.data.base_type, 'MetricData')
        self.assertEqual(len(envelope.data.base_data.properties), 1)
        self.assertEqual(envelope.data.base_data.properties['test'], 'attribute')
        self.assertEqual(len(envelope.data.base_data.metrics), 1)
        self.assertEqual(envelope.data.base_data.metrics[0].name, "test name")
        self.assertEqual(envelope.data.base_data.metrics[0].value, 31)
        self.assertEqual(envelope.data.base_data.metrics[0].data_point_type, "Aggregation")
        self.assertEqual(envelope.data.base_data.metrics[0].count, 7)

class TestAzureMetricExporterUtils(unittest.TestCase):
    def test_get_metric_export_result(self):
        self.assertEqual(
            _get_metric_export_result(ExportResult.SUCCESS),
            MetricExportResult.SUCCESS,
        )
        self.assertEqual(
            _get_metric_export_result(ExportResult.FAILED_NOT_RETRYABLE),
            MetricExportResult.FAILURE,
        )
        self.assertEqual(
            _get_metric_export_result(ExportResult.FAILED_RETRYABLE),
            MetricExportResult.FAILURE,
        )
        self.assertEqual(_get_metric_export_result(None), None)
