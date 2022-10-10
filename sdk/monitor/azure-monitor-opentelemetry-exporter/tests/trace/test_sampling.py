# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import unittest

from azure.monitor.opentelemetry.exporter.export.trace._sampling import (
    ApplicationInsightsSampler,
)

# pylint: disable=protected-access
class TestApplicationInsightsSampler(unittest.TestCase):

    def test_constructor(self):
        sampler = ApplicationInsightsSampler(0.75)
        self.assertEqual(sampler._ratio, 0.75)
        self.assertEqual(sampler._sample_rate, 75)

    def test_invalid_ratio(self):
        self.assertRaises(
            ValueError, lambda: ApplicationInsightsSampler(1.01)
        )
        self.assertRaises(
            ValueError, lambda: ApplicationInsightsSampler(-0.01)
        )
