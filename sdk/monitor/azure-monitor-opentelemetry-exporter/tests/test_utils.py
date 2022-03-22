# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import platform
import unittest

from azure.monitor.opentelemetry.exporter import _utils
from opentelemetry.sdk.resources import Resource

class TestUtils(unittest.TestCase):
    def setUp(self):
        os.environ.clear()
        self._valid_instrumentation_key = (
            "1234abcd-5678-4efa-8abc-1234567890ab"
        )

    def test_nanoseconds_to_duration(self):
        ns_to_duration = _utils.ns_to_duration
        self.assertEqual(ns_to_duration(0), "0.00:00:00.000")
        self.assertEqual(ns_to_duration(1000000), "0.00:00:00.001")
        self.assertEqual(ns_to_duration(1000000000), "0.00:00:01.000")
        self.assertEqual(ns_to_duration(60 * 1000000000), "0.00:01:00.000")
        self.assertEqual(ns_to_duration(3600 * 1000000000), "0.01:00:00.000")
        self.assertEqual(ns_to_duration(86400 * 1000000000), "1.00:00:00.000")

    def test_populate_part_a_fields(self):
        resource = Resource(
            {"service.name": "testServiceName",
             "service.namespace": "testServiceNamespace",
             "service.instance.id": "testServiceInstanceId"})
        tags = _utils._populate_part_a_fields(resource)
        self.assertIsNotNone(tags)
        self.assertEqual(tags.get("ai.cloud.role"), "testServiceNamespace.testServiceName")
        self.assertEqual(tags.get("ai.cloud.roleInstance"), "testServiceInstanceId")
        self.assertEqual(tags.get("ai.internal.nodeName"), "testServiceInstanceId")

    def test_populate_part_a_fields_default(self):
        resource = Resource(
            {"service.name": "testServiceName"})
        tags = _utils._populate_part_a_fields(resource)
        self.assertIsNotNone(tags)
        self.assertEqual(tags.get("ai.cloud.role"), "testServiceName")
        self.assertEqual(tags.get("ai.cloud.roleInstance"), platform.node())
        self.assertEqual(tags.get("ai.internal.nodeName"), tags.get("ai.cloud.roleInstance"))
