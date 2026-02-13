# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import unittest
from unittest.mock import patch, MagicMock
import datetime

from azure.core.exceptions import HttpResponseError

from azure.appconfiguration.provider._azureappconfigurationproviderbase import (
    _get_fixed_backoff,
    _calculate_backoff_duration,
)
from azure.appconfiguration.provider._constants import (
    DEFAULT_STARTUP_TIMEOUT,
    MAX_STARTUP_BACKOFF_DURATION,
    MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION,
    STARTUP_BACKOFF_INTERVALS,
    JITTER_RATIO,
)


class TestGetFixedBackoff(unittest.TestCase):
    """Test the _get_fixed_backoff function."""

    def test_within_first_interval(self):
        """Test backoff within first 100 seconds returns 5 seconds."""
        # STARTUP_BACKOFF_INTERVALS[0] = (100, 5)
        result = _get_fixed_backoff(0, 1)
        self.assertEqual(result, 5)

        result = _get_fixed_backoff(50, 1)
        self.assertEqual(result, 5)

        result = _get_fixed_backoff(99, 1)
        self.assertEqual(result, 5)

    def test_within_second_interval(self):
        """Test backoff within 100-200 seconds returns 10 seconds."""
        # STARTUP_BACKOFF_INTERVALS[1] = (200, 10)
        result = _get_fixed_backoff(100, 1)
        self.assertEqual(result, 10)

        result = _get_fixed_backoff(150, 1)
        self.assertEqual(result, 10)

        result = _get_fixed_backoff(199, 1)
        self.assertEqual(result, 10)

    def test_within_third_interval(self):
        """Test backoff within 200-600 seconds returns MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION."""
        # STARTUP_BACKOFF_INTERVALS[2] = (600, MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION)
        result = _get_fixed_backoff(200, 1)
        self.assertEqual(result, MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION)

        result = _get_fixed_backoff(400, 1)
        self.assertEqual(result, MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION)

        result = _get_fixed_backoff(599, 1)
        self.assertEqual(result, MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION)

    def test_beyond_fixed_window_uses_exponential_backoff(self):
        """Test backoff beyond 600 seconds returns exponential backoff based on attempts."""
        # Beyond fixed window, uses _calculate_backoff_duration(attempts)
        result = _get_fixed_backoff(600, 1)
        self.assertEqual(result, MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION)  # First attempt returns min

        # For attempt 2, should be jittered value around 60 (30 * 2^1)
        result = _get_fixed_backoff(1000, 2)
        self.assertGreaterEqual(result, MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION * (1 - JITTER_RATIO))
        self.assertLessEqual(result, 60 * (1 + JITTER_RATIO))

    def test_negative_elapsed_time(self):
        """Test negative elapsed time returns first interval backoff."""
        result = _get_fixed_backoff(-1, 1)
        self.assertEqual(result, 5)

    def test_boundary_conditions(self):
        """Test exact boundary values."""
        # Test at exact threshold boundaries
        for threshold, expected_backoff in STARTUP_BACKOFF_INTERVALS:
            # Just before threshold should return expected_backoff
            result = _get_fixed_backoff(threshold - 0.001, 1)
            self.assertEqual(result, expected_backoff)


