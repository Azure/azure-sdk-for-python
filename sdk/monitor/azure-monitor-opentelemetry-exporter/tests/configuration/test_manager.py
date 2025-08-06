# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import unittest
import threading
from unittest.mock import Mock, patch

from azure.monitor.opentelemetry.exporter._configuration import (
    _ConfigurationManager,
    _update_configuration_and_get_refresh_interval,
)
from azure.monitor.opentelemetry.exporter._configuration._utils import OneSettingsResponse
from azure.monitor.opentelemetry.exporter._constants import (
    _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS,
    _ONE_SETTINGS_PYTHON_KEY,
    _ONE_SETTINGS_CHANGE_URL,
)


class TestConfigurationManager(unittest.TestCase):
    """Test cases for _ConfigurationManager class."""

    def setUp(self):
        """Reset singleton state before each test."""
        # Reset the singleton instance
        _ConfigurationManager._instance = None
        _ConfigurationManager._configuration_worker = None
        _ConfigurationManager._etag = None
        _ConfigurationManager._refresh_interval = _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS
        _ConfigurationManager._settings_cache = {}
        _ConfigurationManager._version_cache = 0

    def tearDown(self):
        """Clean up after each test."""
        # Shutdown any running workers
        if _ConfigurationManager._instance and _ConfigurationManager._instance._configuration_worker:
            _ConfigurationManager._instance.shutdown()
        # Reset singleton
        _ConfigurationManager._instance = None
        _ConfigurationManager._configuration_worker = None

    @patch('azure.monitor.opentelemetry.exporter._configuration._worker._ConfigurationWorker')
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

    @patch('azure.monitor.opentelemetry.exporter._configuration._worker._ConfigurationWorker')
    def test_worker_initialization(self, mock_worker_class):
        """Test that ConfigurationWorker is initialized properly."""
        mock_worker_instance = Mock()
        mock_worker_class.return_value = mock_worker_instance

        manager = _ConfigurationManager()

        # Verify worker was created with correct refresh interval
        mock_worker_class.assert_called_once_with(_ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS)
        self.assertEqual(manager._configuration_worker, mock_worker_instance)

    @patch('azure.monitor.opentelemetry.exporter._configuration.make_onesettings_request')
    @patch('azure.monitor.opentelemetry.exporter._configuration._worker._ConfigurationWorker')
    def test_get_configuration_and_refresh_interval(self, mock_worker_class, mock_request):
        """Test get_configuration_and_refresh_interval method."""
        # Setup
        mock_response = OneSettingsResponse(
            etag="test-etag",
            refresh_interval=1800.0,
            settings={"key1": "value1"},
            version=5
        )
        mock_request.return_value = mock_response

        manager = _ConfigurationManager()

        # Execute
        result = manager.get_configuration_and_refresh_interval({"param": "value"})

        # Verify
        self.assertEqual(result, 1800.0)
        self.assertEqual(manager._etag, "test-etag")
        self.assertEqual(manager._refresh_interval, 1800.0)
        self.assertEqual(manager._version_cache, 5)

        # Verify request was made with correct parameters
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        self.assertEqual(call_args[0][0], _ONE_SETTINGS_CHANGE_URL)  # URL
        self.assertEqual(call_args[0][1], {"param": "value"})  # query_dict

    @patch('azure.monitor.opentelemetry.exporter._configuration.make_onesettings_request')
    @patch('azure.monitor.opentelemetry.exporter._configuration._worker._ConfigurationWorker')
    def test_etag_headers(self, mock_worker_class, mock_request):
        """Test that etag is included in request headers."""
        # Setup - first call sets etag
        mock_response1 = OneSettingsResponse(etag="test-etag", refresh_interval=1800.0)
        mock_request.return_value = mock_response1

        manager = _ConfigurationManager()
        manager.get_configuration_and_refresh_interval()

        # Setup - second call should include etag
        mock_response2 = OneSettingsResponse(etag="new-etag", refresh_interval=2400.0)
        mock_request.return_value = mock_response2

        # Execute second call
        manager.get_configuration_and_refresh_interval()

        # Verify second call included etag in headers
        self.assertEqual(mock_request.call_count, 2)
        second_call_args = mock_request.call_args
        headers = second_call_args[0][2]  # headers parameter
        self.assertEqual(headers["If-None-Match"], "test-etag")
        self.assertEqual(headers["x-ms-onesetinterval"], "1800.0")

    @patch('azure.monitor.opentelemetry.exporter._configuration.make_onesettings_request')
    @patch('azure.monitor.opentelemetry.exporter._configuration._worker._ConfigurationWorker')
    def test_version_cache_logic(self, mock_worker_class, mock_request):
        """Test version cache update logic."""
        manager = _ConfigurationManager()

        # Test version increase (should update cache)
        mock_response = OneSettingsResponse(
            settings={"key": "value"},
            version=5
        )
        mock_request.return_value = mock_response

        manager.get_configuration_and_refresh_interval()
        self.assertEqual(manager._version_cache, 5)

        # Test same version (should not change cache)
        mock_response = OneSettingsResponse(
            settings={"key": "value"},
            version=5
        )
        mock_request.return_value = mock_response

        manager.get_configuration_and_refresh_interval()
        self.assertEqual(manager._version_cache, 5)

        # Test version increase again
        mock_response = OneSettingsResponse(
            settings={"key": "value"},
            version=7
        )
        mock_request.return_value = mock_response

        manager.get_configuration_and_refresh_interval()
        self.assertEqual(manager._version_cache, 7)

    @patch('azure.monitor.opentelemetry.exporter._configuration.make_onesettings_request')
    @patch('azure.monitor.opentelemetry.exporter._configuration._worker._ConfigurationWorker')
    @patch('azure.monitor.opentelemetry.exporter._configuration.logger')
    def test_version_decrease_warning(self, mock_logger, mock_worker_class, mock_request):
        """Test warning when version decreases."""
        manager = _ConfigurationManager()

        # Set initial version
        mock_response = OneSettingsResponse(
            settings={"key": "value"},
            version=10
        )
        mock_request.return_value = mock_response
        manager.get_configuration_and_refresh_interval()

        # Test version decrease (should log warning)
        mock_response = OneSettingsResponse(
            settings={"key": "value"},
            version=5
        )
        mock_request.return_value = mock_response

        manager.get_configuration_and_refresh_interval()

        # Verify warning was logged
        mock_logger.warning.assert_called_once()
        warning_message = mock_logger.warning.call_args[0][0]
        self.assertIn("CHANGE_VERSION", warning_message)
        self.assertIn("less than", warning_message)

        # Version cache should not be updated
        self.assertEqual(manager._version_cache, 10)

    def test_get_python_configuration_call(self):
        """Test _update_configuration_and_get_refresh_interval function calls manager correctly."""
        with patch.object(_ConfigurationManager, 'get_configuration_and_refresh_interval') as mock_get_config:
            mock_get_config.return_value = 1800.0

            # Call the global function
            result = _update_configuration_and_get_refresh_interval()

            # Verify it called the manager with correct parameters
            mock_get_config.assert_called_once_with({"namespaces": _ONE_SETTINGS_PYTHON_KEY})
            self.assertEqual(result, 1800.0)

    @patch('azure.monitor.opentelemetry.exporter._configuration._worker._ConfigurationWorker')
    def test_settings_cache_thread_safety(self, mock_worker_class):
        """Test thread safety of settings cache."""
        manager = _ConfigurationManager()

        # Test that settings_lock protects cache access
        self.assertIsNotNone(manager._settings_lock)

        # Set some cache data directly (simulating what the real implementation would do)
        with manager._settings_lock:
            manager._settings_cache = {"key1": "value1"}

        # Verify cache was set
        with manager._settings_lock:
            self.assertEqual(manager._settings_cache, {"key1": "value1"})

    @patch('azure.monitor.opentelemetry.exporter._configuration._worker._ConfigurationWorker')
    def test_version_lock_thread_safety(self, mock_worker_class):
        """Test thread safety of version cache."""
        manager = _ConfigurationManager()

        # Test that version_lock protects version cache access
        self.assertIsNotNone(manager._version_lock)

        # Test direct version cache access
        with manager._version_lock:
            initial_version = manager._version_cache
            self.assertIsInstance(initial_version, int)

    @patch('azure.monitor.opentelemetry.exporter._configuration._worker._ConfigurationWorker')
    def test_config_lock_thread_safety(self, mock_worker_class):
        """Test thread safety of config state."""
        manager = _ConfigurationManager()

        # Test that config_lock protects etag and refresh_interval access
        self.assertIsNotNone(manager._config_lock)

        # Test direct access to protected attributes
        with manager._config_lock:
            etag = manager._etag
            refresh_interval = manager._refresh_interval
            # These should be accessible without error

    @patch('azure.monitor.opentelemetry.exporter._configuration._worker._ConfigurationWorker')
    def test_shutdown(self, mock_worker_class):
        """Test shutdown method."""
        mock_worker_instance = Mock()
        mock_worker_class.return_value = mock_worker_instance

        manager = _ConfigurationManager()

        # Call shutdown
        manager.shutdown()

        # Verify worker shutdown was called
        mock_worker_instance.shutdown.assert_called_once()
        self.assertIsNone(manager._instance)

    def test_thread_safety_singleton(self):
        """Test thread safety of singleton pattern."""
        instances = []

        def create_instance():
            with patch('azure.monitor.opentelemetry.exporter._configuration._worker._ConfigurationWorker'):
                instance = _ConfigurationManager()
                instances.append(instance)

        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=create_instance)
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All instances should be the same
        first_instance = instances[0]
        for instance in instances[1:]:
            self.assertIs(instance, first_instance)


class TestUpdateConfigurationFunction(unittest.TestCase):
    """Test cases for _update_configuration_and_get_refresh_interval function."""

    def setUp(self):
        """Reset singleton state before each test."""
        _ConfigurationManager._instance = None
        _ConfigurationManager._configuration_worker = None

    def tearDown(self):
        """Clean up after each test."""
        if _ConfigurationManager._instance and _ConfigurationManager._instance._configuration_worker:
            _ConfigurationManager._instance.shutdown()
        _ConfigurationManager._instance = None
        _ConfigurationManager._configuration_worker = None

    @patch.object(_ConfigurationManager, 'get_configuration_and_refresh_interval')
    @patch('azure.monitor.opentelemetry.exporter._configuration._worker._ConfigurationWorker')
    def test_update_configuration_function(self, mock_worker_class, mock_get_config):
        """Test _update_configuration_and_get_refresh_interval function."""
        mock_get_config.return_value = 2400.0

        result = _update_configuration_and_get_refresh_interval()

        # Verify the function called the manager with correct parameters
        mock_get_config.assert_called_once_with({"namespaces": _ONE_SETTINGS_PYTHON_KEY})
        self.assertEqual(result, 2400.0)
