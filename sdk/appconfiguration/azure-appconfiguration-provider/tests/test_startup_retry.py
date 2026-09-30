# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import unittest
from unittest.mock import patch, MagicMock
import datetime
from azure.appconfiguration.provider._constants import (
    DEFAULT_STARTUP_TIMEOUT,
    MAX_STARTUP_BACKOFF_DURATION,
    MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION,
    STARTUP_BACKOFF_INTERVALS,
    JITTER_RATIO,
)


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

    @patch("azure.appconfiguration.provider._azureappconfigurationprovider.datetime")
    def test_load_all_timeout_raises_timeout_error(self, mock_datetime):
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

            def mock_try_initialize(startup_exceptions):
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