class TestCalculateBackoffDuration(unittest.TestCase):
    """Test the _calculate_backoff_duration function."""

    def test_first_attempt_returns_min_duration(self):
        """Test that first attempt returns minimum duration."""
        result = _calculate_backoff_duration(1)
        self.assertEqual(result, MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION)

    def test_exponential_growth(self):
        """Test that backoff grows exponentially."""
        # For attempts=2, calculated = 30 * 2^1 = 60
        result2 = _calculate_backoff_duration(2)
        # Result should be within jitter range of calculated value
        self.assertGreaterEqual(result2, MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION * (1 - JITTER_RATIO))
        self.assertLessEqual(result2, 60 * (1 + JITTER_RATIO))

        # For attempts=3, calculated = 30 * 2^2 = 120
        result3 = _calculate_backoff_duration(3)
        self.assertGreaterEqual(result3, MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION * (1 - JITTER_RATIO))
        self.assertLessEqual(result3, 120 * (1 + JITTER_RATIO))

        # For attempts=4, calculated = 30 * 2^3 = 240
        result4 = _calculate_backoff_duration(4)
        self.assertGreaterEqual(result4, MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION * (1 - JITTER_RATIO))
        self.assertLessEqual(result4, 240 * (1 + JITTER_RATIO))

    def test_caps_at_max_duration(self):
        """Test that backoff is capped at max duration."""
        # For attempts=6, calculated = 30 * 2^5 = 960, but should cap at MAX_STARTUP_BACKOFF_DURATION (600)
        result = _calculate_backoff_duration(6)
        self.assertLessEqual(result, MAX_STARTUP_BACKOFF_DURATION * (1 + JITTER_RATIO))

    def test_invalid_attempts_raises_error(self):
        """Test that attempts < 1 raises ValueError."""
        with self.assertRaises(ValueError) as context:
            _calculate_backoff_duration(0)
        self.assertIn("Number of attempts must be at least 1", str(context.exception))

        with self.assertRaises(ValueError):
            _calculate_backoff_duration(-1)

    def test_very_large_attempts_does_not_overflow(self):
        """Test that very large attempt numbers don't cause overflow."""
        # Should not raise an exception and should return a reasonable value
        result = _calculate_backoff_duration(100)
        self.assertGreater(result, 0)
        self.assertLessEqual(result, MAX_STARTUP_BACKOFF_DURATION * (1 + JITTER_RATIO))

class TestStartupRetryIntegration(unittest.TestCase):
    """Integration tests for startup retry behavior."""

    def test_default_startup_timeout_value(self):
        """Test that DEFAULT_STARTUP_TIMEOUT has expected value."""
        self.assertEqual(DEFAULT_STARTUP_TIMEOUT, 100)

    def test_max_backoff_duration_value(self):
        """Test that MAX_STARTUP_BACKOFF_DURATION has expected value."""
        self.assertEqual(MAX_STARTUP_BACKOFF_DURATION, 600)

    def test_MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION_value(self):
        """Test that MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION has expected value."""
        self.assertEqual(MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION, 30)

    def test_startup_backoff_intervals_structure(self):
        """Test that STARTUP_BACKOFF_INTERVALS has expected structure."""
        self.assertEqual(len(STARTUP_BACKOFF_INTERVALS), 3)
        # Should be sorted by threshold
        thresholds = [interval[0] for interval in STARTUP_BACKOFF_INTERVALS]
        self.assertEqual(thresholds, sorted(thresholds))

    def test_jitter_ratio_value(self):
        """Test that JITTER_RATIO has expected value."""
        self.assertEqual(JITTER_RATIO, 0.25)


