# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import random
import sys
import threading
import time
import unittest
from typing import List, Optional
from unittest.mock import patch, Mock

from opentelemetry.context import Context
from opentelemetry.trace import SpanContext, TraceFlags, set_span_in_context
from opentelemetry.trace.span import NonRecordingSpan

from azure.monitor.opentelemetry.exporter.export.trace._rate_limited_sampling import (
    Decision,
    RateLimitedSamplingPercentage,
    RateLimitedSampler,
    SamplingResult,
)

from azure.monitor.opentelemetry.exporter._constants import _SAMPLE_RATE_KEY


def create_parent_span(sampled: bool, sample_rate: Optional[float] = None, is_remote: bool = False):
    trace_flags = TraceFlags(0x01) if sampled else TraceFlags(0x00)

    span_context = SpanContext(
        trace_id=0x1234567890ABCDEF1234567890ABCDEF,
        span_id=0x1234567890ABCDEF,
        is_remote=is_remote,
        trace_flags=trace_flags,
        trace_state=None,
    )

    mock_span = Mock()
    mock_span.get_span_context.return_value = span_context
    mock_span.is_recording.return_value = sampled

    attributes = {}
    if sample_rate is not None:
        attributes[_SAMPLE_RATE_KEY] = sample_rate
    mock_span.attributes = attributes

    return mock_span


