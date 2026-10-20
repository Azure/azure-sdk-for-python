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
from opentelemetry._logs import LogRecord
from opentelemetry.sdk._logs import ReadWriteLogRecord
from opentelemetry.sdk._logs.export import LogRecordExportResult
from opentelemetry.sdk.resources import Resource

from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter
from azure.monitor.opentelemetry.exporter._constants import _ONE_SETTINGS_FEATURE_LOCAL_STORAGE


class _Response(HttpResponse):
    def __init__(self, request, status_code=200, headers=None, errors=None):
        super().__init__(request, None)
        self.status_code = status_code
        self.headers = {"Content-Type": "application/json", **(headers or {})}
        self.content_type = "application/json"
        count = len(json.loads(request.body))
        self._body = json.dumps(
            {"itemsReceived": count, "itemsAccepted": count - len(errors or []), "errors": errors or []}
        ).encode()

    def body(self):
        return self._body

    def json(self):
        return json.loads(self._body)


class TestLogRouting(unittest.TestCase):
    def setUp(self):
        environment = mock.patch.dict(
            os.environ,
            {
                "APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL": "true",
                "APPLICATIONINSIGHTS_SDKSTATS_DISABLED": "true",
                "APPLICATIONINSIGHTS_CONTROLPLANE_DISABLED": "true",
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
        exporter = AzureMonitorLogExporter(**options)
        self.addCleanup(exporter.shutdown)
        return exporter

    def _record(self, endpoint="https://one.example/proxy/", key="customer-key", auth="ikey", body="message"):
        return ReadWriteLogRecord(
            LogRecord(
                timestamp=1,
                body=body,
                attributes={
                    "microsoft.instrumentation_key": key,
                    "microsoft.ingestion_endpoint": endpoint,
                    "microsoft.ingestion_auth": auth,
                    "microsoft.multi_endpoint_cloud_role": "not-the-resource-role",
                },
            ),
            resource=Resource({"service.name": "resource-role", "service.instance.id": "resource-instance"}),
        )

    def test_grouping_and_per_item_keys(self):
        exporter = self._exporter()
        records = [
            self._record(key=" key-one "),
            self._record(endpoint="https://two.example/", key="key-two"),
            self._record(endpoint="HTTPS://ONE.EXAMPLE:443/proxy", key="key-three"),
        ]
        self.assertEqual(exporter.export(records), LogRecordExportResult.SUCCESS)
        requests = [call.args[0] for call in self.transport.send.call_args_list]
        self.assertEqual(len(requests), 2)
        self.assertTrue(requests[0].url.startswith("https://one.example/proxy/"))
        self.assertTrue(requests[1].url.startswith("https://two.example/"))
        self.assertEqual([item["iKey"] for item in json.loads(requests[0].body)], ["key-one", "key-three"])
        self.assertEqual([item["iKey"] for item in json.loads(requests[1].body)], ["key-two"])
        for request in requests:
            for item in json.loads(request.body):
                self.assertEqual(item["tags"]["ai.cloud.role"], "resource-role")
                self.assertEqual(item["tags"]["ai.cloud.roleInstance"], "resource-instance")
        self.assertEqual(records[0].log_record.attributes["microsoft.instrumentation_key"], " key-one ")

    def test_single_connection_string_is_unchanged(self):
        exporter = self._exporter(enable_multi_endpoint_routing=False)
        records = [self._record(), self._record(endpoint="https://two.example/")]
        self.assertEqual(exporter.export(records), LogRecordExportResult.SUCCESS)
        self.transport.send.assert_called_once()
        request = self.transport.send.call_args.args[0]
        self.assertTrue(request.url.startswith("https://host.example/"))
        self.assertEqual(
            [item["iKey"] for item in json.loads(request.body)],
            ["1234abcd-5678-4efa-8abc-1234567890ab"] * 2,
        )

    def test_route_creation_preserves_resolved_host_configuration(self):
        with mock.patch.dict(
            os.environ,
            {
                "APPINSIGHTS_INSTRUMENTATIONKEY": "1234abcd-5678-4efa-8abc-1234567890ab",
            },
        ):
            os.environ.pop("APPLICATIONINSIGHTS_CONNECTION_STRING", None)
            exporter = self._exporter(connection_string=None, credential=None)
            os.environ.pop("APPINSIGHTS_INSTRUMENTATIONKEY")
            os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"] = "invalid"
            self.assertEqual(exporter.export([self._record()]), LogRecordExportResult.SUCCESS)
        self.assertTrue(self.transport.send.call_args.args[0].url.startswith("https://one.example/proxy/"))

    def test_authentication_groups_and_client_reuse(self):
        credential = mock.Mock(spec=["get_token"])
        credential.get_token.return_value = AccessToken("test-token", int(time.time()) + 3600)
        exporter = self._exporter(credential=credential)
        records = [self._record(), self._record(auth=" AAD ")]
        for _ in range(2):
            self.assertEqual(exporter.export(records), LogRecordExportResult.SUCCESS)
        requests = [call.args[0] for call in self.transport.send.call_args_list]
        self.assertEqual(len(requests), 4)
        for request in requests[::2]:
            self.assertNotIn("Authorization", request.headers)
        for request in requests[1::2]:
            self.assertEqual(request.headers["Authorization"], "Bearer test-token")
        credential.get_token.assert_called_once()

    def test_missing_aad_credential_does_not_block_other_routes(self):
        exporter = self._exporter(credential=None)
        with self.assertLogs("azure.monitor.opentelemetry.exporter.export._base", level="ERROR"):
            result = exporter.export([self._record(auth="aad"), self._record(endpoint="https://two.example/")])
        self.assertEqual(result, LogRecordExportResult.FAILURE)
        self.transport.send.assert_called_once()
        self.assertTrue(self.transport.send.call_args.args[0].url.startswith("https://two.example/"))

    def test_routed_export_exception_is_reported(self):
        exporter = self._exporter()
        with mock.patch.object(exporter, "_transmit_routed", side_effect=RuntimeError("test failure")):
            with self.assertLogs("azure.monitor.opentelemetry.exporter.export.logs._exporter", level="ERROR") as logs:
                self.assertEqual(exporter.export([self._record()]), LogRecordExportResult.FAILURE)
        self.assertIn("test failure", logs.output[0])

    def test_invalid_destination_response_does_not_shutdown_host_stats(self):
        exporter = self._exporter()
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request, 400)
        with mock.patch(
            "azure.monitor.opentelemetry.exporter.statsbeat._statsbeat.shutdown_statsbeat_metrics"
        ) as shutdown_statsbeat, mock.patch(
            "azure.monitor.opentelemetry.exporter.statsbeat.customer.shutdown_customer_sdkstats_metrics"
        ) as shutdown_customer_stats:
            self.assertEqual(exporter.export([self._record()]), LogRecordExportResult.FAILURE)
        shutdown_statsbeat.assert_not_called()
        shutdown_customer_stats.assert_not_called()

    def test_retry_storage_survives_restart_and_preserves_keys(self):
        now = datetime.datetime(2026, 10, 20, tzinfo=datetime.timezone.utc)
        exporter = self._exporter(disable_offline_storage=False)
        self.transport.send.side_effect = lambda request, **kwargs: _Response(
            request, 429, headers={"Retry-After": "60"}
        )
        with mock.patch("azure.monitor.opentelemetry.exporter._storage._now", return_value=now):
            self.assertEqual(exporter.export([self._record(key="old-key")]), LogRecordExportResult.FAILURE)
        exporter.shutdown()
        restarted = self._exporter(disable_offline_storage=False)
        self.transport.send.reset_mock()
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request)
        with mock.patch(
            "azure.monitor.opentelemetry.exporter._storage._now", return_value=now + datetime.timedelta(seconds=61)
        ):
            self.assertEqual(restarted.export([self._record(key="new-key")]), LogRecordExportResult.SUCCESS)
        requests = [call.args[0] for call in self.transport.send.call_args_list]
        self.assertEqual(len(requests), 2)
        self.assertEqual([json.loads(request.body)[0]["iKey"] for request in requests], ["new-key", "old-key"])
        self.assertTrue(all(request.url.startswith("https://one.example/proxy/") for request in requests))
        self.assertFalse(list((Path(self.directory.name) / "host").iterdir()))

    def test_retry_failure_is_isolated_from_other_destinations(self):
        exporter = self._exporter(disable_offline_storage=False)
        self.transport.send.side_effect = lambda request, **kwargs: _Response(
            request, 429 if request.url.startswith("https://one.example/") else 200, headers={"Retry-After": "60"}
        )
        result = exporter.export([self._record(), self._record(endpoint="https://two.example/")])
        self.assertEqual(result, LogRecordExportResult.FAILURE)
        requests = [call.args[0] for call in self.transport.send.call_args_list]
        self.assertEqual(len(requests), 2)
        self.assertTrue(requests[1].url.startswith("https://two.example/"))
        self.assertFalse(list((Path(self.directory.name) / "host").iterdir()))

    def test_partial_failure_retries_only_rejected_items(self):
        now = datetime.datetime(2026, 10, 20, tzinfo=datetime.timezone.utc)
        exporter = self._exporter(disable_offline_storage=False)
        self.transport.send.side_effect = lambda request, **kwargs: _Response(
            request,
            206,
            headers={"Retry-After": "60"},
            errors=[{"index": 1, "statusCode": 429, "message": "retry"}],
        )
        with mock.patch("azure.monitor.opentelemetry.exporter._storage._now", return_value=now):
            result = exporter.export([self._record(key="accepted"), self._record(key="rejected")])
        self.assertEqual(result, LogRecordExportResult.FAILURE)
        self.transport.send.reset_mock()
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request)
        with mock.patch(
            "azure.monitor.opentelemetry.exporter._storage._now", return_value=now + datetime.timedelta(seconds=61)
        ):
            self.assertEqual(exporter.export([self._record(key="new")]), LogRecordExportResult.SUCCESS)
        requests = [call.args[0] for call in self.transport.send.call_args_list]
        self.assertEqual([json.loads(request.body)[0]["iKey"] for request in requests], ["new", "rejected"])

    def test_retry_storage_is_separate_for_authentication_modes(self):
        credential = mock.Mock(spec=["get_token"])
        credential.get_token.return_value = AccessToken("test-token", int(time.time()) + 3600)
        exporter = self._exporter(credential=credential, disable_offline_storage=False)
        self.transport.send.side_effect = lambda request, **kwargs: _Response(
            request, 200 if "Authorization" in request.headers else 429, headers={"Retry-After": "60"}
        )
        self.assertEqual(exporter.export([self._record(), self._record(auth="aad")]), LogRecordExportResult.FAILURE)
        partitions = list((Path(self.directory.name) / "host-routes").iterdir())
        self.assertEqual(len(partitions), 2)
        self.assertEqual(sorted(bool(list(partition.iterdir())) for partition in partitions), [False, True])
        self.transport.send.reset_mock()
        self.assertEqual(exporter.export([self._record(auth="aad")]), LogRecordExportResult.SUCCESS)
        self.transport.send.assert_called_once()

    def test_storage_capacity_is_shared_by_routes_not_host(self):
        exporter = self._exporter(
            disable_offline_storage=False,
            storage_max_size=1,
            storage_directory=str(Path(self.directory.name) / "host") + os.sep,
        )
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request, 429)
        result = exporter.export([self._record(), self._record(endpoint="https://two.example/")])
        self.assertEqual(result, LogRecordExportResult.FAILURE)
        partitions = list((Path(self.directory.name) / "host-routes").iterdir())
        self.assertEqual(len(partitions), 2)
        self.assertEqual(sorted(bool(list(partition.iterdir())) for partition in partitions), [False, True])
        self.assertTrue(exporter.storage._check_storage_size())

    @mock.patch("azure.monitor.opentelemetry.exporter.export._rate_limiter.time.monotonic", return_value=0)
    def test_rate_limit_is_shared_by_routes(self, _monotonic):
        exporter = self._exporter(max_envelopes_per_second=1)
        result = exporter.export([self._record(), self._record(endpoint="https://two.example/")])
        self.assertEqual(result, LogRecordExportResult.FAILURE)
        self.transport.send.assert_called_once()

    def test_shutdown_closes_routed_clients(self):
        exporter = self._exporter()
        self.assertEqual(
            exporter.export([self._record(), self._record(endpoint="https://two.example/")]),
            LogRecordExportResult.SUCCESS,
        )
        exporter.shutdown()
        self.assertEqual(self.transport.close.call_count, 3)
        self.assertEqual(exporter.export([self._record()]), LogRecordExportResult.FAILURE)

    def test_storage_kill_switch_applies_to_routes(self):
        exporter = self._exporter(disable_offline_storage=False)
        exporter._local_storage_configuration_callback({_ONE_SETTINGS_FEATURE_LOCAL_STORAGE: {"default": "disabled"}})
        self.transport.send.side_effect = lambda request, **kwargs: _Response(request, 429)
        self.assertEqual(exporter.export([self._record()]), LogRecordExportResult.FAILURE)
        self.assertFalse(list(Path(self.directory.name).rglob("*.lock")))
        exporter._local_storage_configuration_callback({_ONE_SETTINGS_FEATURE_LOCAL_STORAGE: {"default": "enabled"}})
        self.assertEqual(exporter.export([self._record()]), LogRecordExportResult.FAILURE)
        self.assertEqual(len(list(Path(self.directory.name).rglob("*.lock"))), 1)
