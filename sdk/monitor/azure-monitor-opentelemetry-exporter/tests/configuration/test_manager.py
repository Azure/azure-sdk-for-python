# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import unittest
from unittest.mock import Mock, patch
import os

from azure.monitor.opentelemetry.exporter._configuration import (
    _ConfigurationManager,
    _ConfigurationState,
)
from azure.monitor.opentelemetry.exporter._configuration._state import get_configuration_manager
from azure.monitor.opentelemetry.exporter._configuration._utils import OneSettingsResponse
from azure.monitor.opentelemetry.exporter._constants import (
    _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS,
    _ONE_SETTINGS_MAX_REFRESH_INTERVAL_SECONDS,
    _ONE_SETTINGS_PYTHON_KEY,
    _ONE_SETTINGS_CHANGE_URL,
    _ONE_SETTINGS_CONFIG_URL,
    _RETRYABLE_STATUS_CODES,
)


class TestConfigurationState(unittest.TestCase):
    """Test cases for _ConfigurationState immutable data class."""

    def test_default_values(self):
        """Test that _ConfigurationState has correct default values."""
        state = _ConfigurationState()

        self.assertEqual(state.etag, "")
        self.assertEqual(state.refresh_interval, _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS)
        self.assertEqual(state.version_cache, -1)
        self.assertEqual(state.settings_cache, {})

    def test_with_updates_single_field(self):
        """Test updating a single field creates new state object."""
        original_state = _ConfigurationState()
        updated_state = original_state.with_updates(etag="new-etag")

        # Original state unchanged
        self.assertEqual(original_state.etag, "")
        # New state has updated value
        self.assertEqual(updated_state.etag, "new-etag")
        # Other fields preserved
        self.assertEqual(updated_state.refresh_interval, _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS)
        self.assertEqual(updated_state.version_cache, -1)

    def test_with_updates_multiple_fields(self):
        """Test updating multiple fields creates new state object."""
        original_state = _ConfigurationState()
        updated_state = original_state.with_updates(
            etag="test-etag", refresh_interval=60, version_cache=5, settings_cache={"key": "value"}
        )

        # Original state unchanged
        self.assertEqual(original_state.etag, "")
        self.assertEqual(original_state.refresh_interval, _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS)
        self.assertEqual(original_state.version_cache, -1)
        self.assertEqual(original_state.settings_cache, {})

        # New state has all updated values
        self.assertEqual(updated_state.etag, "test-etag")
        self.assertEqual(updated_state.refresh_interval, 60)
        self.assertEqual(updated_state.version_cache, 5)
        self.assertEqual(updated_state.settings_cache, {"key": "value"})

    def test_settings_cache_isolation(self):
        """Test that settings_cache is properly isolated between state objects."""
        original_state = _ConfigurationState()
        original_state.settings_cache["original"] = "value"

        updated_state = original_state.with_updates(settings_cache={"new": "value"})

        # Original and updated states should be isolated
        self.assertEqual(original_state.settings_cache, {"original": "value"})
        self.assertEqual(updated_state.settings_cache, {"new": "value"})


