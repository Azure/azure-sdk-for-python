# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import json
import os
import unittest
from dataclasses import FrozenInstanceError
from types import MappingProxyType
from unittest import mock

from opentelemetry._logs.severity import SeverityNumber
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import ALWAYS_ON
from opentelemetry.trace import SpanKind

from azure.core.pipeline.transport import HttpResponse, HttpTransport
from azure.monitor.opentelemetry.exporter import (
    AzureMonitorLogExporter,
    AzureMonitorMetricExporter,
    AzureMonitorTraceExporter,
    _utils,
)
from azure.monitor.opentelemetry.exporter._constants import _MULTI_ENDPOINT_ROUTING_ATTRIBUTES
from azure.monitor.opentelemetry.exporter._routing import (
    _get_cloud_role,
    _get_ingestion_endpoint,
    _get_instrumentation_key,
    _get_route,
    _is_aad_route,
    _is_valid_route,
)
from azure.monitor.opentelemetry.exporter.export.logs._exporter import _is_ignored_attribute
from azure.monitor.opentelemetry.exporter.export.trace._exporter import _is_standard_attribute


class TestRouting(unittest.TestCase):
    def test_route_validation(self):
        attributes = {
            "microsoft.instrumentation_key": "customer-key",
            "microsoft.ingestion_endpoint": "https://example.com/",
        }
        self.assertTrue(_is_valid_route(attributes))
        for invalid in (
            None,
            {},
            {**attributes, "microsoft.ingestion_endpoint": "http://example.com/"},
            {"microsoft.instrumentation_key": "secret-key" * 100},
            {
                "microsoft.instrumentation_key": "secret-key",
                "microsoft.ingestion_endpoint": "https://user:password@example.com/?token=secret",
                "secret-attribute": "private-telemetry",
            },
        ):
            with self.subTest(attributes=invalid):
                with self.assertLogs("azure.monitor.opentelemetry.exporter._routing", level="DEBUG") as logs:
                    self.assertFalse(_is_valid_route(invalid))
                self.assertEqual(len(logs.output), 1)
                self.assertEqual(logs.records[0].levelname, "DEBUG")
                self.assertIsNone(logs.records[0].exc_info)
                for secret in ("secret-key", "password", "example.com", "private-telemetry"):
                    self.assertNotIn(secret, logs.output[0])

    def test_instrumentation_key(self):
        for value, expected in (
            ("customer-key", "customer-key"),
            (" \tCUSTOMER-KEY\n", "CUSTOMER-KEY"),
            ("k" * 200, "k" * 200),
            (" " * 99 + "k" + " " * 100, "k"),
        ):
            with self.subTest(value=value):
                self.assertEqual(_get_instrumentation_key({"microsoft.instrumentation_key": value}), expected)

    def test_missing_instrumentation_key(self):
        for attributes in (None, {}, {"unrelated": "customer-key"}):
            with self.subTest(attributes=attributes):
                with self.assertRaisesRegex(ValueError, "Routing instrumentation key must be a nonempty string"):
                    _get_instrumentation_key(attributes)

    def test_invalid_instrumentation_key(self):
        for value in (None, "", " \t\n", 42, True, ("customer-key",), b"customer-key"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "Routing instrumentation key must be a nonempty string"):
                    _get_instrumentation_key({"microsoft.instrumentation_key": value})

    def test_instrumentation_key_length_before_trimming(self):
        for value in ("k" * 201, " " + "k" * 200, " " * 201):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "Routing instrumentation key must not exceed 200 characters"):
                    _get_instrumentation_key({"microsoft.instrumentation_key": value})


