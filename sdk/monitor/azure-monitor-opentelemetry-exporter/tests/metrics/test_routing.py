# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import datetime
import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from azure.core.credentials import AccessToken
from azure.core.pipeline.transport import HttpResponse, HttpTransport
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
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.util.instrumentation import InstrumentationScope
from opentelemetry.semconv.metrics.http_metrics import HTTP_SERVER_REQUEST_DURATION
from opentelemetry.semconv.metrics import MetricInstruments

from azure.monitor.opentelemetry.exporter import AzureMonitorMetricExporter
from azure.monitor.opentelemetry.exporter._constants import _MULTI_ENDPOINT_ROUTING_ATTRIBUTES


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


class TestMetricRouting(unittest.TestCase):
    def setUp(self):
        environment = mock.patch.dict(
            os.environ,
            {
                "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
                "APPLICATIONINSIGHTS_SDKSTATS_DISABLED": "true",
                "APPLICATIONINSIGHTS_CONTROLPLANE_DISABLED": "true",
                "APPLICATIONINSIGHTS_METRIC_NAMESPACE_OPT_IN": "true",
            },
        )
        environment.start()
        self.addCleanup(environment.stop)
        aks = mock.patch("azure.monitor.opentelemetry.exporter._utils._is_on_aks", return_value=False)
        aks.start()
        self.addCleanup(aks.stop)
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.transport = mock.MagicMock(spec=HttpTransport)
        self.transport.close.return_value = None
        self.transport.__exit__.side_effect = lambda *args: self.transport.close()
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request)

    def _exporter(self, **kwargs):
        options = {
            "connection_string": "InstrumentationKey=1234abcd-5678-4efa-8abc-1234567890ab;"
            "IngestionEndpoint=https://host.example/",
            "enable_multi_endpoint_routing": True,
            "disable_offline_storage": True,
            "storage_directory": str(Path(self.directory.name) / "host"),
            "transport": self.transport,
            "retry_total": 0,
        }
        options.update(kwargs)
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
        exporter = self._exporter(enable_multi_endpoint_routing=False)
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

    def test_routed_transmission_exception_is_reported(self):
        exporter = self._exporter()
        with mock.patch.object(exporter, "_transmit_routed", side_effect=RuntimeError("test failure")):
            with self.assertLogs(
                "azure.monitor.opentelemetry.exporter.export.metrics._exporter", level="ERROR"
            ) as logs:
                result = exporter.export(self._data(self._metric([self._point()])))
        self.assertEqual(result, MetricExportResult.FAILURE)
        self.assertIn("test failure", logs.output[0])