class TestConfigurationManager(unittest.TestCase):
    """Test cases for _ConfigurationManager class."""

    def setUp(self):
        """Reset singleton state before each test."""
        # Clear any existing singleton instance
        from azure.monitor.opentelemetry.exporter._utils import Singleton

        if _ConfigurationManager in Singleton._instances:
            # Shutdown existing instance first
            existing_instance = Singleton._instances[_ConfigurationManager]
            if hasattr(existing_instance, "_configuration_worker") and existing_instance._configuration_worker:
                existing_instance.shutdown()
        if _ConfigurationManager in Singleton._instances:
            del Singleton._instances[_ConfigurationManager]

    def tearDown(self):
        """Clean up after each test."""
        from azure.monitor.opentelemetry.exporter._utils import Singleton

        if _ConfigurationManager in Singleton._instances:
            # Shutdown the instance
            instance = Singleton._instances[_ConfigurationManager]
            if hasattr(instance, "_configuration_worker") and instance._configuration_worker:
                instance.shutdown()
        if _ConfigurationManager in Singleton._instances:
            del Singleton._instances[_ConfigurationManager]

    @patch("azure.monitor.opentelemetry.exporter._configuration._worker._ConfigurationWorker")
    def test_singleton_pattern(self, mock_worker_class):
        """Test that ConfigurationManager follows singleton pattern."""
        # Create first instance
        manager1 = _ConfigurationManager()

        # Create second instance
        manager2 = _ConfigurationManager()

        manager1.initialize()
        manager2.initialize()

        # Should be the same instance
        self.assertIs(manager1, manager2)

        # Worker should only be initialized once
        mock_worker_class.assert_called_once()

    @patch("azure.monitor.opentelemetry.exporter._configuration._worker._ConfigurationWorker")
    def test_worker_initialization(self, mock_worker_class):
        """Test that ConfigurationWorker is initialized properly."""
        mock_worker_instance = Mock()
        mock_worker_class.return_value = mock_worker_instance

        manager = _ConfigurationManager()
        manager.initialize()

        # Verify worker was created with manager and default refresh interval
        mock_worker_class.assert_called_once_with(manager, _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS)
        self.assertEqual(manager._configuration_worker, mock_worker_instance)

    @patch("azure.monitor.opentelemetry.exporter._configuration.make_onesettings_request")
    @patch("azure.monitor.opentelemetry.exporter._configuration._worker._ConfigurationWorker")
    def test_get_configuration_basic_success(self, mock_worker_class, mock_request):
        """Test basic successful configuration retrieval without CONFIG fetch."""
        # Setup - Use version -1 to match initial state, no CONFIG fetch
        mock_response = OneSettingsResponse(
            etag="test-etag",
            refresh_interval=1800,
            settings={"key": "value"},
            version=-1,  # Same as initial version, no CONFIG fetch
            status_code=200,
        )
        mock_request.return_value = mock_response

        manager = _ConfigurationManager()
        manager.initialize()

        # Execute
        result = manager.get_configuration_and_refresh_interval({"param": "value"})

        # Verify return value
        self.assertEqual(result, 1800)

        # Verify only one request was made (to CHANGE endpoint only)
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        self.assertEqual(call_args[0][0], _ONE_SETTINGS_CHANGE_URL)  # URL
        self.assertEqual(call_args[0][1], {"param": "value"})  # query_dict

    @patch("azure.monitor.opentelemetry.exporter._configuration.make_onesettings_request")
    @patch("azure.monitor.opentelemetry.exporter._configuration._worker._ConfigurationWorker")
    def test_etag_headers_included(self, mock_worker_class, mock_request):
        """Test that etag is included in request headers."""
        # Setup - first call sets etag
        mock_response1 = OneSettingsResponse(etag="test-etag", refresh_interval=1800, status_code=200)
        mock_request.return_value = mock_response1

        manager = _ConfigurationManager()
        manager.initialize()
        manager.get_configuration_and_refresh_interval()

        # Setup - second call should include etag
        mock_response2 = OneSettingsResponse(etag="new-etag", refresh_interval=2400, status_code=200)
        mock_request.return_value = mock_response2

        # Execute second call
        manager.get_configuration_and_refresh_interval()

        # Verify second call included etag in headers
        self.assertEqual(mock_request.call_count, 2)
        second_call_args = mock_request.call_args
        headers = second_call_args[0][2]  # headers parameter
        self.assertEqual(headers["If-None-Match"], "test-etag")
        self.assertEqual(headers["x-ms-onesetinterval"], "1800")

    @patch("azure.monitor.opentelemetry.exporter._configuration.make_onesettings_request")
    @patch("azure.monitor.opentelemetry.exporter._configuration._worker._ConfigurationWorker")
    def test_version_increase_triggers_config_fetch(self, mock_worker_class, mock_request):
        """Test that version increase triggers CONFIG endpoint fetch."""
        manager = _ConfigurationManager()
        manager.initialize()

        # Mock responses for CHANGE and CONFIG endpoints
        change_response = OneSettingsResponse(
            etag="test-etag", refresh_interval=1800, settings={"key": "value"}, version=5, status_code=200
        )
        config_response = OneSettingsResponse(settings={"key": "config_value"}, version=5, status_code=200)

        # Configure mock to return different responses for different URLs
        def mock_request_side_effect(url, query_dict, headers=None):
            if url == _ONE_SETTINGS_CHANGE_URL:
                return change_response
            elif url == _ONE_SETTINGS_CONFIG_URL:
                return config_response
            return OneSettingsResponse()

        mock_request.side_effect = mock_request_side_effect

        # Execute
        result = manager.get_configuration_and_refresh_interval()

        # Verify both endpoints were called
        self.assertEqual(mock_request.call_count, 2)

        # Verify first call was to CHANGE endpoint
        first_call = mock_request.call_args_list[0]
        self.assertEqual(first_call[0][0], _ONE_SETTINGS_CHANGE_URL)

        # Verify second call was to CONFIG endpoint
        second_call = mock_request.call_args_list[1]
        self.assertEqual(second_call[0][0], _ONE_SETTINGS_CONFIG_URL)

        # Verify state was updated with CONFIG response
        self.assertEqual(manager.get_current_version(), 5)
        self.assertEqual(manager.get_settings(), {"key": "config_value"})
        self.assertEqual(result, 1800)

    @patch("azure.monitor.opentelemetry.exporter._configuration.make_onesettings_request")
    @patch("azure.monitor.opentelemetry.exporter._configuration._worker._ConfigurationWorker")
    def test_version_same_no_config_fetch(self, mock_worker_class, mock_request):
        """Test that same version does not trigger CONFIG fetch."""
        manager = _ConfigurationManager()
        manager.initialize()
        manager._current_state.refresh_interval = 10
        manager._current_state.etag = "old_etag"
        manager._current_state.version_cache = 3

        # First call to establish version cache
        first_response = OneSettingsResponse(
            etag="first-etag", refresh_interval=2500, settings={"key": "first_value"}, version=3, status_code=200
        )
        mock_request.return_value = first_response
        result = manager.get_configuration_and_refresh_interval()

        # Verify that ALL calls were to CHANGE endpoint only
        all_calls = mock_request.call_args_list
        for call in all_calls:
            self.assertEqual(call[0][0], _ONE_SETTINGS_CHANGE_URL)

        self.assertEqual(result, 2500)

    @patch("azure.monitor.opentelemetry.exporter._configuration.make_onesettings_request")
    @patch("azure.monitor.opentelemetry.exporter._configuration._worker._ConfigurationWorker")
    @patch("azure.monitor.opentelemetry.exporter._configuration.logger")
    def test_version_decrease_warning(self, mock_logger, mock_worker_class, mock_request):
        """Test warning when version decreases."""
        manager = _ConfigurationManager()
        manager.initialize()

        # Set initial state with higher version
        manager._current_state.refresh_interval = 1800
        manager._current_state.etag = "first_etag"
        manager._current_state.version_cache = 5

        # Call with lower version
        lower_version_response = OneSettingsResponse(
            etag="second-etag",
            refresh_interval=2400,
            settings={"key": "second_value"},
            version=3,  # Lower version
            status_code=200,
        )
        mock_request.return_value = lower_version_response

        # Execute call
        manager.get_configuration_and_refresh_interval()

        # Verify warning was logged
        mock_logger.warning.assert_called()
        warning_message = mock_logger.warning.call_args[0][0]
        self.assertIn("lower than cached version", warning_message)

        # Verify that ALL calls were to CHANGE endpoint only
        all_calls = mock_request.call_args_list
        for call in all_calls:
            self.assertEqual(call[0][0], _ONE_SETTINGS_CHANGE_URL)

    @patch("azure.monitor.opentelemetry.exporter._configuration.make_onesettings_request")
    @patch("azure.monitor.opentelemetry.exporter._configuration._worker._ConfigurationWorker")
    def test_304_not_modified_response(self, mock_worker_class, mock_request):
        """Test handling of 304 Not Modified response."""
        manager = _ConfigurationManager()
        manager.initialize()

        # First call to establish etag and state
        first_response = OneSettingsResponse(
            etag="test-etag", refresh_interval=1800, settings={"key": "value"}, version=2, status_code=200
        )
        config_response = OneSettingsResponse(settings={"key": "config_value"}, version=2, status_code=200)

        def first_call_side_effect(url, query_dict, headers=None):
            if url == _ONE_SETTINGS_CHANGE_URL:
                return first_response
            elif url == _ONE_SETTINGS_CONFIG_URL:
                return config_response
            return OneSettingsResponse()

        mock_request.side_effect = first_call_side_effect
        first_result = manager.get_configuration_and_refresh_interval()

        # Reset mock for 304 response
        mock_request.reset_mock()

        # Second call returns 304 Not Modified
        not_modified_response = OneSettingsResponse(status_code=304)
        mock_request.return_value = not_modified_response

        # Execute second call
        second_result = manager.get_configuration_and_refresh_interval()

        # Verify 304 response preserves previous refresh interval (both should be 1800)
        self.assertEqual(first_result, 1800)
        self.assertEqual(second_result, 1800)  # Should preserve the original interval

        # Verify only CHANGE endpoint was called
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        self.assertEqual(call_args[0][0], _ONE_SETTINGS_CHANGE_URL)

        # Verify etag was included in headers
        headers = call_args[0][2]
        self.assertEqual(headers["If-None-Match"], "test-etag")

    @patch("azure.monitor.opentelemetry.exporter._configuration.make_onesettings_request")
    @patch("azure.monitor.opentelemetry.exporter._configuration._worker._ConfigurationWorker")
    @patch("azure.monitor.opentelemetry.exporter._configuration.logger")
    def test_transient_error_timeout(self, mock_logger, mock_worker_class, mock_request):
        """Test transient error handling for timeout."""
        manager = _ConfigurationManager()
        manager.initialize()

        # Set initial refresh interval
        with manager._state_lock:
            manager._current_state = manager._current_state.with_updates(refresh_interval=1800)

        # Setup timeout response
        timeout_response = OneSettingsResponse(
            has_exception=True, status_code=200  # Default status when exception occurs
        )
        mock_request.return_value = timeout_response

        # Execute
        result = manager.get_configuration_and_refresh_interval()

        # Verify refresh interval was doubled
        self.assertEqual(result, 3600)  # 1800 * 2

        # Verify only CHANGE endpoint was called (no CONFIG fetch on error)
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        self.assertEqual(call_args[0][0], _ONE_SETTINGS_CHANGE_URL)

        # Verify warning was logged
        mock_logger.warning.assert_called()
        warning_message = mock_logger.warning.call_args[0][0]
        self.assertIn("transient error", warning_message)

    @patch("azure.monitor.opentelemetry.exporter._configuration.make_onesettings_request")
    @patch("azure.monitor.opentelemetry.exporter._configuration._worker._ConfigurationWorker")
    @patch("azure.monitor.opentelemetry.exporter._configuration.logger")
    def test_transient_error_network_exception(self, mock_logger, mock_worker_class, mock_request):
        """Test transient error handling for network exception."""
        manager = _ConfigurationManager()
        manager.initialize()

        # Set initial refresh interval
        with manager._state_lock:
            manager._current_state = manager._current_state.with_updates(refresh_interval=900)

        # Setup network exception response
        exception_response = OneSettingsResponse(has_exception=True, status_code=200)
        mock_request.return_value = exception_response

        # Execute
        result = manager.get_configuration_and_refresh_interval()

        # Verify refresh interval was doubled
        self.assertEqual(result, 1800)  # 900 * 2

        # Verify warning was logged with correct error type
        mock_logger.warning.assert_called()
        warning_message = mock_logger.warning.call_args[0][0]
        self.assertIn("transient error", warning_message)

    @patch("azure.monitor.opentelemetry.exporter._configuration.make_onesettings_request")
    @patch("azure.monitor.opentelemetry.exporter._configuration._worker._ConfigurationWorker")
    @patch("azure.monitor.opentelemetry.exporter._configuration.logger")
    def test_transient_error_http_status_codes(self, mock_logger, mock_worker_class, mock_request):
        """Test transient error handling for various HTTP status codes."""
        manager = _ConfigurationManager()
        manager.initialize()

        # Test various retryable status codes
        test_cases = [429, 500, 502, 503, 504, 408, 401, 403]

        for status_code in test_cases:
            with self.subTest(status_code=status_code):
                # Reset mock and set initial refresh interval
                mock_request.reset_mock()
                mock_logger.reset_mock()

                with manager._state_lock:
                    manager._current_state = manager._current_state.with_updates(refresh_interval=1200)

                # Setup HTTP error response
                http_error_response = OneSettingsResponse(
                    status_code=status_code,
                    has_exception=False,
                )
                mock_request.return_value = http_error_response

                # Execute
                result = manager.get_configuration_and_refresh_interval()

                # Verify refresh interval was doubled
                self.assertEqual(result, 2400)  # 1200 * 2

                # Verify warning was logged with correct status code
                mock_logger.warning.assert_called()
                warning_message = mock_logger.warning.call_args[0][0]
                self.assertIn("transient error", warning_message)

    @patch("azure.monitor.opentelemetry.exporter._configuration.make_onesettings_request")
    @patch("azure.monitor.opentelemetry.exporter._configuration._worker._ConfigurationWorker")
    @patch("azure.monitor.opentelemetry.exporter._configuration.logger")
    def test_transient_error_refresh_interval_cap(self, mock_logger, mock_worker_class, mock_request):
        """Test that refresh interval is capped at 24 hours for transient errors."""
        manager = _ConfigurationManager()
        manager.initialize()

        # Set initial refresh interval to a high value that would exceed cap when doubled
        high_refresh_interval = _ONE_SETTINGS_MAX_REFRESH_INTERVAL_SECONDS // 2 + 1000  # Will exceed cap when doubled

        with manager._state_lock:
            manager._current_state = manager._current_state.with_updates(refresh_interval=high_refresh_interval)

        # Setup timeout response
        timeout_response = OneSettingsResponse(has_exception=True, status_code=200)
        mock_request.return_value = timeout_response

        # Execute
        result = manager.get_configuration_and_refresh_interval()

        # Verify refresh interval was capped at 24 hours
        self.assertEqual(result, _ONE_SETTINGS_MAX_REFRESH_INTERVAL_SECONDS)

        # Verify warning was logged mentioning transient error
        mock_logger.warning.assert_called()
        warning_message = mock_logger.warning.call_args[0][0]
        self.assertIn("transient", warning_message)

    @patch("azure.monitor.opentelemetry.exporter._configuration.make_onesettings_request")
    @patch("azure.monitor.opentelemetry.exporter._configuration._worker._ConfigurationWorker")
    def test_non_transient_error_no_backoff(self, mock_worker_class, mock_request):
        """Test that non-transient errors don't trigger backoff."""
        manager = _ConfigurationManager()
        manager.initialize()

        # Set initial refresh interval
        with manager._state_lock:
            manager._current_state = manager._current_state.with_updates(refresh_interval=1800)

        # Setup non-retryable HTTP error response (e.g., 400 Bad Request)
        bad_request_response = OneSettingsResponse(
            status_code=400,  # Not in _RETRYABLE_STATUS_CODES
            has_exception=False,
            refresh_interval=1800,  # Should remain unchanged
        )
        mock_request.return_value = bad_request_response

        # Execute
        result = manager.get_configuration_and_refresh_interval()

        # Verify refresh interval was updated to response value
        self.assertEqual(result, 1800)

        # Verify only CHANGE endpoint was called
        mock_request.assert_called_once()

    @patch("azure.monitor.opentelemetry.exporter._configuration.make_onesettings_request")
    @patch("azure.monitor.opentelemetry.exporter._configuration._worker._ConfigurationWorker")
    def test_successful_request_after_transient_error(self, mock_worker_class, mock_request):
        """Test that successful requests don't double refresh interval."""
        manager = _ConfigurationManager()
        manager.initialize()

        # Setup successful response
        success_response = OneSettingsResponse(
            etag="test-etag",
            refresh_interval=1800,
            settings={"key": "value"},
            version=-1,  # Same as initial version
            status_code=200,
            has_exception=False,
        )
        mock_request.return_value = success_response

        # Execute
        result = manager.get_configuration_and_refresh_interval()

        # Verify refresh interval is not doubled (uses response value)
        self.assertEqual(result, 1800)

    @patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONTROLPLANE_DISABLED": "true"})
    def test_configuration_manager_disabled(self):
        """Test that configuration manager is disabled when environment variable is set."""

        # When controlplane is disabled, get_configuration_manager should return None
        manager = get_configuration_manager()
        self.assertIsNone(manager)

    @patch.dict(os.environ, {"APPLICATIONINSIGHTS_CONTROLPLANE_DISABLED": "false"})
    def test_configuration_manager_enabled(self):
        """Test that configuration manager is enabled when environment variable is false."""

        # When controlplane is not disabled, get_configuration_manager should return instance
        manager = get_configuration_manager()
        self.assertIsNotNone(manager)
        self.assertIsInstance(manager, _ConfigurationManager)

    def test_configuration_manager_enabled_by_default(self):
        """Test that configuration manager is enabled by default when no environment variable is set."""

        # Ensure env var is not set
        if "APPLICATIONINSIGHTS_CONTROLPLANE_DISABLED" in os.environ:
            del os.environ["APPLICATIONINSIGHTS_CONTROLPLANE_DISABLED"]

        # When no env var is set, get_configuration_manager should return instance
        manager = get_configuration_manager()
        self.assertIsNotNone(manager)
        self.assertIsInstance(manager, _ConfigurationManager)


if __name__ == "__main__":
    unittest.main()
