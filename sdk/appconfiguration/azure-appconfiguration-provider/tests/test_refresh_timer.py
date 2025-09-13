# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import unittest
import time

from azure.appconfiguration.provider._refresh_timer import RefreshTimer


class TestRefreshTimer(unittest.TestCase):
    """Test the RefreshTimer class."""

    def test_default_initialization(self):
        """Test default initialization."""
        timer = RefreshTimer()
        self.assertEqual(timer._interval, 30)
        self.assertEqual(timer._attempts, 1)
        self.assertEqual(timer._min_backoff, 30)
        self.assertEqual(timer._max_backoff, 30)

    def test_custom_initialization(self):
        """Test custom initialization."""
        timer = RefreshTimer(refresh_interval=60, min_backoff=10, max_backoff=300)
        self.assertEqual(timer._interval, 60)
        self.assertEqual(timer._min_backoff, 10)
        # max_backoff is constrained by the interval, so it should be 60, not 300
        self.assertEqual(timer._max_backoff, 60)

    def test_invalid_refresh_interval_raises_error(self):
        """Test that invalid refresh interval raises ValueError."""
        with self.assertRaises(ValueError):
            RefreshTimer(refresh_interval=0)

    def test_needs_refresh_initially_false(self):
        """Test that needs_refresh is initially false."""
        timer = RefreshTimer(refresh_interval=1)
        self.assertFalse(timer.needs_refresh())

    def test_needs_refresh_after_interval(self):
        """Test that needs_refresh becomes true after interval."""
        timer = RefreshTimer(refresh_interval=1)
        # Manually set the next refresh time to the past
        timer._next_refresh_time = time.time() - 1
        self.assertTrue(timer.needs_refresh())

    def test_reset_functionality(self):
        """Test the reset functionality."""
        timer = RefreshTimer(refresh_interval=1)
        timer._attempts = 5
        timer.reset()
        self.assertEqual(timer._attempts, 1)
        # Next refresh time should be reset to future
        self.assertGreater(timer._next_refresh_time, time.time())

    def test_backoff_increases_attempts(self):
        """Test that backoff increases attempts."""
        timer = RefreshTimer(refresh_interval=60, min_backoff=1, max_backoff=60)
        initial_attempts = timer._attempts
        timer.backoff()
        self.assertEqual(timer._attempts, initial_attempts + 1)
        self.assertGreater(timer._next_refresh_time, time.time())

    def test_calculate_backoff_progression(self):
        """Test that backoff calculation progresses correctly."""
        timer = RefreshTimer(refresh_interval=60, min_backoff=1, max_backoff=60)

        # Test multiple backoff calculations to verify exponential progression
        # Since backoff includes randomization, we test the range of possible values
        min_backoff_ms = 1000  # min_backoff in milliseconds
        max_backoff_ms = 60000  # max_backoff in milliseconds

        # For attempts=1, calculated value should be min_backoff * 2^1 = 2000ms
        # Random component can range from min_backoff (1000) to calculated (2000)
        backoff1 = timer._calculate_backoff()
        self.assertGreaterEqual(backoff1, min_backoff_ms)
        self.assertLessEqual(backoff1, 2000)  # min_backoff * 2^1

        timer._attempts += 1
        # For attempts=2, calculated value should be min_backoff * 2^2 = 4000ms
        # Random component can range from min_backoff (1000) to calculated (4000)
        backoff2 = timer._calculate_backoff()
        self.assertGreaterEqual(backoff2, min_backoff_ms)
        self.assertLessEqual(backoff2, 4000)  # min_backoff * 2^2

        # Both should be within overall min/max bounds
        self.assertLessEqual(backoff1, max_backoff_ms)
        self.assertLessEqual(backoff2, max_backoff_ms)


if __name__ == "__main__":
    unittest.main()
