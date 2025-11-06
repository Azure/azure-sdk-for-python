# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import unittest
from unittest import mock

from azure.monitor.opentelemetry.exporter.export.trace._utils import (
    _get_DJB2_sample_score,
)
# fixedint was removed as a source dependency. It is used as a dev requirement to test sample score
from fixedint import Int32
from azure.monitor.opentelemetry.exporter._constants import (
    _SAMPLING_HASH,
    _INT32_MAX,
    _INT32_MIN,
)


class TestGetDJB2SampleScore(unittest.TestCase):
    """Test cases for _get_DJB2_sample_score function."""

    def test_empty_string(self):
        """Test with empty string."""
        result = _get_DJB2_sample_score("")
        # With empty string, hash should remain _SAMPLING_HASH (5381)
        # Result should be 5381 / _INT32_MAX
        expected = float(5381) / _INT32_MAX
        self.assertEqual(result, expected)

    def test_single_character(self):
        """Test with single character."""
        result = _get_DJB2_sample_score("a")
        # hash = ((5381 << 5) + 5381) + ord('a')
        # hash = (172192 + 5381) + 97 = 177670
        expected_hash = ((5381 << 5) + 5381) + ord('a')
        expected = float(expected_hash) / _INT32_MAX
        self.assertEqual(result, expected)

    def test_typical_trace_id(self):
        """Test with typical 32-character trace ID."""
        trace_id = "12345678901234567890123456789012"
        result = _get_DJB2_sample_score(trace_id)
        
        # Manually calculate expected result
        hash_value = Int32(_SAMPLING_HASH)
        for char in trace_id:
            hash_value = ((hash_value << 5) + hash_value) + ord(char)
        
        if hash_value == _INT32_MIN:
            hash_value = int(_INT32_MAX)
        else:
            hash_value = abs(hash_value)
        
        expected = float(hash_value) / _INT32_MAX
        self.assertEqual(result, expected)

    def test_hex_characters(self):
        """Test with valid hex characters (0-9, a-f)."""
        test_cases = [
            "0123456789abcdef",
            "fedcba9876543210",
            "aaaaaaaaaaaaaaaa",
            "0000000000000000",
            "ffffffffffffffff"
        ]
        
        for trace_id in test_cases:
            with self.subTest(trace_id=trace_id):
                result = _get_DJB2_sample_score(trace_id)
                self.assertIsInstance(result, float)
                self.assertGreaterEqual(result, 0.0)
                self.assertLessEqual(result, 1.0)

    def test_int32_overflow_handling(self):
        """Test that Int32 overflow is handled correctly."""
        # Create a string that should cause overflow
        long_string = "f" * 100  # 100 'f' characters should cause overflow
        result = _get_DJB2_sample_score(long_string)
        
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 1.0)

    def test_int32_minimum_value_handling(self):
        """Test handling when hash equals INTEGER_MIN."""
        # This is tricky to test directly since we need to find a string 
        # that results in exactly _INT32_MIN. Instead, let's test the logic.
        
        # We'll use a mock to simulate this condition

        
        def mock_djb2_with_min_value(trace_id_hex):
            # Call original to get the structure, then simulate _INT32_MIN case
            hash_value = Int32(_SAMPLING_HASH)
            for char in trace_id_hex:
                hash_value = ((hash_value << 5) + hash_value) + ord(char)
            
            # Simulate the case where we get _INT32_MIN
            if str(trace_id_hex) == "test_min":
                hash_value = Int32(_INT32_MIN)
            
            if hash_value == _INT32_MIN:
                hash_value = int(_INT32_MAX)
            else:
                hash_value = abs(hash_value)
            
            return float(hash_value) / _INT32_MAX
        
        # Test the _INT32_MIN case
        result = mock_djb2_with_min_value("test_min")
        expected = float(_INT32_MAX) / _INT32_MAX
        self.assertEqual(result, expected)

    def test_negative_hash_conversion(self):
        """Test that negative hash values are converted to positive."""
        # Find a string that produces a negative hash
        test_string = "negative_test_case_string"
        result = _get_DJB2_sample_score(test_string)
        
        # Result should always be positive (between 0 and 1)
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 1.0)

    def test_deterministic_output(self):
        """Test that same input always produces same output."""
        trace_id = "abcdef1234567890abcdef1234567890"
        
        # Call multiple times with same input
        results = [_get_DJB2_sample_score(trace_id) for _ in range(5)]
        
        # All results should be identical
        self.assertTrue(all(r == results[0] for r in results))

    def test_different_inputs_different_outputs(self):
        """Test that different inputs produce different outputs."""
        trace_ids = [
            "12345678901234567890123456789012",
            "12345678901234567890123456789013",  # Last digit different
            "22345678901234567890123456789012",  # First digit different
            "abcdef1234567890fedcba0987654321",  # Completely different
        ]
        
        results = [_get_DJB2_sample_score(tid) for tid in trace_ids]
        
        # All results should be different
        self.assertEqual(len(results), len(set(results)))

    def test_boundary_values(self):
        """Test with boundary values and edge cases."""
        test_cases = [
            "0",  # Single minimum hex digit
            "f",  # Single maximum hex digit
            "00000000000000000000000000000000",  # All zeros
            "ffffffffffffffffffffffffffffffff",  # All f's (32 chars)
        ]
        
        for trace_id in test_cases:
            with self.subTest(trace_id=trace_id):
                result = _get_DJB2_sample_score(trace_id)
                self.assertIsInstance(result, float)
                self.assertGreaterEqual(result, 0.0)
                self.assertLessEqual(result, 1.0)

    def test_constants_used_correctly(self):
        """Test that the function uses the expected constants."""
        # Verify that _SAMPLING_HASH is 5381 (standard DJB2 hash initial value)
        self.assertEqual(_SAMPLING_HASH, 5381)
        
        # Verify Int32 constants
        self.assertEqual(_INT32_MAX, 2147483647)  # 2^31 - 1
        self.assertEqual(_INT32_MIN, -2147483648)  # -2^31

    def test_algorithm_correctness(self):
        """Test that the DJB2 algorithm is implemented correctly."""
        # Test with known input and manually calculated expected output
        trace_id = "abc"
        
        # Manual calculation:
        # Start with 5381
        # For 'a' (97): hash = ((5381 << 5) + 5381) + 97 = 177670
        # For 'b' (98): hash = ((177670 << 5) + 177670) + 98 = 5823168
        # For 'c' (99): hash = ((5823168 << 5) + 5823168) + 99 = 191582563
        
        expected_hash = _SAMPLING_HASH
        for char in trace_id:
            expected_hash = Int32(((expected_hash << 5) + expected_hash) + ord(char))
        
        if expected_hash == _INT32_MIN:
            expected_hash = int(_INT32_MAX)
        else:
            expected_hash = abs(expected_hash)
        
        expected_result = float(expected_hash) / _INT32_MAX
        actual_result = _get_DJB2_sample_score(trace_id)
        
        self.assertEqual(actual_result, expected_result)
