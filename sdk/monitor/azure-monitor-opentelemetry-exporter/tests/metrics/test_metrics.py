# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import datetime
import json
import os
import platform
import shutil
import tempfile
import time
import unittest
from pathlib import Path
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
from opentelemetry.semconv.metrics.http_metrics import HTTP_SERVER_REQUEST_DURATION
from opentelemetry.semconv.metrics import MetricInstruments

from azure.core.credentials import AccessToken
from azure.core.pipeline.transport import HttpResponse, HttpTransport
from azure.monitor.opentelemetry.exporter.export._base import BaseExporter, ExportResult
from azure.monitor.opentelemetry.exporter._constants import _MULTI_ENDPOINT_ROUTING_ATTRIBUTES
from azure.monitor.opentelemetry.exporter.export.metrics._exporter import (
    AzureMonitorMetricExporter,
    _get_metric_export_result,
)
from azure.monitor.opentelemetry.exporter._generated.exporter.models import ContextTagKeys
from azure.monitor.opentelemetry.exporter._utils import azure_monitor_context


def ns_to_datetime(ns: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(ns / 1e9, tz=datetime.timezone.utc)


def throw(exc_type, *args, **kwargs):
    def func(*_args, **_kwargs):
        raise exc_type(*args, **kwargs)

    return func


# pylint: disable=import-error, too-many-public-methods
# pylint: disable=protected-access, too-many-statements
# pylint: disable=too-many-lines, unused-argument
class TestAzureMetricExporter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ.pop("APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL", None)
        os.environ.pop("APPINSIGHTS_INSTRUMENTATIONKEY", None)
        os.environ["APPINSIGHTS_INSTRUMENTATIONKEY"] = "1234abcd-5678-4efa-8abc-1234567890ab"
        os.environ["APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL"] = "true"
        cls._exporter = AzureMonitorMetricExporter()
        cls._exporter_log_analytics_disabled = AzureMonitorMetricExporter()
        cls._exporter_log_analytics_disabled._metrics_to_log_analytics = False
        cls._metrics_data = MetricsData(
            resource_metrics=[
                ResourceMetrics(
                    resource=Resource.create(attributes={"asd": "test_resource"}),
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
                                    ),
                                )
                            ],
                            schema_url="test url",
                        )
                    ],
                    schema_url="test url",
                )
            ]
        )
        cls._histogram_data_point = HistogramDataPoint(
            attributes={
                "test": "attribute",
            },
            bucket_counts=[0, 3, 4],
            count=7,
            explicit_bounds=[0, 5, 10, 0],
            max=18,
            min=1,
            start_time_unix_nano=1646865018558419456,
            time_unix_nano=1646865018558419457,
            sum=31,
        )
        cls._number_data_point = NumberDataPoint(
            attributes={
                "test": "attribute",
            },
            start_time_unix_nano=1646865018558419456,
            time_unix_nano=1646865018558419457,
            value=10,
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

    @mock.patch("azure.monitor.opentelemetry.exporter._utils._is_on_aks", return_value=False)
    def test_export_routing_attributes(self, _is_on_aks):
        attributes = {
            "microsoft.instrumentation_key": "customer-key",
            "microsoft.ingestion_endpoint": "https://example.com/",
            "microsoft.multi_endpoint_cloud_role": "customer-service",
            "microsoft.ingestion_auth": "ikey",
            "custom": "value",
            "microsoft.custom": "preserved",
        }
        point = NumberDataPoint(attributes=attributes.copy(), start_time_unix_nano=1, time_unix_nano=2, value=1)
        metric = Metric(
            name="custom",
            description="",
            unit="",
            data=Sum(
                data_points=[point], aggregation_temporality=AggregationTemporality.CUMULATIVE, is_monotonic=False
            ),
        )
        scope = ScopeMetrics(scope=InstrumentationScope("test"), metrics=[metric], schema_url="")
        data = MetricsData(
            resource_metrics=[ResourceMetrics(resource=Resource({}), scope_metrics=[scope], schema_url="")]
        )
        for routing in (False, True):
            with self.subTest(routing=routing):
                with mock.patch.dict(
                    os.environ,
                    {"APPLICATIONINSIGHTS_EXPERIMENTAL_FEATURES": "multi_endpoint_routing" if routing else ""},
                ), mock.patch("azure.monitor.opentelemetry.exporter.export._base._enabled_experimental_features", None):
                    exporter = AzureMonitorMetricExporter(disable_offline_storage=True)
                self.addCleanup(exporter.client.close)
                self.addCleanup(exporter.shutdown)
                with mock.patch.object(BaseExporter, "_transmit", return_value=ExportResult.SUCCESS) as transmit:
                    self.assertEqual(exporter.export(data), MetricExportResult.SUCCESS)
                transmit.assert_called_once()
                envelopes = transmit.call_args.args[0]
                self.assertEqual(len(envelopes), 1)
                self.assertEqual(envelopes[0].data.base_type, "MetricData")
                properties = envelopes[0].data.base_data.properties
                self.assertEqual(properties["custom"], "value")
                self.assertEqual(properties["microsoft.custom"], "preserved")
                if routing:
                    self.assertNotIn("microsoft.instrumentation_key", properties)
                    self.assertNotIn("microsoft.ingestion_endpoint", properties)
                    self.assertNotIn("microsoft.multi_endpoint_cloud_role", properties)
                    self.assertNotIn("microsoft.ingestion_auth", properties)
                else:
                    self.assertEqual(properties, attributes)
                self.assertEqual(point.attributes, attributes)

    @mock.patch("azure.monitor.opentelemetry.exporter._utils._is_on_aks", return_value=False)
    def test_export_invalid_routing_attributes(self, _is_on_aks):
        valid = {
            "microsoft.instrumentation_key": "customer-key",
            "microsoft.ingestion_endpoint": "https://example.com/",
        }
        invalid = (
            {},
            {"microsoft.instrumentation_key": "customer-key"},
            {"microsoft.ingestion_endpoint": "https://example.com/"},
            {**valid, "microsoft.instrumentation_key": " "},
            {**valid, "microsoft.instrumentation_key": 42},
            {**valid, "microsoft.ingestion_endpoint": "http://example.com/"},
            {**valid, "microsoft.ingestion_endpoint": ("https://example.com/",)},
        )
        for routing in (False, True):
            with mock.patch.dict(
                os.environ, {"APPLICATIONINSIGHTS_EXPERIMENTAL_FEATURES": "multi_endpoint_routing" if routing else ""}
            ), mock.patch("azure.monitor.opentelemetry.exporter.export._base._enabled_experimental_features", None):
                exporter = AzureMonitorMetricExporter(disable_offline_storage=True)
            self.addCleanup(exporter.client.close)
            self.addCleanup(exporter.shutdown)
            for attributes in ([valid, *invalid, valid], invalid):
                with self.subTest(routing=routing, attributes=attributes):
                    metric = Metric(
                        name="custom",
                        description="",
                        unit="",
                        data=Sum(
                            data_points=[
                                NumberDataPoint(attributes=item, start_time_unix_nano=1, time_unix_nano=2, value=index)
                                for index, item in enumerate(attributes)
                            ],
                            aggregation_temporality=AggregationTemporality.CUMULATIVE,
                            is_monotonic=False,
                        ),
                    )
                    scope = ScopeMetrics(scope=InstrumentationScope("test"), metrics=[metric], schema_url="")
                    data = MetricsData(
                        resource_metrics=[ResourceMetrics(resource=Resource({}), scope_metrics=[scope], schema_url="")]
                    )
                    with mock.patch.object(BaseExporter, "_transmit", return_value=ExportResult.SUCCESS) as transmit:
                        self.assertEqual(exporter.export(data), MetricExportResult.SUCCESS)
                    if routing and not any(item == valid for item in attributes):
                        transmit.assert_not_called()
                        continue
                    transmit.assert_called_once()
                    envelopes = transmit.call_args.args[0]
                    expected = sum(item == valid for item in attributes) if routing else len(attributes)
                    self.assertEqual(len(envelopes), expected)
                    self.assertEqual(
                        [envelope.data.base_data.metrics[0].value for envelope in envelopes],
                        [index for index, item in enumerate(attributes) if not routing or item == valid],
                    )

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
            {
                "service.name": "testServiceName",
                "service.namespace": "testServiceNamespace",
                "service.instance.id": "testServiceInstanceId",
            }
        )
        point = NumberDataPoint(
            attributes={
                "test": "attribute",
                "user_agent.synthetic.type": "bot",
            },
            start_time_unix_nano=1646865018558419456,
            time_unix_nano=1646865018558419457,
            value=10,
        )
        envelope = exporter._point_to_envelope(point, "test name", resource)

        self.assertEqual(envelope.instrumentation_key, exporter._instrumentation_key)
        self.assertIsNotNone(envelope.tags)
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_DEVICE_ID), azure_monitor_context[ContextTagKeys.AI_DEVICE_ID]
        )
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_DEVICE_LOCALE), azure_monitor_context[ContextTagKeys.AI_DEVICE_LOCALE]
        )
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_DEVICE_TYPE), azure_monitor_context[ContextTagKeys.AI_DEVICE_TYPE]
        )
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_INTERNAL_SDK_VERSION),
            azure_monitor_context[ContextTagKeys.AI_INTERNAL_SDK_VERSION],
        )
        self.assertEqual(envelope.tags.get(ContextTagKeys.AI_OPERATION_SYNTHETIC_SOURCE), "True")
        self.assertEqual(envelope.tags.get(ContextTagKeys.AI_CLOUD_ROLE), "testServiceNamespace.testServiceName")
        self.assertEqual(envelope.tags.get(ContextTagKeys.AI_CLOUD_ROLE_INSTANCE), "testServiceInstanceId")
        self.assertEqual(envelope.tags.get(ContextTagKeys.AI_INTERNAL_NODE_NAME), "testServiceInstanceId")

    def test_point_to_envelope_partA_default(self):
        exporter = self._exporter
        resource = Resource({"service.name": "testServiceName"})
        point = self._number_data_point
        envelope = exporter._point_to_envelope(point, "test name", resource)
        self.assertEqual(envelope.tags.get(ContextTagKeys.AI_CLOUD_ROLE), "testServiceName")
        self.assertEqual(envelope.tags.get(ContextTagKeys.AI_CLOUD_ROLE_INSTANCE), platform.node())
        self.assertEqual(
            envelope.tags.get(ContextTagKeys.AI_INTERNAL_NODE_NAME),
            envelope.tags.get(ContextTagKeys.AI_CLOUD_ROLE_INSTANCE),
        )

    def test_point_to_envelope_number(self):
        exporter = self._exporter
        resource = Resource.create(attributes={"asd": "test_resource"})
        scope = InstrumentationScope("test_scope")
        point = self._number_data_point
        envelope = exporter._point_to_envelope(point, "test name", resource, scope)
        self.assertEqual(envelope.instrumentation_key, exporter._instrumentation_key)
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Metric")
        self.assertEqual(envelope.time, ns_to_datetime(point.time_unix_nano))
        self.assertEqual(envelope.data.base_type, "MetricData")
        self.assertEqual(len(envelope.data.base_data.properties), 1)
        self.assertEqual(envelope.data.base_data.properties["test"], "attribute")
        self.assertEqual(len(envelope.data.base_data.metrics), 1)
        self.assertEqual(envelope.data.base_data.metrics[0].name, "test name")
        self.assertEqual(envelope.data.base_data.metrics[0].namespace, None)
        self.assertEqual(envelope.data.base_data.metrics[0].value, 10)
        self.assertEqual(envelope.data.base_data.metrics[0].count, 1)

    def test_point_to_envelope_histogram(self):
        exporter = self._exporter
        resource = Resource.create(attributes={"asd": "test_resource"})
        point = self._histogram_data_point
        envelope = exporter._point_to_envelope(point, "test name", resource)
        self.assertEqual(envelope.instrumentation_key, exporter._instrumentation_key)
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Metric")
        self.assertEqual(envelope.time, ns_to_datetime(point.time_unix_nano))
        self.assertEqual(envelope.data.base_type, "MetricData")
        self.assertEqual(len(envelope.data.base_data.properties), 1)
        self.assertEqual(envelope.data.base_data.properties["test"], "attribute")
        self.assertEqual(len(envelope.data.base_data.metrics), 1)
        self.assertEqual(envelope.data.base_data.metrics[0].name, "test name")
        self.assertEqual(envelope.data.base_data.metrics[0].value, 31)
        self.assertEqual(envelope.data.base_data.metrics[0].count, 7)

    @mock.patch.dict(
        "os.environ",
        {
            "OTEL_METRICS_EXPORTER": " foo, otlp, bar",
            "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT": "TEST_ENDPOINT",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter._utils._is_on_aks", return_value=True)
    @mock.patch(
        "azure.monitor.opentelemetry.exporter.export.metrics._exporter._utils._is_attach_enabled", return_value=True
    )
    def test_point_to_envelope_aks_amw(self, attach_mock, aks_mock):
        exporter = self._exporter
        resource = Resource.create(attributes={"asd": "test_resource"})
        scope = InstrumentationScope("test_scope")
        point = self._number_data_point
        envelope = exporter._point_to_envelope(point, "test name", resource, scope)
        self.assertEqual(len(envelope.data.base_data.properties), 2)
        self.assertEqual(envelope.data.base_data.properties["_MS.SentToAMW"], "True")

    @mock.patch.dict(
        "os.environ",
        {
            "OTEL_METRICS_EXPORTER": " foo, otlp, bar",
            "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT": "TEST_ENDPOINT",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter._utils._is_on_aks", return_value=True)
    @mock.patch(
        "azure.monitor.opentelemetry.exporter.export.metrics._exporter._utils._is_attach_enabled", return_value=True
    )
    def test_point_to_envelope_statsbeat(self, attach_mock, aks_mock):
        exporter = AzureMonitorMetricExporter(
            is_sdkstats=True,
        )
        point = self._number_data_point
        envelope = exporter._point_to_envelope(point, "attach")
        self.assertEqual(len(envelope.data.base_data.properties), 1)
        self.assertNotIn("_MS.SentToAMW", envelope.data.base_data.properties)

    @mock.patch.dict(
        "os.environ",
        {
            "OTEL_METRICS_EXPORTER": " foo ,otlp ,bar",
            "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT": "TEST_ENDPOINT",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter._utils._is_on_aks", return_value=False)
    @mock.patch(
        "azure.monitor.opentelemetry.exporter.export.metrics._exporter._utils._is_attach_enabled", return_value=True
    )
    def test_point_to_envelope_otlp_no_aks(self, attach_mock, aks_mock):
        exporter = self._exporter
        resource = Resource.create(attributes={"asd": "test_resource"})
        point = self._histogram_data_point
        envelope = exporter._point_to_envelope(point, "test name", resource)
        self.assertEqual(len(envelope.data.base_data.properties), 1)
        self.assertNotIn("_MS.SentToAMW", envelope.data.base_data.properties)

    @mock.patch.dict(
        "os.environ",
        {
            "OTEL_METRICS_EXPORTER": " foo ,otlp ,bar",
            "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT": "TEST_ENDPOINT",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter._utils._is_on_aks", return_value=True)
    @mock.patch(
        "azure.monitor.opentelemetry.exporter.export.metrics._exporter._utils._is_attach_enabled", return_value=False
    )
    def test_point_to_envelope_otlp_aks_no_attach(self, attach_mock, aks_mock):
        exporter = self._exporter
        resource = Resource.create(attributes={"asd": "test_resource"})
        point = self._histogram_data_point
        envelope = exporter._point_to_envelope(point, "test name", resource)
        self.assertEqual(len(envelope.data.base_data.properties), 1)
        self.assertNotIn("_MS.SentToAMW", envelope.data.base_data.properties)

    @mock.patch.dict(
        "os.environ",
        {
            "OTEL_METRICS_EXPORTER": " foo, bar",
            "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT": "TEST_ENDPOINT",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter._utils._is_on_aks", return_value=True)
    @mock.patch(
        "azure.monitor.opentelemetry.exporter.export.metrics._exporter._utils._is_attach_enabled", return_value=True
    )
    def test_point_to_envelope_aks_attach_no_otlp(self, attach_mock, aks_mock):
        exporter = self._exporter
        resource = Resource.create(attributes={"asd": "test_resource"})
        scope = InstrumentationScope("test_scope")
        point = self._number_data_point
        envelope = exporter._point_to_envelope(point, "test name", resource, scope)
        self.assertEqual(len(envelope.data.base_data.properties), 2)
        self.assertEqual(envelope.data.base_data.properties["_MS.SentToAMW"], "False")

    @mock.patch.dict(
        "os.environ",
        {
            "OTEL_METRICS_EXPORTER": " foo ,otlp ,bar",
        },
    )
    @mock.patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter._utils._is_on_aks", return_value=True)
    @mock.patch(
        "azure.monitor.opentelemetry.exporter.export.metrics._exporter._utils._is_attach_enabled", return_value=True
    )
    def test_point_to_envelope_aks_attach_no_endpoint(self, attach_mock, aks_mock):
        exporter = self._exporter
        resource = Resource.create(attributes={"asd": "test_resource"})
        point = self._histogram_data_point
        envelope = exporter._point_to_envelope(point, "test name", resource)
        self.assertEqual(len(envelope.data.base_data.properties), 2)
        self.assertEqual(envelope.data.base_data.properties["_MS.SentToAMW"], "False")

    @mock.patch.dict(
        "os.environ",
        {
            "APPLICATIONINSIGHTS_METRIC_NAMESPACE_OPT_IN": "True",
        },
    )
    def test_point_to_envelope_metric_namespace(self):
        exporter = self._exporter
        resource = Resource.create(attributes={"asd": "test_resource"})
        scope = InstrumentationScope("test_scope")
        point = self._number_data_point
        envelope = exporter._point_to_envelope(point, "test name", resource, scope)
        self.assertEqual(envelope.instrumentation_key, exporter._instrumentation_key)
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Metric")
        self.assertEqual(envelope.time, ns_to_datetime(point.time_unix_nano))
        self.assertEqual(envelope.data.base_type, "MetricData")
        self.assertEqual(len(envelope.data.base_data.properties), 1)
        self.assertEqual(envelope.data.base_data.properties["test"], "attribute")
        self.assertEqual(len(envelope.data.base_data.metrics), 1)
        self.assertEqual(envelope.data.base_data.metrics[0].name, "test name")
        self.assertEqual(envelope.data.base_data.metrics[0].namespace, "test_scope")
        self.assertEqual(envelope.data.base_data.metrics[0].value, 10)
        self.assertEqual(envelope.data.base_data.metrics[0].count, 1)

    def test_point_to_envelope_number_log_analytics_disabled(self):
        exporter = self._exporter_log_analytics_disabled
        resource = Resource.create(attributes={"asd": "test_resource"})
        scope = InstrumentationScope("test_scope")
        point = self._number_data_point
        envelope = exporter._point_to_envelope(point, "test name", resource, scope)
        self.assertIsNone(envelope)

    def test_point_to_envelope_histogram_log_analytics_disabled(self):
        exporter = self._exporter_log_analytics_disabled
        resource = Resource.create(attributes={"asd": "test_resource"})
        point = self._histogram_data_point
        envelope = exporter._point_to_envelope(point, "test name", resource)
        self.assertIsNone(envelope)

    @mock.patch("azure.monitor.opentelemetry.exporter.export.trace._utils._get_target_and_path_for_http_dependency")
    def test_point_to_envelope_std_metric_client_duration(self, target_mock):
        exporter = self._exporter
        resource = Resource(
            {
                "service.name": "testServiceName",
                "service.namespace": "testServiceNamespace",
                "service.instance.id": "testServiceInstanceId",
            }
        )
        point = mock.Mock(spec=NumberDataPoint)
        point.attributes = {
            "http.status_code": 200,
            "custom_attr": "custom_key",
        }
        point.start_time_unix_nano = 1646865018558419456
        point.time_unix_nano = 1646865018558419457
        point.value = 15.0
        target_mock.return_value = ("test_service", "test_path")
        envelope = exporter._point_to_envelope(point, "http.client.duration", resource)
        self.assertEqual(envelope.instrumentation_key, exporter._instrumentation_key)
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Metric")
        self.assertEqual(envelope.time, ns_to_datetime(point.time_unix_nano))
        self.assertEqual(envelope.data.base_type, "MetricData")
        self.assertEqual(envelope.data.base_data.properties["_MS.MetricId"], "dependencies/duration")
        self.assertEqual(envelope.data.base_data.properties["_MS.IsAutocollected"], "True")
        self.assertNotIn("_MS.SentToAMW", envelope.data.base_data.properties)
        self.assertEqual(envelope.data.base_data.properties["Dependency.Type"], "http")
        self.assertEqual(envelope.data.base_data.properties["Dependency.Success"], "True")
        self.assertEqual(envelope.data.base_data.properties["dependency/target"], "test_service")
        self.assertEqual(envelope.data.base_data.properties["dependency/resultCode"], "200")
        self.assertEqual(envelope.data.base_data.properties["cloud/roleInstance"], "testServiceInstanceId")
        self.assertEqual(envelope.data.base_data.properties["cloud/roleName"], "testServiceNamespace.testServiceName")
        self.assertIsNone(envelope.data.base_data.properties.get("custom_attr"))
        self.assertEqual(len(envelope.data.base_data.metrics), 1)
        self.assertEqual(envelope.data.base_data.metrics[0].name, "http.client.duration")
        self.assertEqual(envelope.data.base_data.metrics[0].value, 15.0)

        # Success/Failure
        point.attributes["http.status_code"] = 500
        envelope = exporter._point_to_envelope(point, "http.client.duration", resource)
        self.assertEqual(envelope.data.base_data.properties["Dependency.Success"], "False")

        point.attributes["http.status_code"] = None
        envelope = exporter._point_to_envelope(point, "http.client.duration", resource)
        self.assertEqual(envelope.data.base_data.properties["Dependency.Success"], "False")
        self.assertEqual(envelope.data.base_data.properties["dependency/resultCode"], "0")

        point.attributes["http.status_code"] = "None"
        envelope = exporter._point_to_envelope(point, "http.client.duration", resource)
        self.assertEqual(envelope.data.base_data.properties["Dependency.Success"], "False")
        self.assertEqual(envelope.data.base_data.properties["dependency/resultCode"], "0")

        # stable
        point.attributes = {
            "http.response.status_code": 200,
            "custom_attr": "custom_key",
        }
        envelope = exporter._point_to_envelope(point, "http.client.request.duration", resource)
        self.assertEqual(envelope.instrumentation_key, exporter._instrumentation_key)
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Metric")
        self.assertEqual(envelope.time, ns_to_datetime(point.time_unix_nano))
        self.assertEqual(envelope.data.base_type, "MetricData")
        self.assertEqual(envelope.data.base_data.properties["_MS.MetricId"], "dependencies/duration")
        self.assertEqual(envelope.data.base_data.properties["_MS.IsAutocollected"], "True")
        self.assertNotIn("_MS.SentToAMW", envelope.data.base_data.properties)
        self.assertEqual(envelope.data.base_data.properties["Dependency.Type"], "http")
        self.assertEqual(envelope.data.base_data.properties["Dependency.Success"], "True")
        self.assertEqual(envelope.data.base_data.properties["dependency/target"], "test_service")
        self.assertEqual(envelope.data.base_data.properties["dependency/resultCode"], "200")
        self.assertEqual(envelope.data.base_data.properties["cloud/roleInstance"], "testServiceInstanceId")
        self.assertEqual(envelope.data.base_data.properties["cloud/roleName"], "testServiceNamespace.testServiceName")
        self.assertIsNone(envelope.data.base_data.properties.get("custom_attr"))
        self.assertEqual(len(envelope.data.base_data.metrics), 1)
        self.assertEqual(envelope.data.base_data.metrics[0].name, "http.client.request.duration")
        self.assertEqual(envelope.data.base_data.metrics[0].value, 15.0)

    def test_point_to_envelope_std_metric_server_duration(self):
        exporter = self._exporter
        resource = Resource(
            {
                "service.name": "testServiceName",
                "service.namespace": "testServiceNamespace",
                "service.instance.id": "testServiceInstanceId",
            }
        )
        point = mock.Mock(spec=NumberDataPoint)
        point.attributes = {
            "http.status_code": 200,
            "custom_attr": "custom_key",
        }
        point.start_time_unix_nano = 1646865018558419456
        point.time_unix_nano = 1646865018558419457
        point.value = 15.0
        envelope = exporter._point_to_envelope(point, "http.server.duration", resource)
        self.assertEqual(envelope.instrumentation_key, exporter._instrumentation_key)
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Metric")
        self.assertEqual(envelope.time, ns_to_datetime(point.time_unix_nano))
        self.assertEqual(envelope.data.base_type, "MetricData")
        self.assertEqual(envelope.data.base_data.properties["_MS.MetricId"], "requests/duration")
        self.assertEqual(envelope.data.base_data.properties["_MS.IsAutocollected"], "True")
        self.assertNotIn("_MS.SentToAMW", envelope.data.base_data.properties)
        self.assertEqual(envelope.data.base_data.properties["Request.Success"], "True")
        self.assertEqual(envelope.data.base_data.properties["request/resultCode"], "200")
        self.assertEqual(envelope.data.base_data.properties["cloud/roleInstance"], "testServiceInstanceId")
        self.assertEqual(envelope.data.base_data.properties["cloud/roleName"], "testServiceNamespace.testServiceName")
        self.assertIsNone(envelope.data.base_data.properties.get("custom_attr"))
        self.assertEqual(len(envelope.data.base_data.metrics), 1)
        self.assertEqual(envelope.data.base_data.metrics[0].name, "http.server.duration")
        self.assertEqual(envelope.data.base_data.metrics[0].value, 15.0)

        # Success/Failure
        point.attributes["http.status_code"] = 500
        envelope = exporter._point_to_envelope(point, "http.server.duration", resource)
        self.assertEqual(envelope.data.base_data.properties["Request.Success"], "False")

        point.attributes["http.status_code"] = None
        envelope = exporter._point_to_envelope(point, "http.server.duration", resource)
        self.assertEqual(envelope.data.base_data.properties["Request.Success"], "False")
        self.assertEqual(envelope.data.base_data.properties.get("request/resultCode"), "0")

        point.attributes["http.status_code"] = "None"
        envelope = exporter._point_to_envelope(point, "http.server.duration", resource)
        self.assertEqual(envelope.data.base_data.properties["Request.Success"], "False")
        self.assertEqual(envelope.data.base_data.properties.get("request/resultCode"), "0")

        # Synthetic
        point.attributes["user_agent.synthetic.type"] = "bot"
        envelope = exporter._point_to_envelope(point, "http.server.duration", resource)
        self.assertEqual(envelope.data.base_data.properties["operation/synthetic"], "True")

        # Stable
        point.attributes = {
            "http.response.status_code": 200,
            "custom_attr": "custom_key",
        }
        envelope = exporter._point_to_envelope(point, "http.server.request.duration", resource)
        self.assertEqual(envelope.instrumentation_key, exporter._instrumentation_key)
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Metric")
        self.assertEqual(envelope.time, ns_to_datetime(point.time_unix_nano))
        self.assertEqual(envelope.data.base_type, "MetricData")
        self.assertEqual(envelope.data.base_data.properties["_MS.MetricId"], "requests/duration")
        self.assertEqual(envelope.data.base_data.properties["_MS.IsAutocollected"], "True")
        self.assertNotIn("_MS.SentToAMW", envelope.data.base_data.properties)
        self.assertEqual(envelope.data.base_data.properties["Request.Success"], "True")
        self.assertEqual(envelope.data.base_data.properties["request/resultCode"], "200")
        self.assertEqual(envelope.data.base_data.properties["cloud/roleInstance"], "testServiceInstanceId")
        self.assertEqual(envelope.data.base_data.properties["cloud/roleName"], "testServiceNamespace.testServiceName")
        self.assertIsNone(envelope.data.base_data.properties.get("custom_attr"))
        self.assertEqual(len(envelope.data.base_data.metrics), 1)
        self.assertEqual(envelope.data.base_data.metrics[0].name, "http.server.request.duration")
        self.assertEqual(envelope.data.base_data.metrics[0].value, 15.0)

    def test_point_to_envelope_std_metric_unsupported(self):
        exporter = self._exporter
        resource = Resource(
            {
                "service.name": "testServiceName",
                "service.namespace": "testServiceNamespace",
                "service.instance.id": "testServiceInstanceId",
            }
        )
        point = NumberDataPoint(
            attributes={
                "http.status_code": 200,
                "peer.service": "test_service",
                "custom_attr": "custom_key",
            },
            start_time_unix_nano=1646865018558419456,
            time_unix_nano=1646865018558419457,
            value=15.0,
        )
        envelope = exporter._point_to_envelope(point, "http.server.request.size", resource)
        self.assertIsNone(envelope)

    @mock.patch("azure.monitor.opentelemetry.exporter.export.trace._utils._get_target_and_path_for_http_dependency")
    def test_point_to_envelope_std_metric_client_duration_log_analytics_disabled(self, target_mock):
        exporter = self._exporter_log_analytics_disabled
        resource = Resource(
            {
                "service.name": "testServiceName",
                "service.namespace": "testServiceNamespace",
                "service.instance.id": "testServiceInstanceId",
            }
        )
        point = mock.Mock(spec=NumberDataPoint)
        point.attributes = {
            "http.status_code": 200,
            "custom_attr": "custom_key",
        }
        point.start_time_unix_nano = 1646865018558419456
        point.time_unix_nano = 1646865018558419457
        point.value = 15.0
        target_mock.return_value = ("test_service", "test_path")
        envelope = exporter._point_to_envelope(point, "http.client.duration", resource)
        self.assertEqual(envelope.instrumentation_key, exporter._instrumentation_key)
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Metric")
        self.assertEqual(envelope.time, ns_to_datetime(point.time_unix_nano))
        self.assertEqual(envelope.data.base_type, "MetricData")
        self.assertEqual(envelope.data.base_data.properties["_MS.MetricId"], "dependencies/duration")
        self.assertEqual(envelope.data.base_data.properties["_MS.IsAutocollected"], "True")
        self.assertEqual(envelope.data.base_data.properties["Dependency.Type"], "http")
        self.assertEqual(envelope.data.base_data.properties["Dependency.Success"], "True")
        self.assertEqual(envelope.data.base_data.properties["dependency/target"], "test_service")
        self.assertEqual(envelope.data.base_data.properties["dependency/resultCode"], "200")
        self.assertEqual(envelope.data.base_data.properties["cloud/roleInstance"], "testServiceInstanceId")
        self.assertEqual(envelope.data.base_data.properties["cloud/roleName"], "testServiceNamespace.testServiceName")
        self.assertIsNone(envelope.data.base_data.properties.get("custom_attr"))
        self.assertEqual(len(envelope.data.base_data.metrics), 1)
        self.assertEqual(envelope.data.base_data.metrics[0].name, "http.client.duration")
        self.assertEqual(envelope.data.base_data.metrics[0].value, 15.0)

        # Success/Failure
        point.attributes["http.status_code"] = 500
        envelope = exporter._point_to_envelope(point, "http.client.duration", resource)
        self.assertEqual(envelope.data.base_data.properties["Dependency.Success"], "False")

        point.attributes["http.status_code"] = None
        envelope = exporter._point_to_envelope(point, "http.client.duration", resource)
        self.assertEqual(envelope.data.base_data.properties["Dependency.Success"], "False")
        self.assertEqual(envelope.data.base_data.properties["dependency/resultCode"], "0")

        point.attributes["http.status_code"] = "None"
        envelope = exporter._point_to_envelope(point, "http.client.duration", resource)
        self.assertEqual(envelope.data.base_data.properties["Dependency.Success"], "False")
        self.assertEqual(envelope.data.base_data.properties["dependency/resultCode"], "0")

        # stable
        point.attributes = {
            "http.response.status_code": 200,
            "custom_attr": "custom_key",
        }
        envelope = exporter._point_to_envelope(point, "http.client.request.duration", resource)
        self.assertEqual(envelope.instrumentation_key, exporter._instrumentation_key)
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Metric")
        self.assertEqual(envelope.time, ns_to_datetime(point.time_unix_nano))
        self.assertEqual(envelope.data.base_type, "MetricData")
        self.assertEqual(envelope.data.base_data.properties["_MS.MetricId"], "dependencies/duration")
        self.assertEqual(envelope.data.base_data.properties["_MS.IsAutocollected"], "True")
        self.assertEqual(envelope.data.base_data.properties["Dependency.Type"], "http")
        self.assertEqual(envelope.data.base_data.properties["Dependency.Success"], "True")
        self.assertEqual(envelope.data.base_data.properties["dependency/target"], "test_service")
        self.assertEqual(envelope.data.base_data.properties["dependency/resultCode"], "200")
        self.assertEqual(envelope.data.base_data.properties["cloud/roleInstance"], "testServiceInstanceId")
        self.assertEqual(envelope.data.base_data.properties["cloud/roleName"], "testServiceNamespace.testServiceName")
        self.assertIsNone(envelope.data.base_data.properties.get("custom_attr"))
        self.assertEqual(len(envelope.data.base_data.metrics), 1)
        self.assertEqual(envelope.data.base_data.metrics[0].name, "http.client.request.duration")
        self.assertEqual(envelope.data.base_data.metrics[0].value, 15.0)

    def test_point_to_envelope_std_metric_server_duration_log_analytics_disabled(self):
        exporter = self._exporter_log_analytics_disabled
        resource = Resource(
            {
                "service.name": "testServiceName",
                "service.namespace": "testServiceNamespace",
                "service.instance.id": "testServiceInstanceId",
            }
        )
        point = mock.Mock(spec=NumberDataPoint)
        point.attributes = {
            "http.status_code": 200,
            "custom_attr": "custom_key",
        }
        point.start_time_unix_nano = 1646865018558419456
        point.time_unix_nano = 1646865018558419457
        point.value = 15.0
        envelope = exporter._point_to_envelope(point, "http.server.duration", resource)
        self.assertEqual(envelope.instrumentation_key, exporter._instrumentation_key)
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Metric")
        self.assertEqual(envelope.time, ns_to_datetime(point.time_unix_nano))
        self.assertEqual(envelope.data.base_type, "MetricData")
        self.assertEqual(envelope.data.base_data.properties["_MS.MetricId"], "requests/duration")
        self.assertEqual(envelope.data.base_data.properties["_MS.IsAutocollected"], "True")
        self.assertEqual(envelope.data.base_data.properties["Request.Success"], "True")
        self.assertEqual(envelope.data.base_data.properties["request/resultCode"], "200")
        self.assertEqual(envelope.data.base_data.properties["cloud/roleInstance"], "testServiceInstanceId")
        self.assertEqual(envelope.data.base_data.properties["cloud/roleName"], "testServiceNamespace.testServiceName")
        self.assertIsNone(envelope.data.base_data.properties.get("custom_attr"))
        self.assertEqual(len(envelope.data.base_data.metrics), 1)
        self.assertEqual(envelope.data.base_data.metrics[0].name, "http.server.duration")
        self.assertEqual(envelope.data.base_data.metrics[0].value, 15.0)

        # Success/Failure
        point.attributes["http.status_code"] = 500
        envelope = exporter._point_to_envelope(point, "http.server.duration", resource)
        self.assertEqual(envelope.data.base_data.properties["Request.Success"], "False")

        point.attributes["http.status_code"] = None
        envelope = exporter._point_to_envelope(point, "http.server.duration", resource)
        self.assertEqual(envelope.data.base_data.properties["Request.Success"], "False")
        self.assertEqual(envelope.data.base_data.properties.get("request/resultCode"), "0")

        point.attributes["http.status_code"] = "None"
        envelope = exporter._point_to_envelope(point, "http.server.duration", resource)
        self.assertEqual(envelope.data.base_data.properties["Request.Success"], "False")
        self.assertEqual(envelope.data.base_data.properties.get("request/resultCode"), "0")

        # Synthetic
        point.attributes["user_agent.synthetic.type"] = "bot"
        envelope = exporter._point_to_envelope(point, "http.server.duration", resource)
        self.assertEqual(envelope.data.base_data.properties["operation/synthetic"], "True")

        # Stable
        point.attributes = {
            "http.response.status_code": 200,
            "custom_attr": "custom_key",
        }
        envelope = exporter._point_to_envelope(point, "http.server.request.duration", resource)
        self.assertEqual(envelope.instrumentation_key, exporter._instrumentation_key)
        self.assertEqual(envelope.name, "Microsoft.ApplicationInsights.Metric")
        self.assertEqual(envelope.time, ns_to_datetime(point.time_unix_nano))
        self.assertEqual(envelope.data.base_type, "MetricData")
        self.assertEqual(envelope.data.base_data.properties["_MS.MetricId"], "requests/duration")
        self.assertEqual(envelope.data.base_data.properties["_MS.IsAutocollected"], "True")
        self.assertEqual(envelope.data.base_data.properties["Request.Success"], "True")
        self.assertEqual(envelope.data.base_data.properties["request/resultCode"], "200")
        self.assertEqual(envelope.data.base_data.properties["cloud/roleInstance"], "testServiceInstanceId")
        self.assertEqual(envelope.data.base_data.properties["cloud/roleName"], "testServiceNamespace.testServiceName")
        self.assertIsNone(envelope.data.base_data.properties.get("custom_attr"))
        self.assertEqual(len(envelope.data.base_data.metrics), 1)
        self.assertEqual(envelope.data.base_data.metrics[0].name, "http.server.request.duration")
        self.assertEqual(envelope.data.base_data.metrics[0].value, 15.0)

    def test_point_to_envelope_std_metric_unsupported_log_analytics_disabled(self):
        exporter = self._exporter_log_analytics_disabled
        resource = Resource(
            {
                "service.name": "testServiceName",
                "service.namespace": "testServiceNamespace",
                "service.instance.id": "testServiceInstanceId",
            }
        )
        point = NumberDataPoint(
            attributes={
                "http.status_code": 200,
                "peer.service": "test_service",
                "custom_attr": "custom_key",
            },
            start_time_unix_nano=1646865018558419456,
            time_unix_nano=1646865018558419457,
            value=15.0,
        )
        envelope = exporter._point_to_envelope(point, "http.server.request.size", resource)
        self.assertIsNone(envelope)

    def test_point_to_envelope_std_metric_log_analytics_disabled(self):
        exporter = self._exporter
        resource = Resource(
            {
                "service.name": "testServiceName",
                "service.namespace": "testServiceNamespace",
                "service.instance.id": "testServiceInstanceId",
            }
        )
        point = NumberDataPoint(
            attributes={
                "http.status_code": 200,
                "peer.service": "test_service",
                "custom_attr": "custom_key",
            },
            start_time_unix_nano=1646865018558419456,
            time_unix_nano=1646865018558419457,
            value=15.0,
        )
        envelope = exporter._point_to_envelope(point, "http.server.request.size", resource)
        self.assertIsNone(envelope)

    @mock.patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter._utils._is_on_aks", return_value=True)
    @mock.patch(
        "azure.monitor.opentelemetry.exporter.export.metrics._exporter._utils._is_attach_enabled", return_value=True
    )
    def test_constructor_log_analytics_enabled_default_aks(self, attach_mock, aks_mock):
        exporter = AzureMonitorMetricExporter()
        self.assertTrue(exporter._metrics_to_log_analytics)

    @mock.patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter._utils._is_on_aks", return_value=False)
    @mock.patch(
        "azure.monitor.opentelemetry.exporter.export.metrics._exporter._utils._is_attach_enabled", return_value=True
    )
    def test_constructor_log_analytics_enabled_default_off_aks(self, attach_mock, aks_mock):
        exporter = AzureMonitorMetricExporter()
        self.assertTrue(exporter._metrics_to_log_analytics)

    @mock.patch.dict("os.environ", {"APPLICATIONINSIGHTS_METRICS_TO_LOGANALYTICS_ENABLED": " TRUE"})
    @mock.patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter._utils._is_on_aks", return_value=True)
    @mock.patch(
        "azure.monitor.opentelemetry.exporter.export.metrics._exporter._utils._is_attach_enabled", return_value=True
    )
    def test_constructor_log_analytics_enabled_env_var(self, attach_mock, aks_mock):
        exporter = AzureMonitorMetricExporter()
        self.assertTrue(exporter._metrics_to_log_analytics)

    @mock.patch.dict("os.environ", {"APPLICATIONINSIGHTS_METRICS_TO_LOGANALYTICS_ENABLED": " false "})
    @mock.patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter._utils._is_on_aks", return_value=False)
    @mock.patch(
        "azure.monitor.opentelemetry.exporter.export.metrics._exporter._utils._is_attach_enabled", return_value=True
    )
    def test_constructor_log_analytics_disabled_env_var_off_aks(self, attach_mock, aks_mock):
        exporter = AzureMonitorMetricExporter()
        # APPLICATIONINSIGHTS_METRICS_TO_LOGANALYTICS_ENABLED is currently only specified for AKS Attach
        self.assertTrue(exporter._metrics_to_log_analytics)

    @mock.patch.dict("os.environ", {"APPLICATIONINSIGHTS_METRICS_TO_LOGANALYTICS_ENABLED": " false "})
    @mock.patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter._utils._is_on_aks", return_value=True)
    @mock.patch(
        "azure.monitor.opentelemetry.exporter.export.metrics._exporter._utils._is_attach_enabled", return_value=False
    )
    def test_constructor_log_analytics_disabled_env_var_manual_aks(self, attach_mock, aks_mock):
        exporter = AzureMonitorMetricExporter()
        # APPLICATIONINSIGHTS_METRICS_TO_LOGANALYTICS_ENABLED is currently only specified for AKS Attach
        self.assertTrue(exporter._metrics_to_log_analytics)

    @mock.patch.dict("os.environ", {"APPLICATIONINSIGHTS_METRICS_TO_LOGANALYTICS_ENABLED": " false "})
    @mock.patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter._utils._is_on_aks", return_value=True)
    @mock.patch(
        "azure.monitor.opentelemetry.exporter.export.metrics._exporter._utils._is_attach_enabled", return_value=True
    )
    def test_constructor_log_analytics_disabled_env_var(self, attach_mock, aks_mock):
        exporter = AzureMonitorMetricExporter()
        self.assertFalse(exporter._metrics_to_log_analytics)

    @mock.patch.dict("os.environ", {"APPLICATIONINSIGHTS_METRICS_TO_LOGANALYTICS_ENABLED": " false "})
    @mock.patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter._utils._is_on_aks", return_value=True)
    @mock.patch(
        "azure.monitor.opentelemetry.exporter.export.metrics._exporter._utils._is_attach_enabled", return_value=True
    )
    def test_constructor_log_analytics_statsbeat(self, attach_mock, aks_mock):
        exporter = AzureMonitorMetricExporter(
            is_sdkstats=True,
        )
        self.assertTrue(exporter._metrics_to_log_analytics)

    @mock.patch.dict("os.environ", {"APPLICATIONINSIGHTS_METRICS_TO_LOGANALYTICS_ENABLED": "falser"})
    @mock.patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter._utils._is_on_aks", return_value=True)
    @mock.patch(
        "azure.monitor.opentelemetry.exporter.export.metrics._exporter._utils._is_attach_enabled", return_value=True
    )
    def test_constructor_log_analytics_invalid_env_var(self, attach_mock, aks_mock):
        exporter = AzureMonitorMetricExporter()
        self.assertTrue(exporter._metrics_to_log_analytics)

    @mock.patch.dict("os.environ", {"APPLICATIONINSIGHTS_METRICS_TO_LOGANALYTICS_ENABLED": ""})
    @mock.patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter._utils._is_on_aks", return_value=True)
    @mock.patch(
        "azure.monitor.opentelemetry.exporter.export.metrics._exporter._utils._is_attach_enabled", return_value=True
    )
    def test_constructor_log_analytics_blank_env_var(self, attach_mock, aks_mock):
        exporter = AzureMonitorMetricExporter()
        self.assertTrue(exporter._metrics_to_log_analytics)


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
        self.assertEqual(
            _get_metric_export_result(None),
            MetricExportResult.FAILURE,
        )


class _Response(HttpResponse):
    def __init__(self, request, status_code=200, headers=None):
        super().__init__(request, None)
        self.status_code = status_code
        self.headers = {"Content-Type": "application/json", **(headers or {})}
        self.content_type = "application/json"
        count = len(json.loads(request.body))
        self._body = json.dumps({"itemsReceived": count, "itemsAccepted": count, "errors": []}).encode()

    def body(self):
        return self._body

    def json(self):
        return json.loads(self._body)


class TestMultiEndpointRouting(unittest.TestCase):
    def setUp(self):
        environment = mock.patch.dict(
            os.environ,
            {
                "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
                "APPLICATIONINSIGHTS_SDKSTATS_DISABLED": "true",
                "APPLICATIONINSIGHTS_CONTROLPLANE_DISABLED": "true",
                "APPLICATIONINSIGHTS_EXPERIMENTAL_FEATURES": "multi_endpoint_routing",
                "APPLICATIONINSIGHTS_METRIC_NAMESPACE_OPT_IN": "true",
            },
        )
        environment.start()
        self.addCleanup(environment.stop)
        features = mock.patch("azure.monitor.opentelemetry.exporter.export._base._enabled_experimental_features", None)
        features.start()
        self.addCleanup(features.stop)
        aks = mock.patch("azure.monitor.opentelemetry.exporter._utils._is_on_aks", return_value=False)
        aks.start()
        self.addCleanup(aks.stop)
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.transport = mock.MagicMock(spec=HttpTransport)
        self.transport.close.return_value = None
        self.transport.__exit__.side_effect = lambda *args: self.transport.close()
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request)

    def _exporter(self, *, routing=True, **kwargs):
        options = {
            "connection_string": "InstrumentationKey=1234abcd-5678-4efa-8abc-1234567890ab;"
            "IngestionEndpoint=https://host.example/",
            "disable_offline_storage": True,
            "storage_directory": str(Path(self.directory.name) / "host"),
            "transport": self.transport,
            "retry_total": 0,
        }
        options.update(kwargs)
        with mock.patch.dict(
            os.environ, {"APPLICATIONINSIGHTS_EXPERIMENTAL_FEATURES": "multi_endpoint_routing" if routing else ""}
        ), mock.patch("azure.monitor.opentelemetry.exporter.export._base._enabled_experimental_features", None):
            exporter = AzureMonitorMetricExporter(**options)
        self.addCleanup(exporter.client.close)
        self.addCleanup(exporter.shutdown)
        return exporter

    def _point(self, endpoint="https://one.example/proxy/", key="customer-key", auth="ikey", value=10):
        return NumberDataPoint(
            attributes={
                "microsoft.instrumentation_key": key,
                "microsoft.ingestion_endpoint": endpoint,
                "microsoft.ingestion_auth": auth,
                "microsoft.multi_endpoint_cloud_role": "not-the-resource-role",
                "custom": "point-value",
            },
            start_time_unix_nano=1,
            time_unix_nano=2,
            value=value,
        )

    def _metric(self, points, name="custom"):
        return Metric(
            name=name,
            description="",
            unit="",
            data=Sum(data_points=points, aggregation_temporality=AggregationTemporality.DELTA, is_monotonic=True),
        )

    def _data(self, *metrics, role="resource-role"):
        return MetricsData(
            resource_metrics=[
                ResourceMetrics(
                    resource=Resource({"service.name": role, "service.instance.id": "resource-instance"}),
                    scope_metrics=[
                        ScopeMetrics(scope=InstrumentationScope("test-meter"), metrics=list(metrics), schema_url="")
                    ],
                    schema_url="",
                )
            ]
        )

    def test_grouping_and_per_point_keys_across_resources(self):
        exporter = self._exporter()
        points = [self._point(key=" key-one ", value=1), self._point(endpoint="https://two.example/", value=2)]
        first = self._data(self._metric(points))
        second = self._data(
            self._metric([self._point(endpoint="HTTPS://ONE.EXAMPLE:443/proxy", key="key-three", value=3)]),
            role="another-resource",
        )
        data = MetricsData(resource_metrics=[*first.resource_metrics, *second.resource_metrics])
        self.assertEqual(exporter.export(data), MetricExportResult.SUCCESS)
        requests = [call.args[0] for call in self.transport.send.call_args_list]
        self.assertEqual(len(requests), 2)
        self.assertTrue(requests[0].url.startswith("https://one.example/proxy/"))
        self.assertTrue(requests[1].url.startswith("https://two.example/"))
        items = json.loads(requests[0].body)
        self.assertEqual([item["iKey"] for item in items], ["key-one", "key-three"])
        self.assertEqual([item["tags"]["ai.cloud.role"] for item in items], ["resource-role", "another-resource"])
        self.assertEqual([item["data"]["baseData"]["metrics"][0]["value"] for item in items], [1, 3])
        self.assertEqual(json.loads(requests[1].body)[0]["data"]["baseData"]["metrics"][0]["value"], 2)
        for request in requests:
            for item in json.loads(request.body):
                self.assertEqual(item["data"]["baseType"], "MetricData")
                self.assertEqual(item["tags"]["ai.cloud.roleInstance"], "resource-instance")
                metric = item["data"]["baseData"]["metrics"][0]
                self.assertEqual(metric["name"], "custom")
                self.assertEqual(metric["ns"], "test-meter")
                self.assertEqual(item["data"]["baseData"]["properties"], {"custom": "point-value"})
        self.assertEqual(points[0].attributes["microsoft.instrumentation_key"], " key-one ")

    def test_gauge_and_histogram_conversion_is_preserved(self):
        exporter = self._exporter()
        point = self._point()
        histogram_point = HistogramDataPoint(
            attributes=self._point(endpoint="https://two.example/", key="histogram-key").attributes,
            start_time_unix_nano=1,
            time_unix_nano=2,
            count=3,
            sum=12,
            bucket_counts=[1, 2],
            explicit_bounds=[3],
            min=2,
            max=6,
        )
        gauge = Metric(name="gauge", description="", unit="", data=Gauge(data_points=[point]))
        histogram = Metric(
            name="histogram",
            description="",
            unit="",
            data=Histogram(data_points=[histogram_point], aggregation_temporality=AggregationTemporality.DELTA),
        )
        self.assertEqual(exporter.export(self._data(gauge, histogram)), MetricExportResult.SUCCESS)
        items = [json.loads(call.args[0].body)[0] for call in self.transport.send.call_args_list]
        self.assertEqual([item["iKey"] for item in items], ["customer-key", "histogram-key"])
        gauge_data, histogram_data = [item["data"]["baseData"]["metrics"][0] for item in items]
        self.assertEqual(gauge_data["value"], 10)
        self.assertEqual(gauge_data["count"], 1)
        self.assertEqual(
            {key: histogram_data[key] for key in ("value", "count", "min", "max")},
            {"value": 12, "count": 3, "min": 2, "max": 6},
        )

    def test_single_connection_string_is_unchanged(self):
        exporter = self._exporter(routing=False)
        data = self._data(self._metric([self._point(), self._point(endpoint="https://two.example/")]))
        self.assertEqual(exporter.export(data), MetricExportResult.SUCCESS)
        self.transport.send.assert_called_once()
        request = self.transport.send.call_args.args[0]
        self.assertTrue(request.url.startswith("https://host.example/"))
        items = json.loads(request.body)
        self.assertEqual([item["iKey"] for item in items], ["1234abcd-5678-4efa-8abc-1234567890ab"] * 2)
        for attribute in _MULTI_ENDPOINT_ROUTING_ATTRIBUTES:
            self.assertIn(attribute, items[0]["data"]["baseData"]["properties"])

    def test_none_empty_and_invalid_points_do_not_transmit(self):
        exporter = self._exporter()
        for data in (
            None,
            MetricsData(resource_metrics=[]),
            self._data(self._metric([])),
            self._data(self._metric([None])),
            self._data(self._metric([self._point(key=" "), self._point(endpoint="http://invalid.example/")])),
        ):
            with self.subTest(data=data):
                self.assertEqual(exporter.export(data), MetricExportResult.SUCCESS)
        self.transport.send.assert_not_called()

    @mock.patch.dict(os.environ)
    def test_routing_without_host_connection_string(self):
        os.environ.pop("APPLICATIONINSIGHTS_CONNECTION_STRING", None)
        os.environ.pop("APPINSIGHTS_INSTRUMENTATIONKEY", None)
        exporter = self._exporter(connection_string=None)
        self.assertIsNone(exporter._instrumentation_key)
        os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"] = "invalid"
        self.assertEqual(exporter.export(self._data(self._metric([self._point()]))), MetricExportResult.SUCCESS)
        request = self.transport.send.call_args.args[0]
        self.assertTrue(request.url.startswith("https://one.example/proxy/"))
        self.assertEqual(json.loads(request.body)[0]["iKey"], "customer-key")

    def test_existing_metric_filters_are_preserved(self):
        exporter = self._exporter()
        exporter._metrics_to_log_analytics = False
        data = self._data(
            self._metric([self._point()], name="custom"),
            self._metric([self._point()], name=MetricInstruments.HTTP_SERVER_ACTIVE_REQUESTS),
            self._metric([self._point()], name=HTTP_SERVER_REQUEST_DURATION),
        )
        self.assertEqual(exporter.export(data), MetricExportResult.SUCCESS)
        self.transport.send.assert_called_once()
        items = json.loads(self.transport.send.call_args.args[0].body)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["iKey"], "customer-key")
        properties = items[0]["data"]["baseData"]["properties"]
        self.assertEqual(properties["_MS.MetricId"], "requests/duration")
        self.assertEqual(properties["cloud/roleName"], "resource-role")
        for attribute in _MULTI_ENDPOINT_ROUTING_ATTRIBUTES:
            self.assertNotIn(attribute, properties)

    def test_resource_and_scope_routes_are_not_used_as_fallbacks(self):
        exporter = self._exporter()
        route = self._point().attributes
        point = NumberDataPoint(attributes={"custom": "value"}, start_time_unix_nano=1, time_unix_nano=2, value=1)
        data = MetricsData(
            resource_metrics=[
                ResourceMetrics(
                    resource=Resource(route),
                    scope_metrics=[
                        ScopeMetrics(
                            scope=InstrumentationScope("test-meter", attributes=route),
                            metrics=[self._metric([point])],
                            schema_url="",
                        )
                    ],
                    schema_url="",
                )
            ]
        )
        self.assertEqual(exporter.export(data), MetricExportResult.SUCCESS)
        self.transport.send.assert_not_called()

    def test_authentication_groups_and_client_reuse(self):
        credential = mock.Mock(spec=["get_token"])
        credential.get_token.return_value = AccessToken("test-token", int(time.time()) + 3600)
        exporter = self._exporter(credential=credential)
        data = self._data(self._metric([self._point(), self._point(auth=" AAD ")]))
        for _ in range(2):
            self.assertEqual(exporter.export(data), MetricExportResult.SUCCESS)
        requests = [call.args[0] for call in self.transport.send.call_args_list]
        self.assertEqual(len(requests), 4)
        for request in requests[::2]:
            self.assertNotIn("Authorization", request.headers)
        for request in requests[1::2]:
            self.assertEqual(request.headers["Authorization"], f"Bearer {credential.get_token.return_value.token}")
        credential.get_token.assert_called_once()

    def test_missing_aad_credential_does_not_block_other_routes(self):
        exporter = self._exporter(credential=None)
        data = self._data(self._metric([self._point(auth="aad"), self._point(endpoint="https://two.example/")]))
        with self.assertLogs("azure.monitor.opentelemetry.exporter.export._base", level="ERROR"):
            self.assertEqual(exporter.export(data), MetricExportResult.FAILURE)
        self.transport.send.assert_called_once()
        self.assertTrue(self.transport.send.call_args.args[0].url.startswith("https://two.example/"))

    def test_retry_storage_preserves_point_keys_and_values(self):
        now = datetime.datetime(2026, 10, 20, tzinfo=datetime.timezone.utc)
        exporter = self._exporter(disable_offline_storage=False)
        self.transport.send.side_effect = lambda request, **kwargs: _Response(
            request, 429 if request.url.startswith("https://one.example/") else 200, {"Retry-After": "60"}
        )
        data = self._data(
            self._metric([self._point(key="old-key", value=1), self._point(endpoint="https://two.example/")])
        )
        with mock.patch("azure.monitor.opentelemetry.exporter._storage._now", return_value=now):
            self.assertEqual(exporter.export(data), MetricExportResult.FAILURE)
        self.assertEqual(self.transport.send.call_count, 2)
        exporter.shutdown()
        restarted = self._exporter(disable_offline_storage=False)
        self.transport.send.reset_mock()
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request)
        with mock.patch(
            "azure.monitor.opentelemetry.exporter._storage._now", return_value=now + datetime.timedelta(seconds=61)
        ):
            self.assertEqual(
                restarted.export(self._data(self._metric([self._point(key="new-key", value=2)]))),
                MetricExportResult.SUCCESS,
            )
        requests = [call.args[0] for call in self.transport.send.call_args_list]
        self.assertEqual(len(requests), 2)
        items = [json.loads(request.body)[0] for request in requests]
        self.assertEqual([item["iKey"] for item in items], ["new-key", "old-key"])
        self.assertEqual([item["data"]["baseData"]["metrics"][0]["value"] for item in items], [2, 1])
        self.assertTrue(all(request.url.startswith("https://one.example/proxy/") for request in requests))
        self.assertFalse(list((Path(self.directory.name) / "host").iterdir()))

    def test_shutdown_closes_routes_and_rejects_later_exports(self):
        exporter = self._exporter(disable_offline_storage=False)
        data = self._data(self._metric([self._point()]))
        self.assertEqual(exporter.export(data), MetricExportResult.SUCCESS)
        exporter.shutdown()
        closes = self.transport.close.call_count
        self.assertEqual(closes, 2)
        exporter.shutdown()
        self.assertEqual(self.transport.close.call_count, closes)
        self.transport.send.reset_mock()
        with self.assertLogs("azure.monitor.opentelemetry.exporter.export._base", level="ERROR"):
            self.assertEqual(exporter.export(data), MetricExportResult.FAILURE)
        self.transport.send.assert_not_called()

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.time.monotonic", return_value=100)
    def test_backoff_defers_metric_points(self, clock):
        exporter = self._exporter(disable_offline_storage=False)
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request, 429, {"Retry-After": "60"})
        data = self._data(self._metric([self._point()]))
        self.assertEqual(exporter.export(data), MetricExportResult.FAILURE)
        self.transport.send.reset_mock()
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request)
        self.assertEqual(exporter.export(data), MetricExportResult.FAILURE)
        self.transport.send.assert_not_called()
        clock.return_value = 160
        self.assertEqual(exporter.export(data), MetricExportResult.SUCCESS)
        self.transport.send.assert_called_once()

    def test_routed_transmission_exception_is_reported(self):
        exporter = self._exporter()
        with mock.patch.object(exporter, "_transmit_routed", side_effect=RuntimeError("test failure")):
            with self.assertLogs(
                "azure.monitor.opentelemetry.exporter.export.metrics._exporter", level="ERROR"
            ) as logs:
                result = exporter.export(self._data(self._metric([self._point()])))
        self.assertEqual(result, MetricExportResult.FAILURE)
        self.assertIn("test failure", logs.output[0])

    @mock.patch("azure.monitor.opentelemetry.exporter.export._base.time.monotonic", return_value=100)
    def test_background_retry_sends_metric_without_new_exports(self, clock):
        now = datetime.datetime(2026, 10, 20, tzinfo=datetime.timezone.utc)
        exporter = self._exporter(disable_offline_storage=False)
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request, 429, {"Retry-After": "60"})
        with mock.patch("azure.monitor.opentelemetry.exporter._storage._now", return_value=now):
            data = self._data(self._metric([self._point(key="original", value=42)]))
            self.assertEqual(exporter.export(data), MetricExportResult.FAILURE)
        self.transport.send.reset_mock()
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request)
        clock.return_value = 161
        with mock.patch(
            "azure.monitor.opentelemetry.exporter._storage._now", return_value=now + datetime.timedelta(seconds=61)
        ):
            exporter._route_retry_task.function()
        self.transport.send.assert_called_once()
        item = json.loads(self.transport.send.call_args.args[0].body)[0]
        self.assertEqual(item["iKey"], "original")
        self.assertEqual(item["data"]["baseData"]["metrics"][0]["value"], 42)
