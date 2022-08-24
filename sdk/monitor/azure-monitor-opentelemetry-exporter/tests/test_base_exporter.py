# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import json
import os
import shutil
import unittest
from unittest import mock
from datetime import datetime

import requests
from opentelemetry.sdk.trace.export import SpanExportResult

from azure.core.exceptions import HttpResponseError, ServiceRequestError
from azure.core.pipeline.transport import HttpResponse
from azure.monitor.opentelemetry.exporter.export._base import (
    BaseExporter,
    ExportResult,
)
from azure.monitor.opentelemetry.exporter.statsbeat._state import _REQUESTS_MAP
from azure.monitor.opentelemetry.exporter._constants import (
    _REQ_DURATION_NAME,
    _REQ_EXCEPTION_NAME,
    _REQ_FAILURE_NAME,
    _REQ_RETRY_NAME,
    _REQ_SUCCESS_NAME,
    _REQ_THROTTLE_NAME,
)
from azure.monitor.opentelemetry.exporter._generated import AzureMonitorClient
from azure.monitor.opentelemetry.exporter._generated.models import (
    TelemetryErrorDetails,
    TelemetryItem,
    TrackResponse,
)


def throw(exc_type, *args, **kwargs):
    def func(*_args, **_kwargs):
        raise exc_type(*args, **kwargs)

    return func


def clean_folder(folder):
    if os.path.isfile(folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))


