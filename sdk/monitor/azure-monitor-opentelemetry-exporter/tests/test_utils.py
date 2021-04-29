# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import unittest

from azure.monitor.opentelemetry.exporter import _utils


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
