# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import unittest
from unittest.mock import Mock, patch

from azure.monitor.opentelemetry.exporter._configuration import (
    _ConfigurationManager,
    _ConfigurationState,
    _update_configuration_and_get_refresh_interval,
)
from azure.monitor.opentelemetry.exporter._configuration._utils import OneSettingsResponse
from azure.monitor.opentelemetry.exporter._constants import (
    _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS,
    _ONE_SETTINGS_PYTHON_KEY,
    _ONE_SETTINGS_CHANGE_URL,
    _ONE_SETTINGS_CONFIG_URL,
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
        # Reset the singleton instance and class variables
        _ConfigurationManager._instance = None
        _ConfigurationManager._configuration_worker = None
        _ConfigurationManager._current_state = _ConfigurationState()

    def tearDown(self):
        """Clean up after each test."""
        # Shutdown any running workers
        if _ConfigurationManager._instance and _ConfigurationManager._instance._configuration_worker:
            _ConfigurationManager._instance.shutdown()
        # Reset singleton
        _ConfigurationManager._instance = None
        _ConfigurationManager._configuration_worker = None
        _ConfigurationManager._current_state = _ConfigurationState()

    @patch("azure.monitor.opentelemetry.exporter._configuration._worker._ConfigurationWorker")
    def test_singleton_pattern(self, mock_worker_class):
        """Test that ConfigurationManager follows singleton pattern."""
        # Create first instance
        manager1 = _ConfigurationManager()

        # Create second instance
        manager2 = _ConfigurationManager()

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

        # Verify worker was created with correct refresh interval (default 30)
        mock_worker_class.assert_called_once_with(_ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS)
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

        # Execute
        result = manager.get_configuration_and_refresh_interval({"param": "value"})

        # Verify return value
        self.assertEqual(result, 1800)

        # Verify state was updated (now using class variables consistently)
        current_state = _ConfigurationManager._current_state
        self.assertEqual(current_state.etag, "test-etag")
        self.assertEqual(current_state.refresh_interval, 1800)
        self.assertEqual(current_state.version_cache, -1)  # No version change
        self.assertEqual(current_state.settings_cache, {})  # No settings update since no CONFIG fetch

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
        current_state = _ConfigurationManager._current_state
        self.assertEqual(current_state.version_cache, 5)
        self.assertEqual(current_state.settings_cache, {"key": "config_value"})
        self.assertEqual(result, 1800)

    @patch("azure.monitor.opentelemetry.exporter._configuration.make_onesettings_request")
    @patch("azure.monitor.opentelemetry.exporter._configuration._worker._ConfigurationWorker")
    def test_version_same_no_config_fetch(self, mock_worker_class, mock_request):
        """Test that same version does not trigger CONFIG fetch."""
        manager = _ConfigurationManager()

        # Set initial version using class variable
        _ConfigurationManager._current_state = _ConfigurationManager._current_state.with_updates(version_cache=5)

        # Mock response with same version
        mock_response = OneSettingsResponse(
            etag="test-etag", refresh_interval=1800, settings={"key": "value"}, version=5, status_code=200
        )
        mock_request.return_value = mock_response

        # Execute
        manager.get_configuration_and_refresh_interval()

        # Verify only one call was made (to CHANGE endpoint)
        mock_request.assert_called_once()
        self.assertEqual(mock_request.call_args[0][0], _ONE_SETTINGS_CHANGE_URL)

    @patch("azure.monitor.opentelemetry.exporter._configuration.make_onesettings_request")
    @patch("azure.monitor.opentelemetry.exporter._configuration._worker._ConfigurationWorker")
    @patch("azure.monitor.opentelemetry.exporter._configuration.logger")
    def test_version_decrease_warning(self, mock_logger, mock_worker_class, mock_request):
        """Test warning when version decreases."""
        manager = _ConfigurationManager()

        # Set initial version using class variable
        _ConfigurationManager._current_state = _ConfigurationManager._current_state.with_updates(version_cache=10)

        # Mock response with decreased version
        mock_response = OneSettingsResponse(
            etag="test-etag", refresh_interval=1800, settings={"key": "value"}, version=5, status_code=200
        )
        mock_request.return_value = mock_response

        # Execute
        manager.get_configuration_and_refresh_interval()

        # Verify warning was logged
        mock_logger.warning.assert_called_once()
        warning_message = mock_logger.warning.call_args[0][0]
        self.assertIn("lower than cached version", warning_message)

        # Version cache should not be updated
        self.assertEqual(_ConfigurationManager._current_state.version_cache, 10)

    @patch("azure.monitor.opentelemetry.exporter._configuration.make_onesettings_request")
    @patch("azure.monitor.opentelemetry.exporter._configuration._worker._ConfigurationWorker")
    def test_304_not_modified_response(self, mock_worker_class, mock_request):
        """Test handling of 304 Not Modified response."""
        manager = _ConfigurationManager()

        # Set initial state using class variable
        _ConfigurationManager._current_state = _ConfigurationManager._current_state.with_updates(
            etag="old-etag", refresh_interval=1800, version_cache=5, settings_cache={"existing": "value"}
        )

        # Mock 304 response
        mock_response = OneSettingsResponse(etag="new-etag", refresh_interval=2400, status_code=304)
        mock_request.return_value = mock_response

        # Execute
        result = manager.get_configuration_and_refresh_interval()

        # Verify etag and refresh interval updated, but settings/version preserved
        current_state = _ConfigurationManager._current_state
        self.assertEqual(current_state.etag, "new-etag")
        self.assertEqual(current_state.refresh_interval, 2400)
        self.assertEqual(current_state.version_cache, 5)  # Preserved
        self.assertEqual(current_state.settings_cache, {"existing": "value"})  # Preserved
        self.assertEqual(result, 2400)

    @patch("azure.monitor.opentelemetry.exporter._configuration.make_onesettings_request")
    @patch("azure.monitor.opentelemetry.exporter._configuration._worker._ConfigurationWorker")
    @patch("azure.monitor.opentelemetry.exporter._configuration.logger")
    def test_config_endpoint_failure_preserves_etag(self, mock_logger, mock_worker_class, mock_request):
        """Test that CONFIG endpoint failure preserves ETag for retry."""
        manager = _ConfigurationManager()

        # Mock responses
        change_response = OneSettingsResponse(
            etag="test-etag", refresh_interval=1800, settings={"key": "value"}, version=5, status_code=200
        )
        config_response = OneSettingsResponse(status_code=500)  # Server error

        def mock_request_side_effect(url, query_dict, headers=None):
            if url == _ONE_SETTINGS_CHANGE_URL:
                return change_response
            elif url == _ONE_SETTINGS_CONFIG_URL:
                return config_response
            return OneSettingsResponse()

        mock_request.side_effect = mock_request_side_effect

        # Execute
        manager.get_configuration_and_refresh_interval()

        # Verify warning was logged
        mock_logger.warning.assert_called()

        # Verify ETag was not updated due to CONFIG failure
        current_state = _ConfigurationManager._current_state
        self.assertEqual(current_state.etag, "")  # Should remain empty
        self.assertEqual(current_state.refresh_interval, 1800)  # Should still be updated

    @patch("azure.monitor.opentelemetry.exporter._configuration.make_onesettings_request")
    @patch("azure.monitor.opentelemetry.exporter._configuration._worker._ConfigurationWorker")
    @patch("azure.monitor.opentelemetry.exporter._configuration.logger")
    def test_version_mismatch_between_endpoints(self, mock_logger, mock_worker_class, mock_request):
        """Test handling of version mismatch between CHANGE and CONFIG endpoints."""
        manager = _ConfigurationManager()

        # Mock responses with mismatched versions
        change_response = OneSettingsResponse(
            etag="test-etag", refresh_interval=1800, settings={"key": "value"}, version=5, status_code=200
        )
        config_response = OneSettingsResponse(
            settings={"key": "config_value"}, version=6, status_code=200  # Different version!
        )

        def mock_request_side_effect(url, query_dict, headers=None):
            if url == _ONE_SETTINGS_CHANGE_URL:
                return change_response
            elif url == _ONE_SETTINGS_CONFIG_URL:
                return config_response
            return OneSettingsResponse()

        mock_request.side_effect = mock_request_side_effect

        # Execute
        manager.get_configuration_and_refresh_interval()

        # Verify warning was logged
        mock_logger.warning.assert_called()
        warning_message = mock_logger.warning.call_args[0][0]
        self.assertIn("Version mismatch", warning_message)

        # Verify ETag was not updated due to version mismatch
        current_state = _ConfigurationManager._current_state
        self.assertEqual(current_state.etag, "")  # Should remain empty
        self.assertEqual(current_state.version_cache, -1)  # Should not be updated

    def test_get_settings(self):
        """Test get_settings returns copy of settings cache."""
        manager = _ConfigurationManager()

        # Set some settings using class variable
        test_settings = {"key1": "value1", "key2": "value2"}
        _ConfigurationManager._current_state = _ConfigurationManager._current_state.with_updates(
            settings_cache=test_settings
        )

        # Get settings
        returned_settings = manager.get_settings()

        # Verify correct settings returned
        self.assertEqual(returned_settings, test_settings)

        # Verify it's a copy (modifying returned dict doesn't affect internal state)
        returned_settings["key3"] = "value3"
        self.assertEqual(_ConfigurationManager._current_state.settings_cache, test_settings)

    def test_get_current_version(self):
        """Test get_current_version returns current version."""
        manager = _ConfigurationManager()

        # Set version using class variable
        _ConfigurationManager._current_state = _ConfigurationManager._current_state.with_updates(version_cache=42)

        # Verify version returned
        self.assertEqual(manager.get_current_version(), 42)

    @patch("azure.monitor.opentelemetry.exporter._configuration._worker._ConfigurationWorker")
    def test_shutdown(self, mock_worker_class):
        """Test shutdown properly cleans up worker and instance."""
        mock_worker_instance = Mock()
        mock_worker_class.return_value = mock_worker_instance

        manager = _ConfigurationManager()

        # Verify worker exists
        self.assertIsNotNone(manager._configuration_worker)
        self.assertIsNotNone(_ConfigurationManager._instance)

        # Shutdown
        manager.shutdown()

        # Verify cleanup
        mock_worker_instance.shutdown.assert_called_once()
        self.assertIsNone(_ConfigurationManager._configuration_worker)
        self.assertIsNone(_ConfigurationManager._instance)


class TestUpdateConfigurationFunction(unittest.TestCase):
    """Test cases for _update_configuration_and_get_refresh_interval function."""

    def setUp(self):
        """Reset singleton state before each test."""
        _ConfigurationManager._instance = None
        _ConfigurationManager._configuration_worker = None
        _ConfigurationManager._current_state = _ConfigurationState()

    def tearDown(self):
        """Clean up after each test."""
        if _ConfigurationManager._instance and _ConfigurationManager._instance._configuration_worker:
            _ConfigurationManager._instance.shutdown()
        _ConfigurationManager._instance = None
        _ConfigurationManager._configuration_worker = None
        _ConfigurationManager._current_state = _ConfigurationState()

    @patch.object(_ConfigurationManager, "get_configuration_and_refresh_interval")
    @patch("azure.monitor.opentelemetry.exporter._configuration._worker._ConfigurationWorker")
    def test_update_configuration_function(self, mock_worker_class, mock_get_config):
        """Test _update_configuration_and_get_refresh_interval function calls manager correctly."""
        # Setup
        mock_get_config.return_value = 3600

        # Execute
        result = _update_configuration_and_get_refresh_interval()

        # Verify
        self.assertEqual(result, 3600)
        mock_get_config.assert_called_once_with({"namespaces": _ONE_SETTINGS_PYTHON_KEY})


if __name__ == "__main__":
    unittest.main()