class TestLoadAllRetryBehavior(unittest.TestCase):
    """Test the _load_all method retry behavior."""

    def setUp(self):
        """Set up test fixtures."""
        # We'll use mocking to test the retry behavior
        pass

    @patch("azure.appconfiguration.provider._azureappconfigurationprovider.time.sleep")
    @patch("azure.appconfiguration.provider._azureappconfigurationprovider.datetime")
    def test_load_all_timeout_raises_timeout_error(self, mock_datetime, mock_sleep):
        """Test that _load_all raises TimeoutError when startup_timeout is exceeded."""
        from azure.appconfiguration.provider._azureappconfigurationprovider import AzureAppConfigurationProvider

        # Create a mock provider
        with patch.object(AzureAppConfigurationProvider, "__init__", lambda self, **kwargs: None):
            provider = AzureAppConfigurationProvider()
            provider._startup_timeout = 1  # 1 second timeout
            provider._replica_client_manager = MagicMock()
            provider._replica_client_manager.get_next_active_client.return_value = None
            provider._secret_provider = MagicMock()
            provider._secret_provider.uses_key_vault = False

            # Mock datetime to simulate time passing
            start_time = datetime.datetime(2026, 1, 1, 0, 0, 0)
            times = [
                start_time,  # Initial startup_start_time
                start_time,  # First loop elapsed check (0 seconds elapsed)
                start_time,  # First loop remaining timeout check
                start_time + datetime.timedelta(seconds=2),  # Second loop check exceeds timeout
            ]
            mock_datetime.datetime.now.side_effect = times

            with self.assertRaises(TimeoutError) as context:
                provider._load_all()

            self.assertIn("timed out", str(context.exception.args[0]).lower())

    @patch("azure.appconfiguration.provider._azureappconfigurationprovider.time.sleep")
    def test_load_all_uses_fixed_backoff_initially(self, mock_sleep):
        """Test that _load_all uses fixed backoff during initial period."""
        from azure.appconfiguration.provider._azureappconfigurationprovider import AzureAppConfigurationProvider

        with patch.object(AzureAppConfigurationProvider, "__init__", lambda self, **kwargs: None):
            provider = AzureAppConfigurationProvider()
            provider._startup_timeout = 10
            provider._replica_client_manager = MagicMock()
            provider._secret_provider = MagicMock()
            provider._secret_provider.uses_key_vault = False
            provider._selects = []
            provider._feature_flag_enabled = False
            provider._watched_settings = {}
            provider._tracing_context = MagicMock()
            provider._update_lock = MagicMock()

            # First attempt fails, second succeeds
            attempt_count = [0]

            def mock_try_initialize(startup_exceptions, **kwargs):
                attempt_count[0] += 1
                if attempt_count[0] == 1:
                    startup_exceptions.append(ConnectionError("Connection failed"))
                    return False
                return True

            provider._try_initialize = mock_try_initialize

            provider._load_all()

            # Verify sleep was called with fixed backoff duration (5 seconds for first 100 seconds)
            mock_sleep.assert_called_once()
            sleep_duration = mock_sleep.call_args[0][0]
            self.assertEqual(sleep_duration, 5)

    @patch("azure.appconfiguration.provider._azureappconfigurationprovider.time.sleep")
    def test_load_all_succeeds_on_first_try(self, mock_sleep):
        """Test that _load_all succeeds without retries when first attempt succeeds."""
        from azure.appconfiguration.provider._azureappconfigurationprovider import AzureAppConfigurationProvider

        with patch.object(AzureAppConfigurationProvider, "__init__", lambda self, **kwargs: None):
            provider = AzureAppConfigurationProvider()
            provider._startup_timeout = 100
            provider._replica_client_manager = MagicMock()
            provider._secret_provider = MagicMock()
            provider._secret_provider.uses_key_vault = False

            # First attempt succeeds
            provider._try_initialize = MagicMock(return_value=True)

            provider._load_all()

            # Sleep should not be called when first attempt succeeds
            mock_sleep.assert_not_called()
            provider._try_initialize.assert_called_once()


class TestStartupTimeoutConfiguration(unittest.TestCase):
    """Test startup_timeout configuration."""

    def test_custom_startup_timeout(self):
        """Test that custom startup_timeout is respected."""
        from azure.appconfiguration.provider._azureappconfigurationprovider import _buildprovider

        with patch("azure.appconfiguration.provider._azureappconfigurationprovider.ConfigurationClientManager"):
            with patch("azure.appconfiguration.provider._azureappconfigurationprovider.SecretProvider"):
                provider = _buildprovider(
                    connection_string="Endpoint=https://fake.endpoint;Id=fake;Secret=fake",
                    endpoint=None,
                    credential=None,
                    startup_timeout=60,
                )
                self.assertEqual(provider._startup_timeout, 60)

    def test_default_startup_timeout(self):
        """Test that default startup_timeout is used when not specified."""
        from azure.appconfiguration.provider._azureappconfigurationprovider import _buildprovider

        with patch("azure.appconfiguration.provider._azureappconfigurationprovider.ConfigurationClientManager"):
            with patch("azure.appconfiguration.provider._azureappconfigurationprovider.SecretProvider"):
                provider = _buildprovider(
                    connection_string="Endpoint=https://fake.endpoint;Id=fake;Secret=fake",
                    endpoint=None,
                    credential=None,
                )
                self.assertEqual(provider._startup_timeout, DEFAULT_STARTUP_TIMEOUT)


if __name__ == "__main__":
    unittest.main()
