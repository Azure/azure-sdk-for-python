# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import unittest
from unittest import mock

from azure.monitor.opentelemetry.exporter.export.trace._sampling import (
    ApplicationInsightsSampler,
    azure_monitor_opentelemetry_sampler_factory,
)

# pylint: disable=protected-access
class TestApplicationInsightsSampler(unittest.TestCase):

    def test_constructor(self):
        sampler = ApplicationInsightsSampler()
        self.assertEqual(sampler._ratio, 1.0)
        self.assertEqual(sampler._sample_rate, 100)

    def test_constructor_ratio(self):
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

    @mock.patch.object(ApplicationInsightsSampler, '_get_DJB2_sample_score')
    def test_should_sample(self, score_mock):
        sampler = ApplicationInsightsSampler(0.75)
        score_mock.return_value = 0.7
        result = sampler.should_sample(None, 0, "test")
        self.assertEqual(result.attributes["_MS.sampleRate"], 75)
        self.assertTrue(result.decision.is_sampled())

    @mock.patch.object(ApplicationInsightsSampler, '_get_DJB2_sample_score')
    def test_should_sample_not_sampled(self, score_mock):
        sampler = ApplicationInsightsSampler(0.5)
        score_mock.return_value = 0.7
        result = sampler.should_sample(None, 0, "test")
        self.assertEqual(result.attributes["_MS.sampleRate"], 50)
        self.assertFalse(result.decision.is_sampled())

    def test_sampler_factory(self):
        sampler = azure_monitor_opentelemetry_sampler_factory("1.0")
        self.assertEqual(sampler._ratio, 1.0)

    def test_sampler_factory_none(self):
        sampler = azure_monitor_opentelemetry_sampler_factory(None)
        self.assertEqual(sampler._ratio, 1.0)

    def test_sampler_factory_empty(self):
        sampler = azure_monitor_opentelemetry_sampler_factory("")
        self.assertEqual(sampler._ratio, 1.0)