class TestIngestionEndpoint(unittest.TestCase):
    def test_normalize_endpoint(self):
        for value, expected in (
            ("HTTPS://Example.COM.:443", "https://example.com/"),
            ("https://gateway.example:8443/ingest///", "https://gateway.example:8443/ingest/"),
            ("https://localhost:9000/", "https://localhost:9000/"),
            ("https://dc.applicationinsights.azure.cn/", "https://dc.applicationinsights.azure.cn/"),
            ("https://[2001:0DB8:0:0:0:0:0:1]:443/", "https://[2001:db8::1]/"),
            ("https://[::1]:8443/", "https://[::1]:8443/"),
            ("https://b\u00fccher.example/", "https://b\u00fccher.example/"),
            ("https://fa\u00df.de/", "https://fa\u00df.de/"),
            ("https://xn--fa-hia.de/", "https://xn--fa-hia.de/"),
            ("https://example\u3002com/", "https://example\u3002com/"),
            (" https://example.com/ ", "https://example.com/"),
        ):
            with self.subTest(value=value):
                self.assertEqual(_get_ingestion_endpoint({"microsoft.ingestion_endpoint": value}), expected)
                self.assertEqual(_get_ingestion_endpoint({"microsoft.ingestion_endpoint": expected}), expected)

    def test_missing_or_non_string_endpoint(self):
        for attributes in (None, {}, {"unrelated": "https://example.com/"}):
            with self.subTest(attributes=attributes):
                with self.assertRaisesRegex(ValueError, "Routing ingestion endpoint must be a nonempty string"):
                    _get_ingestion_endpoint(attributes)
        for value in (None, "", " \t\n", 42, True, ("https://example.com/",), b"https://example.com/"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "Routing ingestion endpoint must be a nonempty string"):
                    _get_ingestion_endpoint({"microsoft.ingestion_endpoint": value})

    def test_invalid_endpoint(self):
        for value in (
            "/relative",
            "not-a-uri",
            "http://example.com/",
            "ftp://example.com/",
            "https:///path",
            "https://user:password@example.com/",
            "https://@example.com/",
            "https://example.com/?a=b",
            "https://example.com/?",
            "https://example.com/#fragment",
            "https://example.com/#",
            "https://example.com:invalid/",
            "https://example.com:65536/",
            "https://example.com:/",
            "https://exa\nmple.com/",
            "https://example.com/\x00",
            "https://example.com\\other/",
            "https://[::1",
            "https://[::1]extra:8443/",
            "https://bad host/",
            "https://%65xample.com/",
            "https://./",
            "https://bad!host/",
        ):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "Routing ingestion endpoint"):
                    _get_ingestion_endpoint({"microsoft.ingestion_endpoint": value})

    def test_endpoint_length_before_trimming(self):
        prefix = "https://example.com/"
        endpoint = prefix + "a" * (2048 - len(prefix))
        self.assertEqual(_get_ingestion_endpoint({"microsoft.ingestion_endpoint": endpoint}), endpoint + "/")
        for value in (endpoint + "a", " " + endpoint):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "Routing ingestion endpoint must not exceed 2048 characters"):
                    _get_ingestion_endpoint({"microsoft.ingestion_endpoint": value})

    def test_invalid_endpoint_does_not_expose_credentials(self):
        endpoint = "https://user:password@example.com/?token=secret"
        with self.assertRaises(ValueError) as raised:
            _get_ingestion_endpoint({"microsoft.ingestion_endpoint": endpoint})
        self.assertNotIn(endpoint, str(raised.exception))
        self.assertTrue(raised.exception.__suppress_context__)

    def test_unicode_host_spelling_is_preserved_for_transport(self):
        for host in ("B\u00dcCHER.Example", "\u039f\u03a3.example", "e\u0301.example", "xn--\u00fc.example"):
            with self.subTest(host=host):
                endpoint = f"https://{host}/"
                self.assertEqual(_get_ingestion_endpoint({"microsoft.ingestion_endpoint": endpoint}), endpoint)