class TestRateLimitedSampler(unittest.TestCase):
    def setUp(self):
        # Use a mock for time.time_ns() instead of nano_time_supplier injection
        self.current_time = 1_000_000_000_000  # 1 second in nanoseconds
        self.time_patcher = patch("time.time_ns", side_effect=lambda: self.current_time)
        self.mock_time = self.time_patcher.start()

    def tearDown(self):
        self.time_patcher.stop()

    def advance_time(self, nanoseconds_increment: int):
        self.current_time += nanoseconds_increment

    def get_current_time_nanoseconds(self) -> int:
        return self.current_time

    # Test sampling behavior with a high target rate and moderate span frequency
    def test_constant_rate_sampling(self):
        target_rate = 1000.0
        sampler = RateLimitedSampler(target_rate)

        # Reset initial state to use our controlled time
        from azure.monitor.opentelemetry.exporter.export.trace._rate_limited_sampling import _State

        initial_time = self.current_time
        sampler._sampling_percentage_generator._state = _State(0.0, 0.0, initial_time)
        sampler._sampling_percentage_generator._round_to_nearest = False

        nanoseconds_between_spans = 10_000_000
        num_spans = 10
        sampled_count = 0

        for i in range(num_spans):
            self.advance_time(nanoseconds_between_spans)

            result = sampler.should_sample(parent_context=None, trace_id=i, name=f"test-span-{i}")

            self.assertIsInstance(result, SamplingResult)
            self.assertIn(result.decision, [Decision.RECORD_AND_SAMPLE, Decision.DROP])

            # Check if _SAMPLE_RATE_KEY is present only when sampling percentage is not 100%
            sampling_percentage = sampler._sampling_percentage_generator.get()
            if sampling_percentage != 100.0:
                self.assertIn(_SAMPLE_RATE_KEY, result.attributes)

            if result.decision == Decision.RECORD_AND_SAMPLE:
                sampled_count += 1

        self.assertGreater(sampled_count, 0, "Should sample some spans with high target rate")

    # Test throttling behavior under high volume of spans with low target rate
    def test_high_volume_sampling(self):
        target_rate = 5.0
        sampler = RateLimitedSampler(target_rate)

        # Reset initial state to use our controlled time
        from azure.monitor.opentelemetry.exporter.export.trace._rate_limited_sampling import _State

        initial_time = self.current_time
        sampler._sampling_percentage_generator._state = _State(0.0, 0.0, initial_time)

        nanoseconds_between_spans = 1_000_000
        num_spans = 500
        sampled_count = 0

        import random

        random.seed(42)
        trace_ids = [random.getrandbits(128) for _ in range(num_spans)]

        for i in range(num_spans):
            self.advance_time(nanoseconds_between_spans)

            result = sampler.should_sample(parent_context=None, trace_id=trace_ids[i], name=f"high-volume-span-{i}")

            if result.decision == Decision.RECORD_AND_SAMPLE:
                sampled_count += 1

        self.assertGreater(sampled_count, 0, "Should sample at least some spans even under high load")
        self.assertLess(sampled_count, num_spans * 0.1, "Should throttle significantly under high load")

    # Test adaptive sampling when span arrival rate increases over time
    def test_rate_adaptation_increasing_load(self):
        target_rate = 20.0
        sampler = RateLimitedSampler(target_rate)

        # Reset initial state to use our controlled time
        from azure.monitor.opentelemetry.exporter.export.trace._rate_limited_sampling import _State

        initial_time = self.current_time
        sampler._sampling_percentage_generator._state = _State(0.0, 0.0, initial_time)

        low_rate_interval = 20_000_000
        phase1_spans = 100

        high_rate_interval = 2_000_000
        phase2_spans = 1000

        sampled_phase1 = 0
        sampled_phase2 = 0

        import random

        random.seed(123)
        trace_ids_phase1 = [random.getrandbits(128) for _ in range(phase1_spans)]
        trace_ids_phase2 = [random.getrandbits(128) for _ in range(phase2_spans)]

        for i in range(phase1_spans):
            self.advance_time(low_rate_interval)
            result = sampler.should_sample(None, trace_ids_phase1[i], f"low-{i}")
            if result.decision == Decision.RECORD_AND_SAMPLE:
                sampled_phase1 += 1

        for i in range(phase2_spans):
            self.advance_time(high_rate_interval)
            result = sampler.should_sample(None, trace_ids_phase2[i], f"high-{i}")
            if result.decision == Decision.RECORD_AND_SAMPLE:
                sampled_phase2 += 1

        self.assertGreater(sampled_phase1, 0, "Should sample in low rate phase")
        self.assertGreater(sampled_phase2, 0, "Should sample in high rate phase")

        phase1_percentage = (sampled_phase1 / phase1_spans) * 100
        phase2_percentage = (sampled_phase2 / phase2_spans) * 100

        self.assertLess(phase2_percentage, phase1_percentage, "Sampling percentage should decrease under high load")

    # Test sampler instantiation with various target rates and description format
    def test_sampler_creation(self):
        for target_rate in [0.1, 0.5, 1.0, 5.0, 100.0]:
            sampler = RateLimitedSampler(target_rate)
            self.assertIsInstance(sampler, RateLimitedSampler)
            self.assertEqual(sampler.get_description(), f"RateLimitedSampler{{{target_rate}}}")

    # Test that negative target rates raise a ValueError
    def test_negative_rate_raises_error(self):
        with self.assertRaises(ValueError):
            RateLimitedSampler(-1.0)

    # Test sampling behavior with zero target rate
    def test_zero_rate_sampling(self):
        sampler = RateLimitedSampler(0.0)

        for i in range(100):
            result = sampler.should_sample(parent_context=None, trace_id=i, name="test-span")

            self.assertIsInstance(result, SamplingResult)
            self.assertIn(result.decision, [Decision.RECORD_AND_SAMPLE, Decision.DROP])
            self.assertIn(_SAMPLE_RATE_KEY, result.attributes)

    # Test that the same trace ID produces consistent sampling decisions
    def test_sampling_decision_consistency(self):
        sampler = RateLimitedSampler(50.0)

        trace_id = 12345

        results = []
        for _ in range(10):
            result = sampler.should_sample(parent_context=None, trace_id=trace_id, name="test-span")
            results.append(result)

        first_decision = results[0].decision
        for result in results[1:]:
            self.assertEqual(
                result.decision, first_decision, "Sampling decision should be consistent for same trace ID"
            )

    # Test that sampling results include valid sample rate attributes
    def test_sampling_attributes(self):
        sampler = RateLimitedSampler(25.0)

        result = sampler.should_sample(parent_context=None, trace_id=123, name="test-span")

        self.assertIsInstance(result, SamplingResult)

        # Check if _SAMPLE_RATE_KEY is present only when sampling percentage is not 100%
        sampling_percentage = sampler._sampling_percentage_generator.get()
        if sampling_percentage != 100.0:
            self.assertIn(_SAMPLE_RATE_KEY, result.attributes)
            sample_rate = result.attributes[_SAMPLE_RATE_KEY]
            self.assertIsInstance(sample_rate, (int, float))
            if isinstance(sample_rate, (int, float)):
                self.assertGreaterEqual(float(sample_rate), 0.0)
                self.assertLessEqual(float(sample_rate), 100.0)

    # Test sampling behavior with edge case trace ID values
    def test_sampler_with_extreme_trace_ids(self):
        sampler = RateLimitedSampler(1.0)

        extreme_trace_ids = [
            0,
            1,
            2**32 - 1,
            2**64 - 1,
            0xABCDEF123456789,
        ]

        for trace_id in extreme_trace_ids:
            with self.subTest(trace_id=trace_id):
                result = sampler.should_sample(parent_context=None, trace_id=trace_id, name="test-span")

                self.assertIsInstance(result, SamplingResult)
                self.assertIn(result.decision, [Decision.RECORD_AND_SAMPLE, Decision.DROP])

                # Check if _SAMPLE_RATE_KEY is present only when sampling percentage is not 100%
                sampling_percentage = sampler._sampling_percentage_generator.get()
                if sampling_percentage != 100.0:
                    self.assertIn(_SAMPLE_RATE_KEY, result.attributes)
                    sample_rate = result.attributes[_SAMPLE_RATE_KEY]
                    self.assertIsInstance(sample_rate, (int, float))
                    if isinstance(sample_rate, (int, float)):
                        self.assertGreaterEqual(float(sample_rate), 0.0)
                        self.assertLessEqual(float(sample_rate), 100.0)

    # Test that sampler is thread-safe under concurrent access
    def test_thread_safety(self):
        sampler = RateLimitedSampler(10.0)
        results = []
        errors = []

        def worker():
            try:
                for i in range(50):
                    result = sampler.should_sample(None, i, f"thread-span-{i}")
                    results.append(result)
                    time.sleep(0.001)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(5)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        self.assertEqual(len(errors), 0, f"Thread safety errors: {errors}")
        self.assertGreater(len(results), 0)
        for result in results:
            self.assertIsInstance(result, SamplingResult)
            self.assertIn(result.decision, [Decision.RECORD_AND_SAMPLE, Decision.DROP])
            # Note: We can't easily check sampling percentage here since it's from multiple threads
            # Just verify that if _SAMPLE_RATE_KEY exists, it's valid
            if _SAMPLE_RATE_KEY in result.attributes:
                sample_rate = result.attributes[_SAMPLE_RATE_KEY]
                self.assertIsInstance(sample_rate, (int, float))

    # Test inheriting sampling decision from sampled parent span with sample rate
    def test_parent_span_sampled_with_sample_rate(self):
        sampler = RateLimitedSampler(10.0)

        parent_span = create_parent_span(sampled=True, sample_rate=75.0, is_remote=False)

        with patch(
            "azure.monitor.opentelemetry.exporter.export.trace._utils.get_current_span", return_value=parent_span
        ):
            context = Mock()

            result = sampler.should_sample(parent_context=context, trace_id=0xABC123, name="test-span")

            self.assertEqual(result.decision, Decision.RECORD_AND_SAMPLE)
            self.assertEqual(result.attributes[_SAMPLE_RATE_KEY], 75.0)

    # Test inheriting sampling decision from non-sampled parent span with sample rate
    def test_parent_span_not_sampled_with_sample_rate(self):
        sampler = RateLimitedSampler(10.0)

        parent_span = create_parent_span(sampled=False, sample_rate=25.0, is_remote=False)

        with patch(
            "azure.monitor.opentelemetry.exporter.export.trace._utils.get_current_span", return_value=parent_span
        ):
            context = Mock()

            result = sampler.should_sample(parent_context=context, trace_id=0xABC123, name="test-span")

            self.assertEqual(result.decision, Decision.DROP)
            self.assertEqual(result.attributes[_SAMPLE_RATE_KEY], 0.0)

    # Test parent span with 100% sample rate maintains decision
    def test_parent_span_sampled_with_100_percent_sample_rate(self):
        sampler = RateLimitedSampler(5.0)

        parent_span = create_parent_span(sampled=True, sample_rate=100.0, is_remote=False)

        with patch(
            "azure.monitor.opentelemetry.exporter.export.trace._utils.get_current_span", return_value=parent_span
        ):
            context = Mock()

            result = sampler.should_sample(parent_context=context, trace_id=0xABC123, name="test-span")

            self.assertEqual(result.decision, Decision.RECORD_AND_SAMPLE)
            self.assertEqual(result.attributes[_SAMPLE_RATE_KEY], 100.0)

    # Test that remote parent spans are ignored for sampling decisions
    def test_parent_span_remote_ignored(self):
        sampler = RateLimitedSampler(5.0)

        parent_span = create_parent_span(sampled=True, sample_rate=80.0, is_remote=True)

        with patch(
            "azure.monitor.opentelemetry.exporter.export.trace._utils.get_current_span", return_value=parent_span
        ):
            context = Mock()

            from azure.monitor.opentelemetry.exporter.export.trace._rate_limited_sampling import _State

            initial_time = self.current_time
            sampler._sampling_percentage_generator._state = _State(0.0, 0.0, initial_time)

            self.advance_time(100_000_000)

            result = sampler.should_sample(parent_context=context, trace_id=0xABC123, name="test-span")

            self.assertNotEqual(result.attributes[_SAMPLE_RATE_KEY], 80.0)

    # Test parent span without sample rate attribute uses local sampling
    def test_parent_span_no_sample_rate_attribute(self):
        sampler = RateLimitedSampler(5.0)

        parent_span = create_parent_span(sampled=True, sample_rate=None, is_remote=False)

        with patch(
            "azure.monitor.opentelemetry.exporter.export.trace._utils.get_current_span", return_value=parent_span
        ):
            context = Mock()

            from azure.monitor.opentelemetry.exporter.export.trace._rate_limited_sampling import _State

            initial_time = self.current_time
            sampler._sampling_percentage_generator._state = _State(0.0, 0.0, initial_time)

            self.advance_time(100_000_000)

            result = sampler.should_sample(parent_context=context, trace_id=0xABC123, name="test-span")

            self.assertIn(result.decision, [Decision.RECORD_AND_SAMPLE, Decision.DROP])
            sample_rate = result.attributes[_SAMPLE_RATE_KEY]
            self.assertIsInstance(sample_rate, (int, float))

    # Test handling parent span with invalid span context
    def test_parent_span_invalid_context(self):
        sampler = RateLimitedSampler(5.0)

        parent_span = Mock()
        invalid_context = Mock()
        invalid_context.is_valid = False
        invalid_context.is_remote = False
        parent_span.get_span_context.return_value = invalid_context

        with patch(
            "azure.monitor.opentelemetry.exporter.export.trace._utils.get_current_span", return_value=parent_span
        ):
            context = Mock()

            from azure.monitor.opentelemetry.exporter.export.trace._rate_limited_sampling import _State

            initial_time = self.current_time
            sampler._sampling_percentage_generator._state = _State(0.0, 0.0, initial_time)

            self.advance_time(100_000_000)

            result = sampler.should_sample(parent_context=context, trace_id=0xABC123, name="test-span")

            self.assertIn(result.decision, [Decision.RECORD_AND_SAMPLE, Decision.DROP])
            sample_rate = result.attributes[_SAMPLE_RATE_KEY]
            self.assertIsInstance(sample_rate, (int, float))

    # Test sampling behavior when no parent context is provided
    def test_no_parent_context_uses_local_sampling(self):
        sampler = RateLimitedSampler(5.0)

        from azure.monitor.opentelemetry.exporter.export.trace._rate_limited_sampling import _State

        initial_time = self.current_time
        sampler._sampling_percentage_generator._state = _State(0.0, 0.0, initial_time)

        self.advance_time(100_000_000)

        result = sampler.should_sample(parent_context=None, trace_id=0xABC123, name="test-span")

        self.assertIn(result.decision, [Decision.RECORD_AND_SAMPLE, Decision.DROP])
        sample_rate = result.attributes[_SAMPLE_RATE_KEY]
        self.assertIsInstance(sample_rate, (int, float))

    # Test that original span attributes are preserved in sampling result
    def test_parent_context_preserves_original_attributes(self):
        sampler = RateLimitedSampler(10.0)

        parent_span = create_parent_span(sampled=True, sample_rate=50.0, is_remote=False)

        with patch(
            "azure.monitor.opentelemetry.exporter.export.trace._utils.get_current_span", return_value=parent_span
        ):
            context = Mock()

            original_attributes = {"service.name": "test-service", "operation.name": "test-operation"}

            result = sampler.should_sample(
                parent_context=context, trace_id=0xABC123, name="test-span", attributes=original_attributes
            )

            self.assertEqual(result.decision, Decision.RECORD_AND_SAMPLE)
            self.assertEqual(result.attributes["service.name"], "test-service")
            self.assertEqual(result.attributes["operation.name"], "test-operation")
            self.assertEqual(result.attributes[_SAMPLE_RATE_KEY], 50.0)


class TestUtilityFunctions(unittest.TestCase):
    # Test that DJB2 hash produces consistent results for the same input
    def test_djb2_hash_consistency(self):
        from azure.monitor.opentelemetry.exporter.export.trace._utils import _get_DJB2_sample_score

        trace_id = "test-trace-id-12345"

        scores = [_get_DJB2_sample_score(trace_id) for _ in range(10)]

        self.assertTrue(all(score == scores[0] for score in scores))

    # Test DJB2 hash function with edge case inputs
    def test_djb2_hash_edge_cases(self):
        from azure.monitor.opentelemetry.exporter.export.trace._utils import _get_DJB2_sample_score

        edge_cases = [
            "",
            "0",
            "a" * 1000,
            "0123456789abcdef" * 8,
        ]

        for trace_id in edge_cases:
            with self.subTest(trace_id=trace_id):
                score = _get_DJB2_sample_score(trace_id)
                self.assertIsInstance(score, float)
                self.assertGreaterEqual(score, 0)
                self.assertLess(score, 100)
