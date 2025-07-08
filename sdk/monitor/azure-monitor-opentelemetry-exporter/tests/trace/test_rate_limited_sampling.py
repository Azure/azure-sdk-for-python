# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import random
import sys
import threading
import time
import unittest
from typing import List
from unittest.mock import patch

from azure.monitor.opentelemetry.exporter.export.trace._rate_limited_sampling import (
    Decision,
    RateLimitedSamplingPercentage,
    RateLimitedSampler,
    SamplingResult,
)

from azure.monitor.opentelemetry.exporter._constants import _SAMPLE_RATE_KEY


class TestRateLimitedSampler(unittest.TestCase):
    
    def setUp(self):
        self.nano_time = [1_000_000_000_000] 
        self.nano_time_supplier = lambda: self.nano_time[0]
    
    def advance_time(self, nanos_increment: int):
        self.nano_time[0] += nanos_increment
    
    def get_current_time_nanos(self) -> int:
        return self.nano_time[0]
    
    def test_constant_rate_sampling(self):
        target_rate = 1000.0
        sampler = RateLimitedSampler(target_rate)

        sampler._sampling_percentage_generator._nano_time_supplier = self.nano_time_supplier
        from azure.monitor.opentelemetry.exporter.export.trace._rate_limited_sampling import _State
        initial_time = self.nano_time_supplier()
        sampler._sampling_percentage_generator._state = _State(0.0, 0.0, initial_time)
        sampler._sampling_percentage_generator._round_to_nearest = False

        nanos_between_spans = 10_000_000
        num_spans = 10
        sampled_count = 0

        for i in range(num_spans):
            self.advance_time(nanos_between_spans)

            result = sampler.should_sample(
                parent_context=None,
                trace_id=i,
                name=f"test-span-{i}"
            )

            self.assertIsInstance(result, SamplingResult)
            self.assertIn(result.decision, [Decision.RECORD_AND_SAMPLE, Decision.DROP])
            self.assertIn(_SAMPLE_RATE_KEY, result.attributes)

            if result.decision == Decision.RECORD_AND_SAMPLE:
                sampled_count += 1

        self.assertGreater(sampled_count, 0, "Should sample some spans with high target rate")

    def test_high_volume_sampling(self):
        target_rate = 5.0
        sampler = RateLimitedSampler(target_rate)

        sampler._sampling_percentage_generator._nano_time_supplier = self.nano_time_supplier
        from azure.monitor.opentelemetry.exporter.export.trace._rate_limited_sampling import _State
        initial_time = self.nano_time_supplier()
        sampler._sampling_percentage_generator._state = _State(0.0, 0.0, initial_time)

        nanos_between_spans = 1_000_000
        num_spans = 500
        sampled_count = 0

        import random
        random.seed(42)
        trace_ids = [random.getrandbits(128) for _ in range(num_spans)]

        for i in range(num_spans):
            self.advance_time(nanos_between_spans)

            result = sampler.should_sample(
                parent_context=None,
                trace_id=trace_ids[i],
                name=f"high-volume-span-{i}"
            )

            if result.decision == Decision.RECORD_AND_SAMPLE:
                sampled_count += 1

        self.assertGreater(sampled_count, 0, "Should sample at least some spans even under high load")
        self.assertLess(sampled_count, num_spans * 0.1, "Should throttle significantly under high load")

    def test_rate_adaptation_increasing_load(self):
        target_rate = 20.0
        sampler = RateLimitedSampler(target_rate)
        sampler._sampling_percentage_generator._nano_time_supplier = self.nano_time_supplier
        from azure.monitor.opentelemetry.exporter.export.trace._rate_limited_sampling import _State
        initial_time = self.nano_time_supplier()
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

        self.assertLess(phase2_percentage, phase1_percentage,
                       "Sampling percentage should decrease under high load")
    
    def test_sampler_creation(self):
        for target_rate in [0.1, 0.5, 1.0, 5.0, 100.0]:
            sampler = RateLimitedSampler(target_rate)
            self.assertIsInstance(sampler, RateLimitedSampler)
            self.assertEqual(
                sampler.get_description(),
                f"RateLimitedSampler{{{target_rate}}}"
            )
    
    def test_negative_rate_raises_error(self):
        with self.assertRaises(ValueError):
            RateLimitedSampler(-1.0)
    
    def test_zero_rate_sampling(self):
        sampler = RateLimitedSampler(0.0)
        
        for i in range(100):
            result = sampler.should_sample(
                parent_context=None,
                trace_id=i,
                name="test-span"
            )
            
            self.assertIsInstance(result, SamplingResult)
            self.assertIn(result.decision, [Decision.RECORD_AND_SAMPLE, Decision.DROP])
            self.assertIn(_SAMPLE_RATE_KEY, result.attributes)
    
    def test_sampling_decision_consistency(self):
        sampler = RateLimitedSampler(50.0)
        
        trace_id = 12345
        
        results = []
        for _ in range(10):
            result = sampler.should_sample(
                parent_context=None,
                trace_id=trace_id,
                name="test-span"
            )
            results.append(result)
        
        first_decision = results[0].decision
        for result in results[1:]:
            self.assertEqual(result.decision, first_decision, 
                           "Sampling decision should be consistent for same trace ID")
    
    def test_sampling_attributes(self):
        sampler = RateLimitedSampler(25.0)
        
        result = sampler.should_sample(
            parent_context=None,
            trace_id=123,
            name="test-span"
        )
        
        self.assertIsInstance(result, SamplingResult)
        self.assertIn(_SAMPLE_RATE_KEY, result.attributes)
        
        sample_rate = result.attributes[_SAMPLE_RATE_KEY]
        self.assertIsInstance(sample_rate, (int, float))
        if isinstance(sample_rate, (int, float)):
            self.assertGreaterEqual(float(sample_rate), 0.0)
            self.assertLessEqual(float(sample_rate), 100.0)
    
    def test_sampler_with_extreme_trace_ids(self):
        sampler = RateLimitedSampler(1.0)
        
        extreme_trace_ids = [
            0,
            1,
            2**32 - 1,
            2**64 - 1,
            0xabcdef123456789,
        ]
        
        for trace_id in extreme_trace_ids:
            with self.subTest(trace_id=trace_id):
                result = sampler.should_sample(
                    parent_context=None,
                    trace_id=trace_id,
                    name="test-span"
                )
                
                self.assertIsInstance(result, SamplingResult)
                self.assertIn(result.decision, [Decision.RECORD_AND_SAMPLE, Decision.DROP])
                self.assertIn(_SAMPLE_RATE_KEY, result.attributes)
                
                sample_rate = result.attributes[_SAMPLE_RATE_KEY]
                self.assertIsInstance(sample_rate, (int, float))
                if isinstance(sample_rate, (int, float)):
                    self.assertGreaterEqual(float(sample_rate), 0.0)
                    self.assertLessEqual(float(sample_rate), 100.0)
    
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
            self.assertIn(_SAMPLE_RATE_KEY, result.attributes)


class TestUtilityFunctions(unittest.TestCase):
    
    def test_djb2_hash_consistency(self):
        from azure.monitor.opentelemetry.exporter.export.trace._utils import _get_djb2_sample_score
        
        trace_id = "test-trace-id-12345"
        
        scores = [_get_djb2_sample_score(trace_id) for _ in range(10)]
        
        self.assertTrue(all(score == scores[0] for score in scores))
    
    def test_djb2_hash_edge_cases(self):
        from azure.monitor.opentelemetry.exporter.export.trace._utils import _get_djb2_sample_score
        
        edge_cases = [
            "",
            "0",
            "a" * 1000,
            "0123456789abcdef" * 8,
        ]
        
        for trace_id in edge_cases:
            with self.subTest(trace_id=trace_id):
                score = _get_djb2_sample_score(trace_id)
                self.assertIsInstance(score, float)
                self.assertGreaterEqual(score, 0)
                self.assertLess(score, 100)