# pylint: disable=W0212
# pylint: disable=R0904
class TestBaseExporter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ[
            "APPINSIGHTS_INSTRUMENTATIONKEY"
        ] = "1234abcd-5678-4efa-8abc-1234567890ab"
        cls._base = BaseExporter()
        cls._envelopes_to_export = [TelemetryItem(name="Test", time=datetime.now())]

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._base.storage._path, True)

    def setUp(self) -> None:
        _REQUESTS_MAP.clear()

    def tearDown(self):
        clean_folder(self._base.storage._path)

    def test_constructor(self):
        """Test the constructor."""
        base = BaseExporter(
            api_version="2021-02-10_Preview",
            connection_string="InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab;IngestionEndpoint=https://westus-0.in.applicationinsights.azure.com/",
            enable_local_storage=True,
            storage_maintenance_period=30,
            storage_max_size=1000,
            storage_min_retry_interval=100,
            storage_path="test/path",
            storage_retention_period=2000,
        )
        self.assertEqual(
            base._instrumentation_key,
            "4321abcd-5678-4efa-8abc-1234567890ab",
        )
        self.assertEqual(
            base._endpoint,
            "https://westus-0.in.applicationinsights.azure.com/",
        )
        self.assertIsNotNone(base.storage)
        self.assertEqual(base.storage._max_size, 1000)
        self.assertEqual(base.storage._retention_period, 2000)
        self.assertEqual(base._storage_maintenance_period, 30)
        self.assertEqual(base._timeout, 10)
        self.assertEqual(base._api_version, "2021-02-10_Preview")
        self.assertEqual(base._storage_min_retry_interval, 100)
        self.assertEqual(base._storage_path, "test/path")

    def test_transmit_from_storage_success(self):
        exporter = BaseExporter()
        exporter.storage = mock.Mock()
        blob_mock = mock.Mock()
        blob_mock.lease.return_value = True
        envelope_mock = {"name":"test","time":"time"}
        blob_mock.get.return_value = [envelope_mock]
        exporter.storage.gets.return_value = [blob_mock]
        with mock.patch.object(AzureMonitorClient, 'track') as post:
            post.return_value = TrackResponse(
                items_received=1,
                items_accepted=1,
                errors=[],
            )
            exporter._transmit_from_storage()
        exporter.storage.gets.assert_called_once()
        blob_mock.lease.assert_called_once()
        blob_mock.delete.assert_called_once()

    def test_transmit_from_storage_store_again(self):
        exporter = BaseExporter()
        exporter.storage = mock.Mock()
        blob_mock = mock.Mock()
        blob_mock.lease.return_value = True
        envelope_mock = {"name":"test","time":"time"}
        blob_mock.get.return_value = [envelope_mock]
        exporter.storage.gets.return_value = [blob_mock]
        with mock.patch("azure.monitor.opentelemetry.exporter.export._base._is_retryable_code"):
            with mock.patch.object(AzureMonitorClient, 'track', throw(HttpResponseError)):
                exporter._transmit_from_storage()
        exporter.storage.gets.assert_called_once()
        blob_mock.lease.assert_called()
        blob_mock.delete.assert_not_called()

    def test_transmit_from_storage_nothing(self):
        with mock.patch("requests.Session.request") as post:
            post.return_value = None
            self._base._transmit_from_storage()

    def test_transmit_from_storage_lease_failure(self):
        exporter = BaseExporter()
        exporter.storage = mock.Mock()
        blob_mock = mock.Mock()
        blob_mock.lease.return_value = False
        exporter.storage.gets.return_value = [blob_mock]
        transmit_mock = mock.Mock()
        exporter._transmit = transmit_mock
        exporter._transmit_from_storage()
        exporter.storage.gets.assert_called_once()
        transmit_mock.assert_not_called()
        blob_mock.lease.assert_called_once()
        blob_mock.delete.assert_not_called()

    def test_transmit_http_error_retryable(self):
        with mock.patch("azure.monitor.opentelemetry.exporter.export._base._is_retryable_code") as m:
            m.return_value = True
            with mock.patch.object(AzureMonitorClient, 'track', throw(HttpResponseError)):
                result = self._base._transmit(self._envelopes_to_export)
            self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    def test_transmit_http_error_not_retryable(self):
        with mock.patch("azure.monitor.opentelemetry.exporter.export._base._is_retryable_code") as m:
            m.return_value = False
            with mock.patch.object(AzureMonitorClient, 'track', throw(HttpResponseError)):
                result = self._base._transmit(self._envelopes_to_export)
            self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    def test_transmit_http_error_redirect(self):
        response = HttpResponse(None, None)
        response.status_code = 307
        response.headers = {"location":"https://example.com"}
        prev_redirects = self._base.client._config.redirect_policy.max_redirects
        self._base.client._config.redirect_policy.max_redirects = 2
        prev_host = self._base.client._config.host
        error = HttpResponseError(response=response)
        with mock.patch.object(AzureMonitorClient, 'track') as post:
            post.side_effect = error
            result = self._base._transmit(self._envelopes_to_export)
            self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)
            self.assertEqual(post.call_count, 2)
            self.assertEqual(self._base.client._config.host, "https://example.com")
        self._base.client._config.redirect_policy.max_redirects = prev_redirects
        self._base.client._config.host = prev_host

    def test_transmit_request_error(self):
        with mock.patch.object(AzureMonitorClient, 'track', throw(ServiceRequestError, message="error")):
            result = self._base._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    def test_transmit_request_exception(self):
        with mock.patch.object(AzureMonitorClient, 'track', throw(Exception)):
            result = self._base._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    def test_transmission_200(self):
        with mock.patch.object(AzureMonitorClient, 'track') as post:
            post.return_value = TrackResponse(
                items_received=1,
                items_accepted=1,
                errors=[],
            )
            result = self._base._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.SUCCESS)

    def test_statsbeat_200(self):
        with mock.patch.object(AzureMonitorClient, 'track') as post:
            post.return_value = TrackResponse(
                items_received=1,
                items_accepted=1,
                errors=[],
            )
            result = self._base._transmit(self._envelopes_to_export)
        self.assertEqual(len(_REQUESTS_MAP), 3)
        self.assertEqual(_REQUESTS_MAP[_REQ_SUCCESS_NAME[1]], 1)
        self.assertEqual(_REQUESTS_MAP["count"], 1)
        self.assertEqual(result, ExportResult.SUCCESS)

    def test_transmission_206_retry(self):
        exporter = BaseExporter()
        exporter.storage = mock.Mock()
        test_envelope = TelemetryItem(name="testEnvelope", time=datetime.now())
        custom_envelopes_to_export = [TelemetryItem(name="Test", time=datetime.now(
        )), TelemetryItem(name="Test", time=datetime.now()), test_envelope]
        with mock.patch.object(AzureMonitorClient, 'track') as post:
            post.return_value = TrackResponse(
                items_received=3,
                items_accepted=1,
                errors=[
                    TelemetryErrorDetails(
                        index=0,
                        status_code=400,
                        message="should drop",
                    ),
                    TelemetryErrorDetails(
                        index=2,
                        status_code=500,
                        message="should retry"
                    )
                ],
            )
            result = exporter._transmit(custom_envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)
        exporter.storage.put.assert_called_once()

    def test_transmission_206_no_retry(self):
        exporter = BaseExporter()
        exporter.storage = mock.Mock()
        test_envelope = TelemetryItem(name="testEnvelope", time=datetime.now())
        custom_envelopes_to_export = [TelemetryItem(name="Test", time=datetime.now(
        )), TelemetryItem(name="Test", time=datetime.now()), test_envelope]
        with mock.patch.object(AzureMonitorClient, 'track') as post:
            post.return_value = TrackResponse(
                items_received=3,
                items_accepted=2,
                errors=[
                    TelemetryErrorDetails(
                        index=0,
                        status_code=400,
                        message="should drop",
                    ),
                ],
            )
            result = self._base._transmit(custom_envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)
        exporter.storage.put.assert_not_called()

    def test_transmission_400(self):
        with mock.patch("requests.Session.request") as post:
            post.return_value = MockResponse(400, "{}")
            result = self._base._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    def test_transmission_408(self):
        with mock.patch("requests.Session.request") as post:
            post.return_value = MockResponse(408, "{}")
            result = self._base._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    def test_transmission_429(self):
        with mock.patch("requests.Session.request") as post:
            post.return_value = MockResponse(429, "{}")
            result = self._base._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    def test_transmission_439(self):
        with mock.patch("requests.Session.request") as post:
            post.return_value = MockResponse(439, "{}")
            result = self._base._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    def test_transmission_500(self):
        with mock.patch("requests.Session.request") as post:
            post.return_value = MockResponse(500, "{}")
            result = self._base._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    def test_transmission_502(self):
        with mock.patch("requests.Session.request") as post:
            post.return_value = MockResponse(503, "{}")
            result = self._base._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    def test_transmission_503(self):
        with mock.patch("requests.Session.request") as post:
            post.return_value = MockResponse(503, "{}")
            result = self._base._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    def test_transmission_504(self):
        with mock.patch("requests.Session.request") as post:
            post.return_value = MockResponse(504, "{}")
            result = self._base._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    def test_transmission_empty(self):
        status = self._base._transmit([])
        self.assertEqual(status, ExportResult.SUCCESS)


class MockResponse:
    def __init__(self, status_code, text, headers={}, reason="test", content="{}"):
        self.status_code = status_code
        self.text = text
        self.headers = headers
        self.reason = reason
        self.content = content
        self.raw = MockRaw()

class MockRaw:
    def __init__(self):
        self.enforce_content_length = False
