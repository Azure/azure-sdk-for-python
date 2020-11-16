# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import json
import os
import shutil
import unittest
from unittest import mock

import requests
from opentelemetry.sdk.metrics.export import MetricsExportResult
from opentelemetry.sdk.trace.export import SpanExportResult

from microsoft.opentelemetry.exporter.azuremonitor.export import (
    BaseExporter,
    ExportResult,
    get_trace_export_result,
)
from microsoft.opentelemetry.exporter.azuremonitor.options import ExporterOptions
from microsoft.opentelemetry.exporter.azuremonitor._generated.models import MonitorBase, TelemetryItem

TEST_FOLDER = os.path.abspath(".test")
STORAGE_PATH = os.path.join(TEST_FOLDER)


def throw(exc_type, *args, **kwargs):
    def func(*_args, **_kwargs):
        raise exc_type(*args, **kwargs)

    return func


# pylint: disable=W0212
# pylint: disable=R0904
class TestBaseExporter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.makedirs(TEST_FOLDER, exist_ok=True)
        os.environ[
            "APPINSIGHTS_INSTRUMENTATIONKEY"
        ] = "1234abcd-5678-4efa-8abc-1234567890ab"
        cls._base = BaseExporter()
        cls._base.storage.path=STORAGE_PATH

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEST_FOLDER, True)

    def setUp(self):
        if os.path.exists(STORAGE_PATH):
            for filename in os.listdir(STORAGE_PATH):
                file_path = os.path.join(STORAGE_PATH, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path, True)
                except OSError as e:
                    print("Failed to delete %s. Reason: %s" % (file_path, e))

    def test_constructor(self):
        """Test the constructor."""
        base = BaseExporter(
            connection_string="InstrumentationKey=4321abcd-5678-4efa-8abc-1234567890ab",
        )
        self.assertEqual(
            base._instrumentation_key,
            "4321abcd-5678-4efa-8abc-1234567890ab",
        )
        self.assertEqual(base.storage.max_size, 52428800)
        self.assertEqual(base.storage.maintenance_period, 60)
        self.assertEqual(base.storage.retention_period, 604800)
        self.assertEqual(base._timeout, 10)
        

    def test_constructor_wrong_options(self):
        """Test the constructor with wrong options."""
        with self.assertRaises(TypeError):
            BaseExporter(something_else=6)

    # def test_transmission_nothing(self):
    #     exporter = BaseExporter(
    #         storage_path=os.path.join(TEST_FOLDER, self.id())
    #     )
    #     with mock.patch("requests.post") as post:
    #         post.return_value = None
    #         exporter._transmit_from_storage()

    # def test_transmit_request_timeout(self):
    #     exporter = BaseExporter(
    #         storage_path=os.path.join(TEST_FOLDER, self.id())
    #     )
    #     envelopes_to_export = map(lambda x: x.as_dict(), tuple(
    #         [TelemetryItem(name="", time="")]))
    #     exporter.storage.put(envelopes_to_export)
    #     with mock.patch("requests.post", throw(requests.Timeout)):
    #         exporter._transmit_from_storage()
    #     self.assertIsNone(exporter.storage.get())
    #     self.assertEqual(len(os.listdir(exporter.storage.path)), 1)

    # def test_transmit_request_exception(self):
    #     exporter = BaseExporter(
    #         storage_path=os.path.join(TEST_FOLDER, self.id())
    #     )
    #     envelopes_to_export = map(lambda x: x.as_dict(), tuple(
    #         [TelemetryItem(name="", time="")]))
    #     exporter.storage.put(envelopes_to_export)
    #     with mock.patch("requests.post", throw(Exception)):
    #         exporter._transmit_from_storage()
    #     self.assertIsNone(exporter.storage.get())
    #     self.assertEqual(len(os.listdir(exporter.storage.path)), 1)

    # @mock.patch("requests.post", return_value=mock.Mock())
    # def test_transmission_lease_failure(self, requests_mock):
    #     requests_mock.return_value = MockResponse(200, "unknown")
    #     exporter = BaseExporter(
    #         storage_path=os.path.join(TEST_FOLDER, self.id())
    #     )
    #     envelopes_to_export = map(lambda x: x.as_dict(), tuple(
    #         [TelemetryItem(name="", time="")]))
    #     exporter.storage.put(envelopes_to_export)
    #     with mock.patch(
    #         "microsoft.opentelemetry.exporter.azuremonitor.storage.LocalFileBlob.lease"
    #     ) as lease:  # noqa: E501
    #         lease.return_value = False
    #         exporter._transmit_from_storage()
    #     self.assertTrue(exporter.storage.get())

    # def test_transmission(self):
    #     exporter = BaseExporter(
    #         storage_path=os.path.join(TEST_FOLDER, self.id())
    #     )
    #     envelopes_to_export = map(lambda x: x.as_dict(), tuple(
    #         [TelemetryItem(name="", time="")]))
    #     exporter.storage.put(envelopes_to_export)
    #     with mock.patch("requests.post") as post:
    #         post.return_value = MockResponse(200, None)
    #         del post.return_value.text
    #         exporter._transmit_from_storage()
    #     self.assertIsNone(exporter.storage.get())
    #     self.assertEqual(len(os.listdir(exporter.storage.path)), 0)

    # def test_transmission_200(self):
    #     exporter = BaseExporter(
    #         storage_path=os.path.join(TEST_FOLDER, self.id())
    #     )
    #     envelopes_to_export = map(lambda x: x.as_dict(), tuple(
    #         [TelemetryItem(name="", time="")]))
    #     exporter.storage.put(envelopes_to_export)
    #     with mock.patch("requests.post") as post:
    #         post.return_value=MockResponse(200, "unknown")
    #         exporter._transmit_from_storage()
    #     self.assertIsNone(exporter.storage.get())
    #     self.assertEqual(len(os.listdir(exporter.storage.path)), 0)

    # def test_transmission_206(self):
    #     exporter=BaseExporter(
    #         storage_path=os.path.join(TEST_FOLDER, self.id())
    #     )
    #     envelopes_to_export=map(lambda x: x.as_dict(), tuple(
    #         [TelemetryItem(name="", time="")]))
    #     exporter.storage.put(envelopes_to_export)
    #     with mock.patch("requests.post") as post:
    #         post.return_value=MockResponse(206, "unknown")
    #         exporter._transmit_from_storage()
    #     self.assertIsNone(exporter.storage.get())
    #     self.assertEqual(len(os.listdir(exporter.storage.path)), 1)

    # def test_transmission_206_500(self):
    #     exporter=BaseExporter(
    #         storage_path=os.path.join(TEST_FOLDER, self.id())
    #     )
    #     test_envelope=TelemetryItem(name="testEnvelope", time="")
    #     envelopes_to_export=map(
    #         lambda x: x.as_dict(),
    #         tuple([TelemetryItem(name="", time=""), TelemetryItem(
    #             name="", time=""), test_envelope]),
    #     )
    #     exporter.storage.put(envelopes_to_export)
    #     with mock.patch("requests.post") as post:
    #         post.return_value=MockResponse(
    #             206,
    #             json.dumps(
    #                 {
    #                     "itemsReceived": 5,
    #                     "itemsAccepted": 3,
    #                     "errors": [
    #                         {"index": 0, "statusCode": 400, "message": ""},
    #                         {
    #                             "index": 2,
    #                             "statusCode": 500,
    #                             "message": "Internal Server Error",
    #                         },
    #                     ],
    #                 }
    #             ),
    #         )
    #         exporter._transmit_from_storage()
    #     self.assertEqual(len(os.listdir(exporter.storage.path)), 1)
    #     self.assertEqual(
    #         exporter.storage.get().get()[0]["name"], "testEnvelope"
    #     )

    # def test_transmission_206_no_retry(self):
    #     exporter=BaseExporter(
    #         storage_path=os.path.join(TEST_FOLDER, self.id())
    #     )
    #     envelopes_to_export=map(lambda x: x.as_dict(), tuple(
    #         [TelemetryItem(name="", time="")]))
    #     exporter.storage.put(envelopes_to_export)
    #     with mock.patch("requests.post") as post:
    #         post.return_value=MockResponse(
    #             206,
    #             json.dumps(
    #                 {
    #                     "itemsReceived": 3,
    #                     "itemsAccepted": 2,
    #                     "errors": [
    #                         {"index": 0, "statusCode": 400, "message": ""}
    #                     ],
    #                 }
    #             ),
    #         )
    #         exporter._transmit_from_storage()
    #     self.assertEqual(len(os.listdir(exporter.storage.path)), 0)

    # def test_transmission_206_bogus(self):
    #     exporter=BaseExporter(
    #         storage_path=os.path.join(TEST_FOLDER, self.id())
    #     )
    #     envelopes_to_export=map(lambda x: x.as_dict(), tuple(
    #         [TelemetryItem(name="", time="")]))
    #     exporter.storage.put(envelopes_to_export)
    #     with mock.patch("requests.post") as post:
    #         post.return_value=MockResponse(
    #             206,
    #             json.dumps(
    #                 {
    #                     "itemsReceived": 5,
    #                     "itemsAccepted": 3,
    #                     "errors": [{"foo": 0, "bar": 1}],
    #                 }
    #             ),
    #         )
    #         exporter._transmit_from_storage()
    #     self.assertIsNone(exporter.storage.get())
    #     self.assertEqual(len(os.listdir(exporter.storage.path)), 0)

    # def test_transmission_400(self):
    #     exporter=BaseExporter(
    #         storage_path=os.path.join(TEST_FOLDER, self.id())
    #     )
    #     envelopes_to_export=map(lambda x: x.as_dict(), tuple(
    #         [TelemetryItem(name="", time="")]))
    #     exporter.storage.put(envelopes_to_export)
    #     with mock.patch("requests.post") as post:
    #         post.return_value=MockResponse(400, "{}")
    #         exporter._transmit_from_storage()
    #     self.assertEqual(len(os.listdir(exporter.storage.path)), 0)

    # def test_transmission_439(self):
    #     exporter=BaseExporter(
    #         storage_path=os.path.join(TEST_FOLDER, self.id())
    #     )
    #     envelopes_to_export=map(lambda x: x.as_dict(), tuple(
    #         [TelemetryItem(name="", time="")]))
    #     exporter.storage.put(envelopes_to_export)
    #     with mock.patch("requests.post") as post:
    #         post.return_value=MockResponse(439, "{}")
    #         exporter._transmit_from_storage()
    #     self.assertIsNone(exporter.storage.get())
    #     self.assertEqual(len(os.listdir(exporter.storage.path)), 1)

    # def test_transmission_500(self):
    #     exporter=BaseExporter(
    #         storage_path=os.path.join(TEST_FOLDER, self.id())
    #     )
    #     envelopes_to_export=map(lambda x: x.as_dict(), tuple(
    #         [TelemetryItem(name="", time="")]))
    #     exporter.storage.put(envelopes_to_export)
    #     with mock.patch("requests.post") as post:
    #         post.return_value=MockResponse(500, "{}")
    #         exporter._transmit_from_storage()
    #     self.assertIsNone(exporter.storage.get())
    #     self.assertEqual(len(os.listdir(exporter.storage.path)), 1)

    # def test_transmission_empty(self):
    #     exporter=BaseExporter(
    #         storage_path=os.path.join(TEST_FOLDER, self.id())
    #     )
    #     status=exporter._transmit([])
    #     self.assertEqual(status, ExportResult.SUCCESS)

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
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text
