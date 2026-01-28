# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import threading
import unittest
from unittest.mock import Mock, patch

from azure.monitor.opentelemetry.exporter._constants import (
    DropCode,
    RetryCode,
    _APPLICATIONINSIGHTS_SDKSTATS_DISABLED,
    _REQUEST,
    _DEPENDENCY,
    _CUSTOM_EVENT,
)
from azure.monitor.opentelemetry.exporter.statsbeat.customer._manager import (
    CustomerSdkStatsManager,
    CustomerSdkStatsStatus,
    _CustomerSdkStatsTelemetryCounters,
)


# pylint: disable=protected-access, docstring-missing-param
# pylint: disable=too-many-public-methods
class TestCustomerSdkStatsManager(unittest.TestCase):
    """Test suite for CustomerSdkStatsManager."""

    def setUp(self):
        """Set up test environment."""
        # Enable customer SDK stats for testing
        os.environ[_APPLICATIONINSIGHTS_SDKSTATS_DISABLED] = "false"

        # Reset singleton state - only clear CustomerSdkStatsManager instances
        if CustomerSdkStatsManager in CustomerSdkStatsManager._instances:
            del CustomerSdkStatsManager._instances[CustomerSdkStatsManager]

        # Get a fresh manager instance
        self.manager = CustomerSdkStatsManager()

    def tearDown(self):
        """Clean up test environment."""
        # Clean up environment variables
        os.environ.pop(_APPLICATIONINSIGHTS_SDKSTATS_DISABLED, None)

        # Shutdown manager if needed
        try:
            self.manager.shutdown()
        except:  # pylint: disable=bare-except
            pass

        # Reset singleton state - only clear CustomerSdkStatsManager instances
        if CustomerSdkStatsManager in CustomerSdkStatsManager._instances:
            del CustomerSdkStatsManager._instances[CustomerSdkStatsManager]

    def test_manager_initialization_enabled(self):
        """Test manager initialization when customer SDK stats is enabled."""
        self.assertEqual(self.manager.status, CustomerSdkStatsStatus.UNINITIALIZED)
        self.assertTrue(self.manager.is_enabled)
        self.assertFalse(self.manager.is_initialized)
        self.assertFalse(self.manager.is_shutdown)

    def test_manager_initialization_disabled(self):
        """Test manager initialization when customer SDK stats is disabled."""
        # Disable customer SDK stats
        os.environ[_APPLICATIONINSIGHTS_SDKSTATS_DISABLED] = "true"

        # Create new manager with disabled state
        if hasattr(CustomerSdkStatsManager, "_instances"):
            CustomerSdkStatsManager._instances = {}
        disabled_manager = CustomerSdkStatsManager()

        self.assertEqual(disabled_manager.status, CustomerSdkStatsStatus.DISABLED)
        self.assertFalse(disabled_manager.is_enabled)
        self.assertFalse(disabled_manager.is_initialized)
        self.assertFalse(disabled_manager.is_shutdown)

    @patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter.AzureMonitorMetricExporter")
    @patch("azure.monitor.opentelemetry.exporter.statsbeat.customer._manager.PeriodicExportingMetricReader")
    @patch("azure.monitor.opentelemetry.exporter.statsbeat.customer._manager.MeterProvider")
    def test_initialize_success(self, mock_meter_provider, mock_metric_reader, mock_exporter):
        """Test successful initialization of the manager."""
        # Setup mocks
        mock_meter = Mock()
        mock_meter_provider_instance = Mock()
        mock_meter_provider_instance.get_meter.return_value = mock_meter
        mock_meter_provider.return_value = mock_meter_provider_instance

        mock_success_gauge = Mock()
        mock_dropped_gauge = Mock()
        mock_retry_gauge = Mock()
        mock_meter.create_observable_gauge.side_effect = [mock_success_gauge, mock_dropped_gauge, mock_retry_gauge]

        connection_string = "InstrumentationKey=12345678-1234-5678-abcd-12345678abcd"

        # Test initialization
        result = self.manager.initialize(connection_string)

        self.assertTrue(result)
        self.assertEqual(self.manager.status, CustomerSdkStatsStatus.ACTIVE)
        self.assertTrue(self.manager.is_initialized)
        self.assertFalse(self.manager.is_shutdown)

        # Verify mocks were called
        mock_exporter.assert_called_once()
        mock_metric_reader.assert_called_once()
        mock_meter_provider.assert_called_once()
        self.assertEqual(mock_meter.create_observable_gauge.call_count, 3)

    def test_initialize_disabled_manager(self):
        """Test that initialization fails when manager is disabled."""
        # Disable customer SDK stats
        os.environ[_APPLICATIONINSIGHTS_SDKSTATS_DISABLED] = "true"

        # Create disabled manager
        if hasattr(CustomerSdkStatsManager, "_instances"):
            CustomerSdkStatsManager._instances = {}
        disabled_manager = CustomerSdkStatsManager()

        connection_string = "InstrumentationKey=12345678-1234-5678-abcd-12345678abcd"
        result = disabled_manager.initialize(connection_string)

        self.assertFalse(result)
        self.assertEqual(disabled_manager.status, CustomerSdkStatsStatus.DISABLED)

    def test_initialize_empty_connection_string(self):
        """Test that initialization fails with empty connection string."""
        result = self.manager.initialize("")

        self.assertFalse(result)
        self.assertEqual(self.manager.status, CustomerSdkStatsStatus.UNINITIALIZED)

    def test_initialize_multiple_calls(self):
        """Test that multiple initialization calls are handled correctly."""
        with patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter.AzureMonitorMetricExporter"), patch(
            "azure.monitor.opentelemetry.exporter.statsbeat.customer._manager.PeriodicExportingMetricReader"
        ), patch(
            "azure.monitor.opentelemetry.exporter.statsbeat.customer._manager.MeterProvider"
        ) as mock_meter_provider:
            # Setup mock meter
            mock_meter = Mock()
            mock_meter_provider_instance = Mock()
            mock_meter_provider_instance.get_meter.return_value = mock_meter
            mock_meter_provider.return_value = mock_meter_provider_instance

            connection_string = "InstrumentationKey=12345678-1234-5678-abcd-12345678abcd"

            # First initialization
            result1 = self.manager.initialize(connection_string)
            self.assertTrue(result1)
            self.assertTrue(self.manager.is_initialized)

            # Second initialization should return True but not reinitialize
            result2 = self.manager.initialize(connection_string)
            self.assertTrue(result2)
            self.assertTrue(self.manager.is_initialized)

            # Verify exporter was only created once
            self.assertEqual(mock_meter_provider.call_count, 1)

    @patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter.AzureMonitorMetricExporter")
    def test_initialize_failure(self, mock_exporter):
        """Test initialization failure handling."""
        # Make exporter creation fail
        mock_exporter.side_effect = Exception("Initialization failed")

        connection_string = "InstrumentationKey=12345678-1234-5678-abcd-12345678abcd"
        result = self.manager.initialize(connection_string)

        self.assertFalse(result)
        self.assertEqual(self.manager.status, CustomerSdkStatsStatus.UNINITIALIZED)

    def test_shutdown_uninitialized(self):
        """Test shutdown when manager is not initialized."""
        result = self.manager.shutdown()

        self.assertFalse(result)
        self.assertEqual(self.manager.status, CustomerSdkStatsStatus.UNINITIALIZED)

    def test_shutdown_already_shutdown(self):
        """Test shutdown when manager is already shut down."""
        # Manually set status to shutdown
        self.manager._status = CustomerSdkStatsStatus.SHUTDOWN

        result = self.manager.shutdown()

        self.assertFalse(result)
        self.assertEqual(self.manager.status, CustomerSdkStatsStatus.SHUTDOWN)

    def test_shutdown_success(self):
        """Test successful shutdown of initialized manager."""
        with patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter.AzureMonitorMetricExporter"), patch(
            "azure.monitor.opentelemetry.exporter.statsbeat.customer._manager.PeriodicExportingMetricReader"
        ), patch(
            "azure.monitor.opentelemetry.exporter.statsbeat.customer._manager.MeterProvider"
        ) as mock_meter_provider:
            # Setup mock meter
            mock_meter = Mock()
            mock_meter_provider_instance = Mock()
            mock_meter_provider_instance.get_meter.return_value = mock_meter
            mock_meter_provider.return_value = mock_meter_provider_instance

            # Initialize first
            connection_string = "InstrumentationKey=12345678-1234-5678-abcd-12345678abcd"
            self.manager.initialize(connection_string)
            self.assertTrue(self.manager.is_initialized)

            # Test shutdown
            result = self.manager.shutdown()

            self.assertTrue(result)
            self.assertEqual(self.manager.status, CustomerSdkStatsStatus.SHUTDOWN)
            self.assertTrue(self.manager.is_shutdown)

            # Verify meter provider shutdown was called
            mock_meter_provider_instance.shutdown.assert_called_once()

            # Verify singleton is not cleared on shutdown
            manager2 = CustomerSdkStatsManager()
            self.assertIs(self.manager, manager2)

    def test_shutdown_with_exception(self):
        """Test shutdown when meter provider shutdown throws exception."""
        with patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter.AzureMonitorMetricExporter"), patch(
            "azure.monitor.opentelemetry.exporter.statsbeat.customer._manager.PeriodicExportingMetricReader"
        ), patch(
            "azure.monitor.opentelemetry.exporter.statsbeat.customer._manager.MeterProvider"
        ) as mock_meter_provider:
            # Setup mock meter
            mock_meter = Mock()
            mock_meter_provider_instance = Mock()
            mock_meter_provider_instance.get_meter.return_value = mock_meter
            mock_meter_provider_instance.shutdown.side_effect = Exception("Shutdown failed")
            mock_meter_provider.return_value = mock_meter_provider_instance

            # Initialize first
            connection_string = "InstrumentationKey=12345678-1234-5678-abcd-12345678abcd"
            self.manager.initialize(connection_string)

            # Test shutdown - should still mark as shutdown even if exception occurs
            result = self.manager.shutdown()

            self.assertFalse(result)  # Returns False due to exception
            self.assertEqual(self.manager.status, CustomerSdkStatsStatus.SHUTDOWN)

    def test_count_successful_items(self):
        """Test counting successful items."""
        # Initialize manager
        with patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter.AzureMonitorMetricExporter"), patch(
            "azure.monitor.opentelemetry.exporter.statsbeat.customer._manager.PeriodicExportingMetricReader"
        ), patch(
            "azure.monitor.opentelemetry.exporter.statsbeat.customer._manager.MeterProvider"
        ) as mock_meter_provider:
            mock_meter = Mock()
            mock_meter_provider_instance = Mock()
            mock_meter_provider_instance.get_meter.return_value = mock_meter
            mock_meter_provider.return_value = mock_meter_provider_instance

            connection_string = "InstrumentationKey=12345678-1234-5678-abcd-12345678abcd"
            self.manager.initialize(connection_string)

            # Count successful items
            self.manager.count_successful_items(5, _REQUEST)
            self.manager.count_successful_items(3, _CUSTOM_EVENT)
            self.manager.count_successful_items(2, _REQUEST)  # Add to existing

            # Verify counters
            self.assertEqual(self.manager._counters.total_item_success_count[_REQUEST], 7)
            self.assertEqual(self.manager._counters.total_item_success_count[_CUSTOM_EVENT], 3)

    def test_count_successful_items_uninitialized(self):  # pylint: disable=name-too-long
        """Test that counting successful items does nothing when not initialized."""
        self.manager.count_successful_items(5, _REQUEST)

        # Verify no counters were set
        self.assertEqual(len(self.manager._counters.total_item_success_count), 0)

    def test_count_successful_items_zero_count(self):
        """Test that zero or negative counts are ignored."""
        with patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter.AzureMonitorMetricExporter"), patch(
            "azure.monitor.opentelemetry.exporter.statsbeat.customer._manager.PeriodicExportingMetricReader"
        ), patch(
            "azure.monitor.opentelemetry.exporter.statsbeat.customer._manager.MeterProvider"
        ) as mock_meter_provider:
            mock_meter = Mock()
            mock_meter_provider_instance = Mock()
            mock_meter_provider_instance.get_meter.return_value = mock_meter
            mock_meter_provider.return_value = mock_meter_provider_instance

            connection_string = "InstrumentationKey=12345678-1234-5678-abcd-12345678abcd"
            self.manager.initialize(connection_string)

            # Try to count zero and negative
            self.manager.count_successful_items(0, _REQUEST)
            self.manager.count_successful_items(-1, _REQUEST)

            # Verify no counters were set
            self.assertEqual(len(self.manager._counters.total_item_success_count), 0)

    def test_count_dropped_items(self):
        """Test counting dropped items."""
        with patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter.AzureMonitorMetricExporter"), patch(
            "azure.monitor.opentelemetry.exporter.statsbeat.customer._manager.PeriodicExportingMetricReader"
        ), patch(
            "azure.monitor.opentelemetry.exporter.statsbeat.customer._manager.MeterProvider"
        ) as mock_meter_provider:
            mock_meter = Mock()
            mock_meter_provider_instance = Mock()
            mock_meter_provider_instance.get_meter.return_value = mock_meter
            mock_meter_provider.return_value = mock_meter_provider_instance

            connection_string = "InstrumentationKey=12345678-1234-5678-abcd-12345678abcd"
            self.manager.initialize(connection_string)

            # Count dropped items
            self.manager.count_dropped_items(3, _REQUEST, 404, True)
            self.manager.count_dropped_items(2, _REQUEST, DropCode.UNKNOWN, False)
            self.manager.count_dropped_items(1, _CUSTOM_EVENT, DropCode.CLIENT_EXCEPTION, True, "Custom error")

            # Verify counters structure
            self.assertIn(_REQUEST, self.manager._counters.total_item_drop_count)
            self.assertEqual(self.manager._counters.total_item_drop_count[_REQUEST][404], {"Not found": {True: 3}})
            self.assertEqual(
                self.manager._counters.total_item_drop_count[_REQUEST][DropCode.UNKNOWN], {"Unknown reason": {False: 2}}
            )
            self.assertEqual(
                self.manager._counters.total_item_drop_count[_CUSTOM_EVENT][DropCode.CLIENT_EXCEPTION],
                {"Custom error": {True: 1}},
            )

    def test_count_dropped_items_none_success(self):
        """Test that dropped items with None success are ignored."""
        with patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter.AzureMonitorMetricExporter"), patch(
            "azure.monitor.opentelemetry.exporter.statsbeat.customer._manager.PeriodicExportingMetricReader"
        ), patch(
            "azure.monitor.opentelemetry.exporter.statsbeat.customer._manager.MeterProvider"
        ) as mock_meter_provider:
            mock_meter = Mock()
            mock_meter_provider_instance = Mock()
            mock_meter_provider_instance.get_meter.return_value = mock_meter
            mock_meter_provider.return_value = mock_meter_provider_instance

            connection_string = "InstrumentationKey=12345678-1234-5678-abcd-12345678abcd"
            self.manager.initialize(connection_string)

            # Try to count with None success
            self.manager.count_dropped_items(3, _REQUEST, DropCode.UNKNOWN, None)

            # Verify no counters were set
            self.assertEqual(len(self.manager._counters.total_item_drop_count), 0)

    def test_count_retry_items(self):
        """Test counting retry items."""
        with patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter.AzureMonitorMetricExporter"), patch(
            "azure.monitor.opentelemetry.exporter.statsbeat.customer._manager.PeriodicExportingMetricReader"
        ), patch(
            "azure.monitor.opentelemetry.exporter.statsbeat.customer._manager.MeterProvider"
        ) as mock_meter_provider:
            mock_meter = Mock()
            mock_meter_provider_instance = Mock()
            mock_meter_provider_instance.get_meter.return_value = mock_meter
            mock_meter_provider.return_value = mock_meter_provider_instance

            connection_string = "InstrumentationKey=12345678-1234-5678-abcd-12345678abcd"
            self.manager.initialize(connection_string)

            # Count retry items
            self.manager.count_retry_items(2, _REQUEST, RetryCode.CLIENT_TIMEOUT)
            self.manager.count_retry_items(1, _DEPENDENCY, 500, "Server error")
            self.manager.count_retry_items(3, _REQUEST, RetryCode.CLIENT_TIMEOUT)  # Add to existing

            # Verify counters structure
            self.assertIn(_REQUEST, self.manager._counters.total_item_retry_count)
            self.assertIn(RetryCode.CLIENT_TIMEOUT, self.manager._counters.total_item_retry_count[_REQUEST])

    def test_threading_safety(self):
        """Test that the manager is thread-safe."""
        with patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter.AzureMonitorMetricExporter"), patch(
            "azure.monitor.opentelemetry.exporter.statsbeat.customer._manager.PeriodicExportingMetricReader"
        ), patch(
            "azure.monitor.opentelemetry.exporter.statsbeat.customer._manager.MeterProvider"
        ) as mock_meter_provider:
            mock_meter = Mock()
            mock_meter_provider_instance = Mock()
            mock_meter_provider_instance.get_meter.return_value = mock_meter
            mock_meter_provider.return_value = mock_meter_provider_instance

            connection_string = "InstrumentationKey=12345678-1234-5678-abcd-12345678abcd"
            self.manager.initialize(connection_string)

            # Define a function to run in threads
            def count_items():
                for _ in range(100):
                    self.manager.count_successful_items(1, _REQUEST)
                    self.manager.count_dropped_items(1, _REQUEST, DropCode.UNKNOWN, True)
                    self.manager.count_retry_items(1, _REQUEST, RetryCode.CLIENT_TIMEOUT)

            # Create and start multiple threads
            threads = []
            for _ in range(5):
                thread = threading.Thread(target=count_items)
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # Verify that all counts were recorded (should be 500 total)
            self.assertEqual(self.manager._counters.total_item_success_count[_REQUEST], 500)

    def test_telemetry_counters_initialization(self):
        """Test that TelemetryCounters is properly initialized."""
        counters = _CustomerSdkStatsTelemetryCounters()

        self.assertIsInstance(counters.total_item_success_count, dict)
        self.assertIsInstance(counters.total_item_drop_count, dict)
        self.assertIsInstance(counters.total_item_retry_count, dict)
        self.assertEqual(len(counters.total_item_success_count), 0)
        self.assertEqual(len(counters.total_item_drop_count), 0)
        self.assertEqual(len(counters.total_item_retry_count), 0)

    def test_get_drop_reason(self):
        """Test _get_drop_reason method."""
        with patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter.AzureMonitorMetricExporter"), patch(
            "azure.monitor.opentelemetry.exporter.statsbeat.customer._manager.PeriodicExportingMetricReader"
        ), patch(
            "azure.monitor.opentelemetry.exporter.statsbeat.customer._manager.MeterProvider"
        ) as mock_meter_provider:
            mock_meter = Mock()
            mock_meter_provider_instance = Mock()
            mock_meter_provider_instance.get_meter.return_value = mock_meter
            mock_meter_provider.return_value = mock_meter_provider_instance

            connection_string = "InstrumentationKey=12345678-1234-5678-abcd-12345678abcd"
            self.manager.initialize(connection_string)

            # Test with status code
            reason = self.manager._get_drop_reason(400)
            self.assertEqual(reason, "Bad request")

            # Test with DropCode enum
            reason = self.manager._get_drop_reason(DropCode.CLIENT_READONLY)
            self.assertEqual(reason, "Client readonly")

            # Test with client exception and custom message
            reason = self.manager._get_drop_reason(DropCode.CLIENT_EXCEPTION, "Custom error")
            self.assertEqual(reason, "Custom error")

            # Test with client exception and no message
            reason = self.manager._get_drop_reason(DropCode.CLIENT_EXCEPTION)
            self.assertEqual(reason, "Client exception")

    def test_get_retry_reason(self):
        """Test _get_retry_reason method."""
        with patch("azure.monitor.opentelemetry.exporter.export.metrics._exporter.AzureMonitorMetricExporter"), patch(
            "azure.monitor.opentelemetry.exporter.statsbeat.customer._manager.PeriodicExportingMetricReader"
        ), patch(
            "azure.monitor.opentelemetry.exporter.statsbeat.customer._manager.MeterProvider"
        ) as mock_meter_provider:
            mock_meter = Mock()
            mock_meter_provider_instance = Mock()
            mock_meter_provider_instance.get_meter.return_value = mock_meter
            mock_meter_provider.return_value = mock_meter_provider_instance

            connection_string = "InstrumentationKey=12345678-1234-5678-abcd-12345678abcd"
            self.manager.initialize(connection_string)

            # Test with status code
            reason = self.manager._get_retry_reason(500)
            self.assertEqual(reason, "Internal server error")

            # Test with RetryCode enum
            reason = self.manager._get_retry_reason(RetryCode.CLIENT_TIMEOUT)
            self.assertEqual(reason, "Client timeout")

            # Test with client exception and custom message
            reason = self.manager._get_retry_reason(RetryCode.CLIENT_EXCEPTION, "Network error")
            self.assertEqual(reason, "Network error")

            # Test with client exception and no message
            reason = self.manager._get_retry_reason(RetryCode.CLIENT_EXCEPTION)
            self.assertEqual(reason, "Client exception")


if __name__ == "__main__":
    unittest.main()