class TestRoutingMetadata(unittest.TestCase):
    def test_cloud_role(self):
        for value, expected in (
            ("Customer-Service", "Customer-Service"),
            (" \tCustomer Service\n", "Customer Service"),
            ("\u2003Service-\u00c9\u2003", "Service-\u00c9"),
        ):
            with self.subTest(value=value):
                attributes = MappingProxyType({"microsoft.multi_endpoint_cloud_role": value})
                self.assertEqual(_get_cloud_role(attributes), expected)

    def test_invalid_cloud_role_uses_unknown_service(self):
        for value in (None, "", " \t\n", 42, True, ("customer-service",), b"customer-service"):
            with self.subTest(value=value):
                self.assertEqual(_get_cloud_role({"microsoft.multi_endpoint_cloud_role": value}), "unknown_service")

    def test_missing_routing_metadata(self):
        for attributes in (None, {}, {"service.name": "host-service"}):
            with self.subTest(attributes=attributes):
                self.assertEqual(_get_cloud_role(attributes), "unknown_service")
                self.assertFalse(_is_aad_route(attributes))

    def test_aad_route(self):
        for value in ("aad", "AAD", "AaD", " \taAd\n", "\u2003aad\u2003"):
            with self.subTest(value=value):
                attributes = MappingProxyType({"microsoft.ingestion_auth": value})
                self.assertTrue(_is_aad_route(attributes))

    def test_other_auth_values_use_instrumentation_key_only(self):
        for value in (None, "", " \t\n", "ikey", "bearer", "aad-token", "a ad", 42, True, ("aad",), b"aad"):
            with self.subTest(value=value):
                self.assertFalse(_is_aad_route({"microsoft.ingestion_auth": value}))


class TestRoute(unittest.TestCase):
    def setUp(self):
        self.attributes = {
            "microsoft.instrumentation_key": "customer-key",
            "microsoft.ingestion_endpoint": "https://example.com/",
        }

    def test_route(self):
        attributes = MappingProxyType(
            {
                "microsoft.instrumentation_key": " customer-key ",
                "microsoft.ingestion_endpoint": " HTTPS://Example.COM.:443/ingest/// ",
                "microsoft.multi_endpoint_cloud_role": " Customer-Service ",
                "microsoft.ingestion_auth": " AaD ",
            }
        )
        route = _get_route(attributes)
        self.assertEqual(route.instrumentation_key, "customer-key")
        self.assertEqual(route.ingestion_endpoint, "https://example.com/ingest/")
        self.assertEqual(route.cloud_role, "Customer-Service")
        self.assertIs(route.is_aad, True)

    def test_optional_defaults(self):
        route = _get_route(self.attributes)
        self.assertEqual(route.cloud_role, "unknown_service")
        self.assertIs(route.is_aad, False)

    def test_invalid_required_attributes_raise(self):
        for attributes in (
            None,
            {},
            {"microsoft.instrumentation_key": "customer-key"},
            {"microsoft.ingestion_endpoint": "https://example.com/"},
            {**self.attributes, "microsoft.instrumentation_key": 42},
            {**self.attributes, "microsoft.ingestion_endpoint": "http://example.com/"},
        ):
            with self.subTest(attributes=attributes):
                with self.assertRaisesRegex(ValueError, "Routing "):
                    _get_route(attributes)

    def test_transport_key(self):
        key = ("https://example.com/", False)
        self.assertEqual(_get_route(self.attributes).transport_key, key)
        for changes, expected in (
            ({"microsoft.instrumentation_key": "other-key"}, key),
            ({"microsoft.multi_endpoint_cloud_role": "Other-Service"}, key),
            ({"microsoft.ingestion_endpoint": "HTTPS://EXAMPLE.COM.:443///"}, key),
            ({"microsoft.ingestion_auth": "aad"}, ("https://example.com/", True)),
            ({"microsoft.ingestion_endpoint": "https://other.example/"}, ("https://other.example/", False)),
        ):
            with self.subTest(changes=changes):
                self.assertEqual(_get_route({**self.attributes, **changes}).transport_key, expected)

    def test_route_is_an_immutable_snapshot(self):
        route = _get_route(self.attributes)
        self.attributes["microsoft.instrumentation_key"] = "changed-key"
        self.assertEqual(route.instrumentation_key, "customer-key")
        with self.assertRaises(FrozenInstanceError):
            route.instrumentation_key = "changed-key"


