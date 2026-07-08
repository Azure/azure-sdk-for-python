# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import unittest
import datetime
from unittest.mock import patch

from azure.appconfiguration.provider._utils import (
    delay_failure,
    sdk_allowed_kwargs,
    get_startup_backoff,
    _calculate_backoff_duration,
)
from azure.appconfiguration.provider._constants import (
    MAX_STARTUP_BACKOFF_DURATION,
    MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION,
    STARTUP_BACKOFF_INTERVALS,
    JITTER_RATIO,
)


def sleep(seconds):
    assert isinstance(seconds, float)


class TestDelayFailure(unittest.TestCase):
    """Test the delay_failure function."""

    def test_delay_failure_when_enough_time_passed(self):
        """Test that no delay occurs when enough time has passed."""
        start_time = datetime.datetime.now() - datetime.timedelta(seconds=10)
        with patch("time.sleep") as mock_sleep:
            delay_failure(start_time)
            mock_sleep.assert_not_called()

    def test_delay_failure_when_insufficient_time_passed(self):
        """Test that delay occurs when insufficient time has passed."""
        start_time = datetime.datetime.now() - datetime.timedelta(seconds=2)
        with patch("time.sleep") as mock_sleep:
            delay_failure(start_time)
            mock_sleep.assert_called_once()
            # Verify the delay is approximately correct (around 3 seconds)
            called_delay = mock_sleep.call_args[0][0]
            self.assertGreater(called_delay, 2)
            self.assertLess(called_delay, 4)


class TestSdkAllowedKwargs(unittest.TestCase):
    """Test the sdk_allowed_kwargs function."""

    def test_filters_allowed_kwargs(self):
        """Test that only allowed kwargs are returned."""
        kwargs = {
            "headers": {"test": "value"},
            "timeout": 30,
            "invalid_param": "should_be_filtered",
            "user_agent": "test_agent",
            "unknown_param": "filtered_out",
        }
        result = sdk_allowed_kwargs(kwargs)
        expected = {"headers": {"test": "value"}, "timeout": 30, "user_agent": "test_agent"}
        self.assertEqual(result, expected)

    def test_empty_kwargs(self):
        """Test with empty kwargs."""
        result = sdk_allowed_kwargs({})
        self.assertEqual(result, {})


class TestGetFixedBackoff(unittest.TestCase):
    """Test the get_startup_backoff function."""

    def test_within_first_interval(self):
        """Test backoff within first 100 seconds returns 5 seconds."""
        # STARTUP_BACKOFF_INTERVALS[0] = (100, 5)
        backoff, exceeded = get_startup_backoff(0, 1)
        self.assertEqual(backoff, 5)
        self.assertFalse(exceeded)

        backoff, exceeded = get_startup_backoff(50, 1)
        self.assertEqual(backoff, 5)
        self.assertFalse(exceeded)

        backoff, exceeded = get_startup_backoff(99, 1)
        self.assertEqual(backoff, 5)
        self.assertFalse(exceeded)

    def test_within_second_interval(self):
        """Test backoff within 100-200 seconds returns 10 seconds."""
        # STARTUP_BACKOFF_INTERVALS[1] = (200, 10)
        backoff, exceeded = get_startup_backoff(100, 1)
        self.assertEqual(backoff, 10)
        self.assertFalse(exceeded)

        backoff, exceeded = get_startup_backoff(150, 1)
        self.assertEqual(backoff, 10)
        self.assertFalse(exceeded)

        backoff, exceeded = get_startup_backoff(199, 1)
        self.assertEqual(backoff, 10)
        self.assertFalse(exceeded)

    def test_within_third_interval(self):
        """Test backoff within 200-600 seconds returns MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION."""
        # STARTUP_BACKOFF_INTERVALS[2] = (600, MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION)
        backoff, exceeded = get_startup_backoff(200, 1)
        self.assertEqual(backoff, MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION)
        self.assertFalse(exceeded)

        backoff, exceeded = get_startup_backoff(400, 1)
        self.assertEqual(backoff, MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION)
        self.assertFalse(exceeded)

        backoff, exceeded = get_startup_backoff(599, 1)
        self.assertEqual(backoff, MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION)
        self.assertFalse(exceeded)

    def test_beyond_fixed_window_uses_exponential_backoff(self):
        """Test backoff beyond 600 seconds returns exponential backoff based on attempts."""
        # Beyond fixed window, uses _calculate_backoff_duration(attempts)
        # For attempt 1, _calculate_backoff_duration(1) does attempts+=1 -> 2, so jittered(30 * 2^1 = 60)
        backoff, exceeded = get_startup_backoff(600, 1)
        self.assertTrue(exceeded)
        self.assertGreaterEqual(backoff, MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION * (1 - JITTER_RATIO))
        self.assertLessEqual(backoff, 60 * (1 + JITTER_RATIO))

        # For attempt 2, _calculate_backoff_duration(2) does attempts+=1 -> 3, so jittered(30 * 2^2 = 120)
        backoff, exceeded = get_startup_backoff(1000, 2)
        self.assertTrue(exceeded)
        self.assertGreaterEqual(backoff, MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION * (1 - JITTER_RATIO))
        self.assertLessEqual(backoff, 120 * (1 + JITTER_RATIO))

    def test_negative_elapsed_time(self):
        """Test negative elapsed time returns first interval backoff."""
        backoff, exceeded = get_startup_backoff(-1, 1)
        self.assertEqual(backoff, 5)
        self.assertFalse(exceeded)

    def test_boundary_conditions(self):
        """Test exact boundary values."""
        # Test at exact threshold boundaries
        for threshold, expected_backoff in STARTUP_BACKOFF_INTERVALS:
            # Just before threshold should return expected_backoff
            backoff, exceeded = get_startup_backoff(threshold - 0.001, 1)
            self.assertEqual(backoff, expected_backoff)
            self.assertFalse(exceeded)


