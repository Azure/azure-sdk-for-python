# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import unittest
from unittest.mock import patch, Mock, MagicMock
import datetime

from azure.core.exceptions import HttpResponseError, ServiceRequestError

from azure.appconfiguration.provider._azureappconfigurationproviderbase import (
    _try_get_fixed_backoff,
    _calculate_backoff_duration,
    _is_failoverable,
)
from azure.appconfiguration.provider._constants import (
    DEFAULT_STARTUP_TIMEOUT,
    MAX_BACKOFF_DURATION,
    MIN_STARTUP_BACKOFF_DURATION,
    STARTUP_BACKOFF_INTERVALS,
    JITTER_RATIO,
)


class TestTryGetFixedBackoff(unittest.TestCase):
    """Test the _try_get_fixed_backoff function."""

    def test_within_first_interval(self):
        """Test backoff within first 100 seconds returns 5 seconds."""
        # STARTUP_BACKOFF_INTERVALS[0] = (100, 5)
        result = _try_get_fixed_backoff(0)
        self.assertEqual(result, 5)

        result = _try_get_fixed_backoff(50)
        self.assertEqual(result, 5)

        result = _try_get_fixed_backoff(99)
        self.assertEqual(result, 5)

    def test_within_second_interval(self):
        """Test backoff within 100-200 seconds returns 10 seconds."""
        # STARTUP_BACKOFF_INTERVALS[1] = (200, 10)
        result = _try_get_fixed_backoff(100)
        self.assertEqual(result, 10)

        result = _try_get_fixed_backoff(150)
        self.assertEqual(result, 10)

        result = _try_get_fixed_backoff(199)
        self.assertEqual(result, 10)

    def test_within_third_interval(self):
        """Test backoff within 200-600 seconds returns MIN_STARTUP_BACKOFF_DURATION."""
        # STARTUP_BACKOFF_INTERVALS[2] = (600, MIN_STARTUP_BACKOFF_DURATION)
        result = _try_get_fixed_backoff(200)
        self.assertEqual(result, MIN_STARTUP_BACKOFF_DURATION)

        result = _try_get_fixed_backoff(400)
        self.assertEqual(result, MIN_STARTUP_BACKOFF_DURATION)

        result = _try_get_fixed_backoff(599)
        self.assertEqual(result, MIN_STARTUP_BACKOFF_DURATION)

    def test_beyond_fixed_window(self):
        """Test backoff beyond 600 seconds returns None (exponential backoff)."""
        result = _try_get_fixed_backoff(600)
        self.assertIsNone(result)

        result = _try_get_fixed_backoff(1000)
        self.assertIsNone(result)

        result = _try_get_fixed_backoff(3600)
        self.assertIsNone(result)

    def test_negative_elapsed_time(self):
        """Test negative elapsed time returns first interval backoff."""
        result = _try_get_fixed_backoff(-1)
        self.assertEqual(result, 5)

    def test_boundary_conditions(self):
        """Test exact boundary values."""
        # Test at exact threshold boundaries
        for threshold, expected_backoff in STARTUP_BACKOFF_INTERVALS:
            # Just before threshold should return expected_backoff
            result = _try_get_fixed_backoff(threshold - 0.001)
            self.assertEqual(result, expected_backoff)


class TestCalculateBackoffDuration(unittest.TestCase):
    """Test the _calculate_backoff_duration function."""

    def test_first_attempt_returns_min_duration(self):
        """Test that first attempt returns minimum duration."""
        result = _calculate_backoff_duration(30, 600, 1)
        self.assertEqual(result, 30)

    def test_exponential_growth(self):
        """Test that backoff grows exponentially."""
        min_duration = 30
        max_duration = 600

        # For attempts=2, calculated = 30 * 2^1 = 60
        result2 = _calculate_backoff_duration(min_duration, max_duration, 2)
        # Result should be within jitter range of calculated value
        self.assertGreaterEqual(result2, min_duration * (1 - JITTER_RATIO))
        self.assertLessEqual(result2, 60 * (1 + JITTER_RATIO))

        # For attempts=3, calculated = 30 * 2^2 = 120
        result3 = _calculate_backoff_duration(min_duration, max_duration, 3)
        self.assertGreaterEqual(result3, min_duration * (1 - JITTER_RATIO))
        self.assertLessEqual(result3, 120 * (1 + JITTER_RATIO))

        # For attempts=4, calculated = 30 * 2^3 = 240
        result4 = _calculate_backoff_duration(min_duration, max_duration, 4)
        self.assertGreaterEqual(result4, min_duration * (1 - JITTER_RATIO))
        self.assertLessEqual(result4, 240 * (1 + JITTER_RATIO))

    def test_caps_at_max_duration(self):
        """Test that backoff is capped at max duration."""
        min_duration = 30
        max_duration = 100

        # For attempts=5, calculated = 30 * 2^4 = 480, but should cap at 100
        result = _calculate_backoff_duration(min_duration, max_duration, 5)
        self.assertLessEqual(result, max_duration * (1 + JITTER_RATIO))

    def test_invalid_min_duration_raises_error(self):
        """Test that min_duration <= 0 raises ValueError."""
        with self.assertRaises(ValueError) as context:
            _calculate_backoff_duration(0, 600, 1)
        self.assertIn("Minimum backoff duration must be greater than 0", str(context.exception))

        with self.assertRaises(ValueError):
            _calculate_backoff_duration(-1, 600, 1)

    def test_invalid_max_less_than_min_raises_error(self):
        """Test that max_duration < min_duration raises ValueError."""
        with self.assertRaises(ValueError) as context:
            _calculate_backoff_duration(100, 50, 1)
        self.assertIn("Maximum backoff duration must be greater than or equal to minimum", str(context.exception))

    def test_invalid_attempts_raises_error(self):
        """Test that attempts < 1 raises ValueError."""
        with self.assertRaises(ValueError) as context:
            _calculate_backoff_duration(30, 600, 0)
        self.assertIn("Number of attempts must be at least 1", str(context.exception))

        with self.assertRaises(ValueError):
            _calculate_backoff_duration(30, 600, -1)

    def test_very_large_attempts_does_not_overflow(self):
        """Test that very large attempt numbers don't cause overflow."""
        # Should not raise an exception and should return a reasonable value
        result = _calculate_backoff_duration(30, 600, 100)
        self.assertGreater(result, 0)
        self.assertLessEqual(result, 600 * (1 + JITTER_RATIO))

    def test_equal_min_max_duration(self):
        """Test when min and max duration are equal."""
        result = _calculate_backoff_duration(100, 100, 5)
        # Should be within jitter range of 100
        self.assertGreaterEqual(result, 100 * (1 - JITTER_RATIO))
        self.assertLessEqual(result, 100 * (1 + JITTER_RATIO))


