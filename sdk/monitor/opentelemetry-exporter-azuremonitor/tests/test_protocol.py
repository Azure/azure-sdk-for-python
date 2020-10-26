# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import unittest

from opentelemetry.exporter.azuremonitor import protocol


class TestProtocol(unittest.TestCase):
    def test_object(self):
        data = protocol.BaseObject()
        self.assertEqual(repr(data), "{}")

    def test_data(self):
        data = protocol.Data()
        self.assertIsNone(data.base_data)
        self.assertIsNone(data.base_type)

    def test_data_point(self):
        data = protocol.DataPoint()
        self.assertEqual(data.ns, "")

    def test_envelope(self):
        data = protocol.Envelope()
        self.assertEqual(data.ver, 1)

    def test_event(self):
        data = protocol.Event()
        self.assertEqual(data.ver, 2)

    def test_event_to_dict(self):
        data = protocol.Event()
        to_dict = {
            "ver": 2,
            "name": "",
            "properties": None,
            "measurements": None,
        }
        self.assertEqual(data.to_dict(), to_dict)

    def test_exception_details(self):
        data = protocol.ExceptionDetails()
        self.assertEqual(data.id, None)

    def test_exception_details_to_dict(self):
        data = protocol.ExceptionDetails()
        to_dict = {
            "id": None,
            "outerId": None,
            "typeName": None,
            "message": None,
            "hasFullStack ": None,
            "stack": None,
            "parsedStack": None,
        }
        self.assertEqual(data.to_dict(), to_dict)

    def test_exception_data(self):
        data = protocol.ExceptionData()
        self.assertEqual(data.ver, 2)

    def test_exception_data_details(self):
        details = protocol.ExceptionDetails()
        data = protocol.ExceptionData(exceptions=[details])
        self.assertEqual(len(data.exceptions), 1)

    def test_exception_data_to_dict(self):
        data = protocol.ExceptionData()
        to_dict = {
            "ver": 2,
            "exceptions": [],
            "severityLevel": None,
            "problemId": None,
            "properties": None,
            "measurements": None,
        }
        self.assertEqual(data.to_dict(), to_dict)

    def test_message(self):
        data = protocol.Message()
        self.assertEqual(data.ver, 2)

    def test_message_to_dict(self):
        data = protocol.Message()
        to_dict = {
            "ver": 2,
            "message": "",
            "severityLevel": None,
            "properties": None,
            "measurements": None,
        }
        self.assertEqual(data.to_dict(), to_dict)

    def test_metric_data(self):
        data = protocol.MetricData()
        self.assertEqual(data.ver, 2)

    def test_remote_dependency(self):
        data = protocol.RemoteDependency()
        self.assertEqual(data.ver, 2)

    def test_request(self):
        data = protocol.Request()
        self.assertEqual(data.ver, 2)

    def test_request_to_dict(self):
        data = protocol.Request()
        to_dict = {
            "ver": 2,
            "id": "",
            "duration": "",
            "responseCode": "",
            "success": True,
            "source": None,
            "name": None,
            "url": None,
            "properties": None,
            "measurements": None,
        }
        self.assertEqual(data.to_dict(), to_dict)