class TestCalculateBackoffDuration(unittest.TestCase):
    """Test the _calculate_backoff_duration function."""

    def test_first_attempt_returns_min_duration(self):
        """Test that first attempt returns minimum duration."""
        # attempts=0 -> internal attempts=1 after +=1, returns MIN
        result = _calculate_backoff_duration(0)
        self.assertEqual(result, MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION)

    def test_exponential_growth(self):
        """Test that backoff grows exponentially."""
        # Input attempts are shifted by +1 internally
        # For attempts=1, internal=2, calculated = 30 * 2^1 = 60
        result2 = _calculate_backoff_duration(1)
        # Result should be within jitter range of calculated value
        self.assertGreaterEqual(result2, MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION * (1 - JITTER_RATIO))
        self.assertLessEqual(result2, 60 * (1 + JITTER_RATIO))

        # For attempts=2, internal=3, calculated = 30 * 2^2 = 120
        result3 = _calculate_backoff_duration(2)
        self.assertGreaterEqual(result3, MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION * (1 - JITTER_RATIO))
        self.assertLessEqual(result3, 120 * (1 + JITTER_RATIO))

        # For attempts=3, internal=4, calculated = 30 * 2^3 = 240
        result4 = _calculate_backoff_duration(3)
        self.assertGreaterEqual(result4, MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION * (1 - JITTER_RATIO))
        self.assertLessEqual(result4, 240 * (1 + JITTER_RATIO))

    def test_caps_at_max_duration(self):
        """Test that backoff is capped at max duration."""
        # For attempts=5, internal=6, calculated = 30 * 2^5 = 960, but should cap at MAX_STARTUP_BACKOFF_DURATION (600)
        result = _calculate_backoff_duration(5)
        self.assertLessEqual(result, MAX_STARTUP_BACKOFF_DURATION * (1 + JITTER_RATIO))

    def test_invalid_attempts_raises_error(self):
        """Test that attempts < 1 raises ValueError."""
        # Input -1 -> internal 0, which is < 1
        with self.assertRaises(ValueError) as context:
            _calculate_backoff_duration(-1)
        self.assertIn("Number of attempts must be at least 1", str(context.exception))

        with self.assertRaises(ValueError):
            _calculate_backoff_duration(-2)

    def test_very_large_attempts_does_not_overflow(self):
        """Test that very large attempt numbers don't cause overflow."""
        # Should not raise an exception and should return a reasonable value
        result = _calculate_backoff_duration(100)
        self.assertGreater(result, 0)
        self.assertLessEqual(result, MAX_STARTUP_BACKOFF_DURATION * (1 + JITTER_RATIO))


class TestDelayFailureProvider(unittest.TestCase):
    """Test delay_failure as used by the provider."""

    @patch("time.sleep", side_effect=sleep)
    def test_delay_failure(self, mock_sleep):
        start_time = datetime.datetime.now()
        delay_failure(start_time)
        assert mock_sleep.call_count == 1

        mock_sleep.reset_mock()
        start_time = datetime.datetime.now() - datetime.timedelta(seconds=10)
        delay_failure(start_time)
        mock_sleep.assert_not_called()