class TestIsFailoverable(unittest.TestCase):
    """Test the _is_failoverable function."""

    def test_http_429_too_many_requests(self):
        """Test that HTTP 429 Too Many Requests is failoverable."""
        exception = HttpResponseError(message="Too many requests")
        exception.status_code = 429
        self.assertTrue(_is_failoverable(exception))

    def test_http_408_request_timeout(self):
        """Test that HTTP 408 Request Timeout is failoverable."""
        exception = HttpResponseError(message="Request timeout")
        exception.status_code = 408
        self.assertTrue(_is_failoverable(exception))

    def test_http_5xx_server_errors(self):
        """Test that HTTP 5xx server errors are failoverable."""
        for status_code in [500, 501, 502, 503, 504]:
            exception = HttpResponseError(message=f"Server error {status_code}")
            exception.status_code = status_code
            with self.subTest(status_code=status_code):
                self.assertTrue(_is_failoverable(exception))

    def test_http_4xx_client_errors_not_failoverable(self):
        """Test that most HTTP 4xx client errors are not failoverable."""
        for status_code in [400, 401, 403, 404, 405, 409]:
            exception = HttpResponseError(message=f"Client error {status_code}")
            exception.status_code = status_code
            with self.subTest(status_code=status_code):
                self.assertFalse(_is_failoverable(exception))

    def test_connection_error_is_failoverable(self):
        """Test that ConnectionError is failoverable."""
        exception = ConnectionError("Connection refused")
        self.assertTrue(_is_failoverable(exception))

    def test_timeout_error_is_failoverable(self):
        """Test that TimeoutError is failoverable."""
        exception = TimeoutError("Connection timed out")
        self.assertTrue(_is_failoverable(exception))

    def test_os_error_is_failoverable(self):
        """Test that OSError is failoverable."""
        exception = OSError("Network unreachable")
        self.assertTrue(_is_failoverable(exception))

    def test_io_error_is_failoverable(self):
        """Test that IOError is failoverable."""
        exception = IOError("I/O operation failed")
        self.assertTrue(_is_failoverable(exception))

    def test_value_error_not_failoverable(self):
        """Test that ValueError is not failoverable."""
        exception = ValueError("Invalid value")
        self.assertFalse(_is_failoverable(exception))

    def test_key_error_not_failoverable(self):
        """Test that KeyError is not failoverable."""
        exception = KeyError("Missing key")
        self.assertFalse(_is_failoverable(exception))

    def test_generic_exception_not_failoverable(self):
        """Test that generic Exception is not failoverable."""
        exception = Exception("Generic error")
        self.assertFalse(_is_failoverable(exception))

    def test_http_response_error_without_status_code(self):
        """Test HttpResponseError without status_code attribute."""
        exception = HttpResponseError(message="Unknown error")
        # HttpResponseError without status_code should not be failoverable
        # unless it has a failoverable inner exception
        if not hasattr(exception, "status_code"):
            exception.status_code = None
        self.assertFalse(_is_failoverable(exception))

    def test_exception_with_failoverable_cause(self):
        """Test exception with failoverable __cause__."""
        inner_exception = ConnectionError("Connection refused")
        outer_exception = Exception("Outer error")
        outer_exception.__cause__ = inner_exception
        self.assertTrue(_is_failoverable(outer_exception))

    def test_exception_with_failoverable_context(self):
        """Test exception with failoverable __context__."""
        inner_exception = TimeoutError("Timeout")
        outer_exception = Exception("Outer error")
        outer_exception.__context__ = inner_exception
        self.assertTrue(_is_failoverable(outer_exception))


class TestStartupRetryIntegration(unittest.TestCase):
    """Integration tests for startup retry behavior."""

    def test_default_startup_timeout_value(self):
        """Test that DEFAULT_STARTUP_TIMEOUT has expected value."""
        self.assertEqual(DEFAULT_STARTUP_TIMEOUT, 100)

    def test_max_backoff_duration_value(self):
        """Test that MAX_BACKOFF_DURATION has expected value."""
        self.assertEqual(MAX_BACKOFF_DURATION, 600)

    def test_min_startup_backoff_duration_value(self):
        """Test that MIN_STARTUP_BACKOFF_DURATION has expected value."""
        self.assertEqual(MIN_STARTUP_BACKOFF_DURATION, 30)

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
            start_time = datetime.datetime(2024, 1, 1, 0, 0, 0)
            times = [
                start_time,  # First call to check elapsed time
                start_time + datetime.timedelta(seconds=2),  # Second call exceeds timeout
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
