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
from azure.monitor.opentelemetry.exporter._generated.models import ContextTagKeys
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
        self.assertEqual(envelope.time, ns_to_iso_str(point.time_unix_nano))
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
        self.assertEqual(envelope.time, ns_to_iso_str(point.time_unix_nano))
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
        self.assertEqual(envelope.time, ns_to_iso_str(point.time_unix_nano))
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
        self.assertEqual(envelope.time, ns_to_iso_str(point.time_unix_nano))
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
        self.assertEqual(envelope.time, ns_to_iso_str(point.time_unix_nano))
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
        self.assertEqual(envelope.time, ns_to_iso_str(point.time_unix_nano))
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
        self.assertEqual(envelope.time, ns_to_iso_str(point.time_unix_nano))
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
        self.assertEqual(envelope.time, ns_to_iso_str(point.time_unix_nano))
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
        self.assertEqual(envelope.time, ns_to_iso_str(point.time_unix_nano))
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
        self.assertEqual(envelope.time, ns_to_iso_str(point.time_unix_nano))
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
        self.assertEqual(envelope.time, ns_to_iso_str(point.time_unix_nano))
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