class TestRoutingProperties(unittest.TestCase):
    def setUp(self):
        self.attributes = {
            "microsoft.instrumentation_key": "customer-key",
            "microsoft.ingestion_endpoint": "https://example.com/",
            "microsoft.multi_endpoint_cloud_role": "customer-service",
            "microsoft.ingestion_auth": "ikey",
            "custom": "value",
            "microsoft.custom": "preserved",
        }
        self.custom_properties = {"custom": "value", "microsoft.custom": "preserved"}

    def test_custom_properties(self):
        attributes = {**self.attributes, "microsoft.custom_measurements": '{"count": 1}'}
        route = _get_route(attributes)
        for predicate in (_is_ignored_attribute, _is_standard_attribute):
            for routing in (False, True):
                with self.subTest(predicate=predicate.__name__, routing=routing):
                    properties = _utils._filter_custom_properties(
                        attributes,
                        lambda key, val: not predicate(key, exclude_routing_attributes=routing),
                    )
                    self.assertEqual(properties, self.custom_properties if routing else self.attributes)
                    self.assertEqual(_get_route(attributes), route)
        properties = _utils._filter_custom_properties(
            attributes,
            lambda key, val: key != "custom" and not _is_ignored_attribute(key, exclude_routing_attributes=True),
        )
        self.assertEqual(properties, {"microsoft.custom": "preserved"})
        for attributes in (None, {}):
            self.assertEqual(_utils._filter_custom_properties(attributes), {})


class _IngestionResponse(HttpResponse):
    def __init__(self, request):
        super().__init__(request, None)
        self.status_code = 200
        self.headers = {"Content-Type": "application/json"}
        self.content_type = "application/json"
        count = len(json.loads(request.body))
        self._body = json.dumps({"itemsReceived": count, "itemsAccepted": count, "errors": []}).encode()

    def body(self):
        return self._body

    def json(self):
        return json.loads(self._body)

    def stream_download(self, _pipeline, **_kwargs):
        raise NotImplementedError("The test transport does not support streaming responses.")


