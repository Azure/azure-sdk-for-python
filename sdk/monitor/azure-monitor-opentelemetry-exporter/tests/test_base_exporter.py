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
from azure.monitor.opentelemetry.exporter.export._base import (
    BaseExporter,
    ExportResult,
    get_trace_export_result,
)
from azure.monitor.opentelemetry.exporter._generated.models import TelemetryItem


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

    def tearDown(self):
        clean_folder(self._base.storage._path)

    def test_constructor(self):
        """Test the constructor."""
        base = BaseExporter(
            api_version="2021-02-10_Preview",
            connection_string="InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab",
        )
        self.assertEqual(
            base._instrumentation_key,
            "4321abcd-5678-4efa-8abc-1234567890ab",
        )
        self.assertEqual(base.storage._max_size, 52428800)
        self.assertEqual(base.storage._retention_period, 604800)
        self.assertEqual(base._timeout, 10)
        self.assertEqual(base._api_version, "2021-02-10_Preview")

    @unittest.skip("transient storage")
    def test_transmit_from_storage_failed_retryable(self):
        envelopes_to_store = [x.as_dict() for x in self._envelopes_to_export]
        self._base.storage.put(envelopes_to_store)
        # Timeout in HTTP request is a retryable case
        with mock.patch("requests.Session.request", throw(requests.Timeout)):
            self._base._transmit_from_storage()
        # File would be locked for 1 second
        self.assertIsNone(self._base.storage.get())
        # File still present
        self.assertGreaterEqual(len(os.listdir(self._base.storage._path)), 1)

    @unittest.skip("transient storage")
    def test_transmit_from_storage_failed_not_retryable(self):
        envelopes_to_store = [x.as_dict() for x in self._envelopes_to_export]
        self._base.storage.put(envelopes_to_store)
        with mock.patch("requests.Session.request") as post:
            # Do not retry with internal server error responses
            post.return_value = MockResponse(400, "{}")
            self._base._transmit_from_storage()
        self._base.storage.get()
        # File no longer present
        self.assertEqual(len(os.listdir(self._base.storage._path)), 0)

    def test_transmit_from_storage_nothing(self):
        with mock.patch("requests.Session.request") as post:
            post.return_value = None
            self._base._transmit_from_storage()

    @unittest.skip("transient storage")
    @mock.patch("requests.Session.request", return_value=mock.Mock())
    def test_transmit_from_storage_lease_failure(self, requests_mock):
        requests_mock.return_value = MockResponse(200, "unknown")
        envelopes_to_store = [x.as_dict() for x in self._envelopes_to_export]
        self._base.storage.put(envelopes_to_store)
        with mock.patch(
            "azure.monitor.opentelemetry.exporter._storage.LocalFileBlob.lease"
        ) as lease:  # noqa: E501
            lease.return_value = False
            self._base._transmit_from_storage()
        self.assertTrue(self._base.storage.get())

    def test_transmit_request_timeout(self):
        with mock.patch("requests.Session.request", throw(requests.Timeout)):
            result = self._base._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    def test_transmit_http_error_retryable(self):
        with mock.patch("azure.monitor.opentelemetry.exporter.export._base._is_retryable_code") as m:
            m.return_value = True
            with mock.patch("requests.Session.request", throw(HttpResponseError)):
                result = self._base._transmit(self._envelopes_to_export)
            self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    def test_transmit_http_error_retryable(self):
        with mock.patch("azure.monitor.opentelemetry.exporter.export._base._is_retryable_code") as m:
            m.return_value = False
            with mock.patch("requests.Session.request", throw(HttpResponseError)):
                result = self._base._transmit(self._envelopes_to_export)
            self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    def test_transmit_request_error(self):
        with mock.patch("requests.Session.request", throw(ServiceRequestError, message="error")):
            result = self._base._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    def test_transmit_request_exception(self):
        with mock.patch("requests.Session.request", throw(Exception)):
            result = self._base._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    def test_transmission_200(self):
        with mock.patch("requests.Session.request") as post:
            post.return_value = MockResponse(200, json.dumps(
                {
                    "itemsReceived": 1,
                    "itemsAccepted": 1,
                    "errors": [],
                }
            ), reason="OK", content="")
            result = self._base._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.SUCCESS)

    def test_transmission_206(self):
        with mock.patch("requests.Session.request") as post:
            post.return_value = MockResponse(206, "unknown")
            result = self._base._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

    def test_transmission_206_500(self):
        test_envelope = TelemetryItem(name="testEnvelope", time=datetime.now())
        custom_envelopes_to_export = [TelemetryItem(name="Test", time=datetime.now(
        )), TelemetryItem(name="Test", time=datetime.now()), test_envelope]
        with mock.patch("requests.Session.request") as post:
            post.return_value = MockResponse(
                206,
                json.dumps(
                    {
                        "itemsReceived": 5,
                        "itemsAccepted": 3,
                        "errors": [
                            {"index": 0, "statusCode": 400, "message": ""},
                            {
                                "index": 2,
                                "statusCode": 500,
                                "message": "Internal Server Error",
                            },
                        ],
                    }
                ),
            )
            result = self._base._transmit(custom_envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)
        self._base.storage.get()
        self.assertEqual(
            self._base.storage.get().get()[0]["name"], "testEnvelope"
        )

    def test_transmission_206_no_retry(self):
        envelopes_to_export = map(lambda x: x.as_dict(), tuple(
            [TelemetryItem(name="testEnvelope", time=datetime.now())]))
        self._base.storage.put(envelopes_to_export)
        with mock.patch("requests.Session.request") as post:
            post.return_value = MockResponse(
                206,
                json.dumps(
                    {
                        "itemsReceived": 3,
                        "itemsAccepted": 2,
                        "errors": [
                            {"index": 0, "statusCode": 400, "message": ""}
                        ],
                    }
                ),
            )
            result = self._base._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

    def test_transmission_206_bogus(self):
        envelopes_to_export = map(lambda x: x.as_dict(), tuple(
            [TelemetryItem(name="testEnvelope", time=datetime.now())]))
        self._base.storage.put(envelopes_to_export)
        with mock.patch("requests.Session.request") as post:
            post.return_value = MockResponse(
                206,
                json.dumps(
                    {
                        "itemsReceived": 5,
                        "itemsAccepted": 3,
                        "errors": [{"foo": 0, "bar": 1}],
                    }
                ),
            )
            result = self._base._transmit(self._envelopes_to_export)
        self.assertEqual(result, ExportResult.FAILED_NOT_RETRYABLE)

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
        self.assertEqual(result, ExportResult.FAILED_RETRYABLE)

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

    def test_get_trace_export_result(self):
        self.assertEqual(
            get_trace_export_result(ExportResult.SUCCESS),
            SpanExportResult.SUCCESS,
        )
        self.assertEqual(
            get_trace_export_result(ExportResult.FAILED_NOT_RETRYABLE),
            SpanExportResult.FAILURE,
        )
        self.assertEqual(
            get_trace_export_result(ExportResult.FAILED_RETRYABLE),
            SpanExportResult.FAILURE,
        )
        self.assertEqual(get_trace_export_result(None), None)


class MockResponse:
    def __init__(self, status_code, text, headers={}, reason="test", content="{}"):
        self.status_code = status_code
        self.text = text
        self.headers = headers
        self.reason = reason
        self.content = content
