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
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import Event, ReadableSpan
from opentelemetry.sdk.trace.export import SpanExportResult
from opentelemetry.trace import SpanContext, SpanKind

from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
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


class TestTraceRouting(unittest.TestCase):
    def setUp(self):
        environment = mock.patch.dict(
            os.environ,
            {
                "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
                "APPLICATIONINSIGHTS_SDKSTATS_DISABLED": "true",
                "APPLICATIONINSIGHTS_CONTROLPLANE_DISABLED": "true",
                "APPLICATIONINSIGHTS_OPENTELEMETRY_RESOURCE_METRIC_DISABLED": "true",
            },
        )
        environment.start()
        self.addCleanup(environment.stop)
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
        exporter = AzureMonitorTraceExporter(**options)
        self.addCleanup(exporter.client.close)
        self.addCleanup(exporter.shutdown)
        return exporter

    def _span(self, endpoint="https://one.example/proxy/", key="customer-key", auth="ikey", kind=SpanKind.CLIENT):
        return ReadableSpan(
            name="operation",
            context=SpanContext(trace_id=1, span_id=2, is_remote=False),
            kind=kind,
            start_time=1,
            end_time=2,
            attributes={
                "microsoft.instrumentation_key": key,
                "microsoft.ingestion_endpoint": endpoint,
                "microsoft.ingestion_auth": auth,
                "microsoft.multi_endpoint_cloud_role": "not-the-resource-role",
                "custom": "span-value",
            },
            resource=Resource({"service.name": "resource-role", "service.instance.id": "resource-instance"}),
            events=(
                Event("message", attributes={"custom": "event-value"}),
                Event(
                    "exception",
                    attributes={
                        "microsoft.instrumentation_key": "event-key",
                        "microsoft.ingestion_endpoint": "https://event.example/",
                        "microsoft.ingestion_auth": "aad",
                        "microsoft.multi_endpoint_cloud_role": "event-role",
                        "custom": "exception-value",
                    },
                ),
            ),
        )

    def test_grouping_and_events_follow_parent_route(self):
        exporter = self._exporter()
        spans = [
            self._span(key=" key-one ", kind=SpanKind.SERVER),
            self._span(endpoint="https://two.example/", key="key-two"),
            self._span(endpoint="HTTPS://ONE.EXAMPLE:443/proxy", key="key-three"),
        ]
        self.assertEqual(exporter.export(spans), SpanExportResult.SUCCESS)
        requests = [call.args[0] for call in self.transport.send.call_args_list]
        self.assertEqual(len(requests), 2)
        self.assertTrue(requests[0].url.startswith("https://one.example/proxy/"))
        self.assertTrue(requests[1].url.startswith("https://two.example/"))
        first = json.loads(requests[0].body)
        self.assertEqual([item["iKey"] for item in first], ["key-one"] * 3 + ["key-three"] * 3)
        self.assertEqual(
            [item["data"]["baseType"] for item in first],
            ["RequestData", "MessageData", "ExceptionData", "RemoteDependencyData", "MessageData", "ExceptionData"],
        )
        self.assertEqual([item["iKey"] for item in json.loads(requests[1].body)], ["key-two"] * 3)
        for request in requests:
            for item in json.loads(request.body):
                self.assertEqual(item["tags"]["ai.cloud.role"], "resource-role")
                self.assertEqual(item["tags"]["ai.cloud.roleInstance"], "resource-instance")
                self.assertEqual(item["tags"]["ai.operation.id"], "{:032x}".format(1))
                properties = item["data"]["baseData"]["properties"]
                for attribute in _MULTI_ENDPOINT_ROUTING_ATTRIBUTES:
                    self.assertNotIn(attribute, properties)
                self.assertIn(properties["custom"], ("span-value", "event-value", "exception-value"))
        self.assertEqual(spans[0].attributes["microsoft.instrumentation_key"], " key-one ")
        self.assertEqual(spans[0].events[1].attributes["microsoft.instrumentation_key"], "event-key")

    def test_single_connection_string_is_unchanged(self):
        exporter = self._exporter(enable_multi_endpoint_routing=False)
        self.assertEqual(
            exporter.export([self._span(), self._span(endpoint="https://two.example/")]), SpanExportResult.SUCCESS
        )
        self.transport.send.assert_called_once()
        request = self.transport.send.call_args.args[0]
        self.assertTrue(request.url.startswith("https://host.example/"))
        items = json.loads(request.body)
        self.assertEqual([item["iKey"] for item in items], ["1234abcd-5678-4efa-8abc-1234567890ab"] * 6)
        self.assertEqual(items[0]["data"]["baseData"]["properties"]["microsoft.instrumentation_key"], "customer-key")
        self.assertEqual(items[2]["data"]["baseData"]["properties"]["microsoft.instrumentation_key"], "event-key")

    def test_empty_and_invalid_batches_do_not_transmit(self):
        exporter = self._exporter()
        for spans in ([], [self._span(key=" ")], [self._span(endpoint="http://invalid.example/")]):
            with self.subTest(spans=spans):
                self.assertEqual(exporter.export(spans), SpanExportResult.SUCCESS)
        self.transport.send.assert_not_called()

    @mock.patch.dict(os.environ)
    def test_routing_without_host_connection_string(self):
        os.environ.pop("APPLICATIONINSIGHTS_CONNECTION_STRING", None)
        os.environ.pop("APPINSIGHTS_INSTRUMENTATIONKEY", None)
        exporter = self._exporter(connection_string=None)
        self.assertIsNone(exporter.application_id)
        os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"] = "invalid"
        self.assertEqual(exporter.export([self._span()]), SpanExportResult.SUCCESS)
        request = self.transport.send.call_args.args[0]
        self.assertTrue(request.url.startswith("https://one.example/proxy/"))
        self.assertEqual([item["iKey"] for item in json.loads(request.body)], ["customer-key"] * 3)

    def test_configured_application_id_is_preserved(self):
        exporter = self._exporter(
            connection_string="InstrumentationKey=1234abcd-5678-4efa-8abc-1234567890ab;ApplicationId=host-app"
        )
        self.assertEqual(exporter.application_id, "host-app")

    def test_authentication_groups_include_parent_events(self):
        credential = mock.Mock(spec=["get_token"])
        credential.get_token.return_value = AccessToken("test-token", int(time.time()) + 3600)
        exporter = self._exporter(credential=credential)
        spans = [self._span(), self._span(auth=" AAD ")]
        for _ in range(2):
            self.assertEqual(exporter.export(spans), SpanExportResult.SUCCESS)
        requests = [call.args[0] for call in self.transport.send.call_args_list]
        self.assertEqual(len(requests), 4)
        for request in requests[::2]:
            self.assertNotIn("Authorization", request.headers)
        for request in requests[1::2]:
            self.assertEqual(request.headers["Authorization"], f"Bearer {credential.get_token.return_value.token}")
        self.assertTrue(all(len(json.loads(request.body)) == 3 for request in requests))
        credential.get_token.assert_called_once()

    def test_missing_aad_credential_does_not_block_other_routes(self):
        exporter = self._exporter(credential=None)
        with self.assertLogs("azure.monitor.opentelemetry.exporter.export._base", level="ERROR"):
            result = exporter.export([self._span(auth="aad"), self._span(endpoint="https://two.example/")])
        self.assertEqual(result, SpanExportResult.FAILURE)
        self.transport.send.assert_called_once()
        self.assertTrue(self.transport.send.call_args.args[0].url.startswith("https://two.example/"))

    def test_retry_storage_preserves_parent_route_and_event_keys(self):
        now = datetime.datetime(2026, 10, 20, tzinfo=datetime.timezone.utc)
        exporter = self._exporter(disable_offline_storage=False)
        self.transport.send.side_effect = lambda request, **kwargs: _Response(
            request, 429 if request.url.startswith("https://one.example/") else 200, {"Retry-After": "60"}
        )
        with mock.patch("azure.monitor.opentelemetry.exporter._storage._now", return_value=now):
            result = exporter.export([self._span(key="old-key"), self._span(endpoint="https://two.example/")])
        self.assertEqual(result, SpanExportResult.FAILURE)
        self.assertEqual(self.transport.send.call_count, 2)
        exporter.shutdown()
        restarted = self._exporter(disable_offline_storage=False)
        self.transport.send.reset_mock()
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request)
        with mock.patch(
            "azure.monitor.opentelemetry.exporter._storage._now", return_value=now + datetime.timedelta(seconds=61)
        ):
            self.assertEqual(restarted.export([self._span(key="new-key")]), SpanExportResult.SUCCESS)
        requests = [call.args[0] for call in self.transport.send.call_args_list]
        self.assertEqual(len(requests), 2)
        self.assertEqual(
            [[item["iKey"] for item in json.loads(request.body)] for request in requests],
            [["new-key"] * 3, ["old-key"] * 3],
        )
        self.assertTrue(all(request.url.startswith("https://one.example/proxy/") for request in requests))
        self.assertFalse(list((Path(self.directory.name) / "host").iterdir()))

    def test_shutdown_closes_routes_and_rejects_later_exports(self):
        exporter = self._exporter(disable_offline_storage=False)
        self.assertEqual(exporter.export([self._span()]), SpanExportResult.SUCCESS)
        exporter.shutdown()
        closes = self.transport.close.call_count
        self.assertEqual(closes, 2)
        exporter.shutdown()
        self.assertEqual(self.transport.close.call_count, closes)
        self.transport.send.reset_mock()
        with self.assertLogs("azure.monitor.opentelemetry.exporter.export._base", level="ERROR"):
            self.assertEqual(exporter.export([self._span()]), SpanExportResult.FAILURE)
        self.transport.send.assert_not_called()

    def test_routed_export_exception_is_reported(self):
        exporter = self._exporter()
        with mock.patch.object(exporter, "_transmit_routed", side_effect=RuntimeError("test failure")):
            with self.assertLogs("azure.monitor.opentelemetry.exporter.export.trace._exporter", level="ERROR") as logs:
                self.assertEqual(exporter.export([self._span()]), SpanExportResult.FAILURE)
        self.assertIn("test failure", logs.output[0])
