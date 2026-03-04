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
        # Invalid explicit ratio logs an error and defaults to 1.0 instead of raising
        sampler = ApplicationInsightsSampler(1.01)
        self.assertEqual(sampler._ratio, 1.0)
        self.assertEqual(sampler._sample_rate, 100.0)
        sampler = ApplicationInsightsSampler(-0.01)
        self.assertEqual(sampler._ratio, 1.0)
        self.assertEqual(sampler._sample_rate, 100.0)
    
    def test_user_passed_value_through_distro(self):
        sampler = ApplicationInsightsSampler(sampling_ratio=0.5)
        self.assertEqual(sampler._ratio, 0.5)
        self.assertEqual(sampler._sample_rate, 50.0)

    def test_constructor_sampler_arg(self):
        with mock.patch.dict("os.environ", {"OTEL_TRACES_SAMPLER_ARG": "0.5"}):
            sampler = ApplicationInsightsSampler()
            self.assertEqual(sampler._ratio, 0.5)
            self.assertEqual(sampler._sample_rate, 50.0)

    def test_constructor_explicit_ratio_ignores_sampler_arg(self):
        # Explicit ratio passed from distro takes priority over env var
        with mock.patch.dict("os.environ", {"OTEL_TRACES_SAMPLER_ARG": "0.3"}):
            sampler = ApplicationInsightsSampler(0.75)
            self.assertEqual(sampler._ratio, 0.75)
            self.assertEqual(sampler._sample_rate, 75.0)

    def test_constructor_sampler_arg_invalid_range(self):
        # Invalid env var with no explicit ratio falls back to 1.0
        with mock.patch.dict("os.environ", {"OTEL_TRACES_SAMPLER_ARG": "1.5"}):
            sampler = ApplicationInsightsSampler()
            self.assertEqual(sampler._ratio, 1.0)
            self.assertEqual(sampler._sample_rate, 100.0)

    def test_constructor_sampler_arg_invalid_float(self):
        # Non-numeric env var with no explicit ratio falls back to 1.0
        with mock.patch.dict("os.environ", {"OTEL_TRACES_SAMPLER_ARG": "not_a_number"}):
            sampler = ApplicationInsightsSampler()
            self.assertEqual(sampler._ratio, 1.0)
            self.assertEqual(sampler._sample_rate, 100.0)

    @mock.patch("azure.monitor.opentelemetry.exporter.export.trace._sampling._get_DJB2_sample_score")
    def test_should_sample(self, score_mock):
        sampler = ApplicationInsightsSampler(0.75)
        score_mock.return_value = 0.7
        result = sampler.should_sample(None, 0, "test")
        self.assertEqual(result.attributes["_MS.sampleRate"], 75)
        self.assertTrue(result.decision.is_sampled())

    @mock.patch("azure.monitor.opentelemetry.exporter.export.trace._sampling._get_DJB2_sample_score")
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