class TestMultiEndpointRoutingIntegration(unittest.TestCase):
    """Exercise provider collection and flush through a mocked ingestion transport."""

    def setUp(self):
        patches = (
            mock.patch.dict(
                os.environ,
                {
                    "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
                    "APPLICATIONINSIGHTS_SDKSTATS_DISABLED": "true",
                    "APPLICATIONINSIGHTS_CONTROLPLANE_DISABLED": "true",
                    "APPLICATIONINSIGHTS_EXPERIMENTAL_FEATURES": "multi_endpoint_routing",
                    "APPLICATIONINSIGHTS_METRIC_NAMESPACE_OPT_IN": "true",
                    "APPLICATIONINSIGHTS_OPENTELEMETRY_RESOURCE_METRIC_DISABLED": "true",
                },
            ),
            mock.patch("azure.monitor.opentelemetry.exporter.export._base._enabled_experimental_features", None),
            mock.patch("azure.monitor.opentelemetry.exporter._utils._is_on_aks", return_value=False),
        )
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)
        self.transport = mock.MagicMock(spec=HttpTransport)
        self.transport.close.return_value = None
        self.transport.__exit__.side_effect = lambda *args: self.transport.close()
        self.transport.send.side_effect = lambda request, **kwargs: _IngestionResponse(request)
        self.resource = Resource({"service.name": "resource-role", "service.instance.id": "resource-instance"})
        self.destinations = (
            ("key-one", "https://one.example/proxy/"),
            ("key-two", "https://two.example/"),
            ("key-three", "HTTPS://ONE.EXAMPLE:443/proxy"),
            ("", "https://invalid.example/"),
        )

    def _exporter(self, exporter_class, *, routing):
        with mock.patch.dict(
            os.environ, {"APPLICATIONINSIGHTS_EXPERIMENTAL_FEATURES": "multi_endpoint_routing" if routing else ""}
        ), mock.patch("azure.monitor.opentelemetry.exporter.export._base._enabled_experimental_features", None):
            exporter = exporter_class(
                connection_string="InstrumentationKey=1234abcd-5678-4efa-8abc-1234567890ab;"
                "IngestionEndpoint=https://host.example/",
                disable_offline_storage=True,
                transport=self.transport,
                retry_total=0,
            )
        self.addCleanup(exporter.client.close)
        self.addCleanup(exporter.shutdown)
        return exporter

    def test_provider_flush_routes_log_records(self):
        for routing in (False, True):
            with self.subTest(routing=routing):
                self.transport.send.reset_mock()
                exporter = self._exporter(AzureMonitorLogExporter, routing=routing)
                provider = LoggerProvider(resource=self.resource, shutdown_on_exit=False)
                self.addCleanup(provider.shutdown)
                provider.add_log_record_processor(BatchLogRecordProcessor(exporter, schedule_delay_millis=60_000))
                logger = provider.get_logger("routing-e2e")
                for index, (key, endpoint) in enumerate(self.destinations):
                    logger.emit(
                        body=f"record-{index}",
                        severity_number=SeverityNumber.INFO,
                        attributes={
                            "microsoft.instrumentation_key": key,
                            "microsoft.ingestion_endpoint": endpoint,
                            "microsoft.multi_endpoint_cloud_role": f"role-{index}",
                            "record.id": str(index),
                        },
                    )
                self.transport.send.assert_not_called()
                self.assertTrue(provider.force_flush(timeout_millis=5_000))
                expected = (
                    {
                        "https://one.example/proxy/v2.1/track": (0, 2),
                        "https://two.example/v2.1/track": (1,),
                    }
                    if routing
                    else {"https://host.example//v2.1/track": (0, 1, 2, 3)}
                )
                requests = {
                    call.args[0].url: json.loads(call.args[0].body) for call in self.transport.send.call_args_list
                }
                self.assertEqual(self.transport.send.call_count, len(expected))
                self.assertEqual(requests.keys(), expected.keys())
                for url, indexes in expected.items():
                    items = requests[url]
                    self.assertEqual(
                        [item["data"]["baseData"]["properties"]["record.id"] for item in items],
                        [str(index) for index in indexes],
                    )
                    for item, index in zip(items, indexes):
                        self.assertEqual(item["data"]["baseType"], "MessageData")
                        self.assertEqual(item["data"]["baseData"]["message"], f"record-{index}")
                        self.assertEqual(
                            item["iKey"],
                            self.destinations[index][0] if routing else "1234abcd-5678-4efa-8abc-1234567890ab",
                        )
                        self.assertEqual(item["tags"]["ai.cloud.role"], f"role-{index}" if routing else "resource-role")
                        self.assertEqual(item["tags"]["ai.cloud.roleInstance"], "resource-instance")
                        if routing:
                            for attribute in _MULTI_ENDPOINT_ROUTING_ATTRIBUTES:
                                self.assertNotIn(attribute, item["data"]["baseData"]["properties"])

    def test_provider_flush_routes_spans_and_events(self):
        for routing in (False, True):
            with self.subTest(routing=routing):
                self.transport.send.reset_mock()
                exporter = self._exporter(AzureMonitorTraceExporter, routing=routing)
                provider = TracerProvider(resource=self.resource, sampler=ALWAYS_ON, shutdown_on_exit=False)
                self.addCleanup(provider.shutdown)
                provider.add_span_processor(BatchSpanProcessor(exporter, schedule_delay_millis=60_000))
                tracer = provider.get_tracer("routing-e2e")
                for index, (key, endpoint) in enumerate(self.destinations):
                    with tracer.start_as_current_span(
                        f"record-{index}",
                        kind=SpanKind.SERVER,
                        attributes={
                            "microsoft.instrumentation_key": key,
                            "microsoft.ingestion_endpoint": endpoint,
                            "microsoft.multi_endpoint_cloud_role": f"role-{index}",
                            "record.id": str(index),
                        },
                    ) as span:
                        span.add_event(
                            f"event-{index}",
                            attributes={
                                "microsoft.instrumentation_key": "event-key",
                                "microsoft.ingestion_endpoint": "https://event.example/",
                                "record.id": str(index),
                            },
                        )
                self.transport.send.assert_not_called()
                self.assertTrue(provider.force_flush(timeout_millis=5_000))
                expected = (
                    {
                        "https://one.example/proxy/v2.1/track": (0, 2),
                        "https://two.example/v2.1/track": (1,),
                    }
                    if routing
                    else {"https://host.example//v2.1/track": (0, 1, 2, 3)}
                )
                requests = {
                    call.args[0].url: json.loads(call.args[0].body) for call in self.transport.send.call_args_list
                }
                self.assertEqual(self.transport.send.call_count, len(expected))
                self.assertEqual(requests.keys(), expected.keys())
                for url, indexes in expected.items():
                    items = requests[url]
                    self.assertEqual(
                        [item["data"]["baseType"] for item in items], ["RequestData", "MessageData"] * len(indexes)
                    )
                    self.assertEqual(
                        [item["data"]["baseData"]["properties"]["record.id"] for item in items],
                        [str(index) for index in indexes for _ in range(2)],
                    )
                    for offset, index in enumerate(indexes):
                        span_item, event_item = items[offset * 2 : offset * 2 + 2]
                        self.assertEqual(span_item["data"]["baseData"]["name"], f"record-{index}")
                        self.assertEqual(event_item["data"]["baseData"]["message"], f"event-{index}")
                        self.assertEqual(span_item["tags"]["ai.operation.id"], event_item["tags"]["ai.operation.id"])
                        for item in (span_item, event_item):
                            self.assertEqual(
                                item["iKey"],
                                self.destinations[index][0] if routing else "1234abcd-5678-4efa-8abc-1234567890ab",
                            )
                            self.assertEqual(
                                item["tags"]["ai.cloud.role"], f"role-{index}" if routing else "resource-role"
                            )
                            self.assertEqual(item["tags"]["ai.cloud.roleInstance"], "resource-instance")
                            if routing:
                                for attribute in _MULTI_ENDPOINT_ROUTING_ATTRIBUTES:
                                    self.assertNotIn(attribute, item["data"]["baseData"]["properties"])

    def test_provider_flush_routes_metric_points(self):
        for routing in (False, True):
            with self.subTest(routing=routing):
                self.transport.send.reset_mock()
                exporter = self._exporter(AzureMonitorMetricExporter, routing=routing)
                reader = PeriodicExportingMetricReader(exporter, export_interval_millis=float("inf"))
                provider = MeterProvider(metric_readers=[reader], resource=self.resource, shutdown_on_exit=False)
                self.addCleanup(provider.shutdown)
                counter = provider.get_meter("routing-e2e").create_counter("routed_count")
                for index, (key, endpoint) in enumerate(self.destinations):
                    counter.add(
                        index + 1,
                        attributes={
                            "microsoft.instrumentation_key": key,
                            "microsoft.ingestion_endpoint": endpoint,
                            "microsoft.multi_endpoint_cloud_role": f"role-{index}",
                            "record.id": str(index),
                        },
                    )
                self.transport.send.assert_not_called()
                self.assertTrue(provider.force_flush(timeout_millis=5_000))
                expected = (
                    {
                        "https://one.example/proxy/v2.1/track": (0, 2),
                        "https://two.example/v2.1/track": (1,),
                    }
                    if routing
                    else {"https://host.example//v2.1/track": (0, 1, 2, 3)}
                )
                requests = {
                    call.args[0].url: json.loads(call.args[0].body) for call in self.transport.send.call_args_list
                }
                self.assertEqual(self.transport.send.call_count, len(expected))
                self.assertEqual(requests.keys(), expected.keys())
                for url, indexes in expected.items():
                    items = requests[url]
                    self.assertEqual(
                        [item["data"]["baseData"]["properties"]["record.id"] for item in items],
                        [str(index) for index in indexes],
                    )
                    for item, index in zip(items, indexes):
                        self.assertEqual(item["data"]["baseType"], "MetricData")
                        self.assertEqual(
                            item["iKey"],
                            self.destinations[index][0] if routing else "1234abcd-5678-4efa-8abc-1234567890ab",
                        )
                        self.assertEqual(item["tags"]["ai.cloud.role"], f"role-{index}" if routing else "resource-role")
                        self.assertEqual(item["tags"]["ai.cloud.roleInstance"], "resource-instance")
                        metric = item["data"]["baseData"]["metrics"][0]
                        self.assertEqual(metric["name"], "routed_count")
                        self.assertEqual(metric["value"], index + 1)
                        if routing:
                            for attribute in _MULTI_ENDPOINT_ROUTING_ATTRIBUTES:
                                self.assertNotIn(attribute, item["data"]["baseData"]["properties"])
