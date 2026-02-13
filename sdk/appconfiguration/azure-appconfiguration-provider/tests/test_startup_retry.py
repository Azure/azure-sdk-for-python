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
    _get_startup_backoff,
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
    """Test the _get_startup_backoff function."""

    def test_within_first_interval(self):
        """Test backoff within first 100 seconds returns 5 seconds."""
        # STARTUP_BACKOFF_INTERVALS[0] = (100, 5)
        backoff, exceeded = _get_startup_backoff(0, 1)
        self.assertEqual(backoff, 5)
        self.assertFalse(exceeded)

        backoff, exceeded = _get_startup_backoff(50, 1)
        self.assertEqual(backoff, 5)
        self.assertFalse(exceeded)

        backoff, exceeded = _get_startup_backoff(99, 1)
        self.assertEqual(backoff, 5)
        self.assertFalse(exceeded)

    def test_within_second_interval(self):
        """Test backoff within 100-200 seconds returns 10 seconds."""
        # STARTUP_BACKOFF_INTERVALS[1] = (200, 10)
        backoff, exceeded = _get_startup_backoff(100, 1)
        self.assertEqual(backoff, 10)
        self.assertFalse(exceeded)

        backoff, exceeded = _get_startup_backoff(150, 1)
        self.assertEqual(backoff, 10)
        self.assertFalse(exceeded)

        backoff, exceeded = _get_startup_backoff(199, 1)
        self.assertEqual(backoff, 10)
        self.assertFalse(exceeded)

    def test_within_third_interval(self):
        """Test backoff within 200-600 seconds returns MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION."""
        # STARTUP_BACKOFF_INTERVALS[2] = (600, MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION)
        backoff, exceeded = _get_startup_backoff(200, 1)
        self.assertEqual(backoff, MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION)
        self.assertFalse(exceeded)

        backoff, exceeded = _get_startup_backoff(400, 1)
        self.assertEqual(backoff, MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION)
        self.assertFalse(exceeded)

        backoff, exceeded = _get_startup_backoff(599, 1)
        self.assertEqual(backoff, MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION)
        self.assertFalse(exceeded)

    def test_beyond_fixed_window_uses_exponential_backoff(self):
        """Test backoff beyond 600 seconds returns exponential backoff based on attempts."""
        # Beyond fixed window, uses _calculate_backoff_duration(attempts)
        # For attempt 1, _calculate_backoff_duration(1) does attempts+=1 -> 2, so jittered(30 * 2^1 = 60)
        backoff, exceeded = _get_startup_backoff(600, 1)
        self.assertTrue(exceeded)
        self.assertGreaterEqual(backoff, MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION * (1 - JITTER_RATIO))
        self.assertLessEqual(backoff, 60 * (1 + JITTER_RATIO))

        # For attempt 2, _calculate_backoff_duration(2) does attempts+=1 -> 3, so jittered(30 * 2^2 = 120)
        backoff, exceeded = _get_startup_backoff(1000, 2)
        self.assertTrue(exceeded)
        self.assertGreaterEqual(backoff, MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION * (1 - JITTER_RATIO))
        self.assertLessEqual(backoff, 120 * (1 + JITTER_RATIO))

    def test_negative_elapsed_time(self):
        """Test negative elapsed time returns first interval backoff."""
        backoff, exceeded = _get_startup_backoff(-1, 1)
        self.assertEqual(backoff, 5)
        self.assertFalse(exceeded)

    def test_boundary_conditions(self):
        """Test exact boundary values."""
        # Test at exact threshold boundaries
        for threshold, expected_backoff in STARTUP_BACKOFF_INTERVALS:
            # Just before threshold should return expected_backoff
            backoff, exceeded = _get_startup_backoff(threshold - 0.001, 1)
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
        from azure.appconfiguration.provider._azureappconfigurationproviderbase import AzureAppConfigurationProviderBase

        # Create a mock provider - use a custom __init__ that calls base but doesn't set up client manager
        def mock_init(self, **kwargs):
            AzureAppConfigurationProviderBase.__init__(self, endpoint="http://test.endpoint", **kwargs)
            self._startup_timeout = 1  # 1 second timeout
            self._replica_client_manager = MagicMock()
            self._secret_provider = MagicMock()
            self._secret_provider.uses_key_vault = False

        with patch.object(AzureAppConfigurationProvider, "__init__", mock_init):
            provider = AzureAppConfigurationProvider()
            provider._replica_client_manager.get_next_active_client.return_value = None

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
        from azure.appconfiguration.provider._azureappconfigurationproviderbase import AzureAppConfigurationProviderBase

        # Create a mock provider - use a custom __init__ that calls base but doesn't set up client manager
        def mock_init(self, **kwargs):
            AzureAppConfigurationProviderBase.__init__(self, endpoint="http://test.endpoint", **kwargs)
            self._startup_timeout = 10
            self._replica_client_manager = MagicMock()
            self._secret_provider = MagicMock()
            self._secret_provider.uses_key_vault = False

        with patch.object(AzureAppConfigurationProvider, "__init__", mock_init):
            provider = AzureAppConfigurationProvider()

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
        from azure.appconfiguration.provider._azureappconfigurationproviderbase import AzureAppConfigurationProviderBase

        # Create a mock provider - use a custom __init__ that calls base but doesn't set up client manager
        def mock_init(self, **kwargs):
            AzureAppConfigurationProviderBase.__init__(self, endpoint="http://test.endpoint", **kwargs)
            self._startup_timeout = 100
            self._replica_client_manager = MagicMock()
            self._secret_provider = MagicMock()
            self._secret_provider.uses_key_vault = False

        with patch.object(AzureAppConfigurationProvider, "__init__", mock_init):
            provider = AzureAppConfigurationProvider()

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
