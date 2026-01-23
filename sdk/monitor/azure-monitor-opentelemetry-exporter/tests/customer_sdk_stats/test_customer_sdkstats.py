# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import unittest
from unittest import mock

from azure.monitor.opentelemetry.exporter._constants import (
    _APPLICATIONINSIGHTS_SDKSTATS_DISABLED,
)
from azure.monitor.opentelemetry.exporter.statsbeat.customer._state import (
    get_customer_stats_manager,
)
from azure.monitor.opentelemetry.exporter.statsbeat.customer._customer_sdkstats import (
    collect_customer_sdkstats,
    shutdown_customer_sdkstats_metrics,
)


class TestCustomerSdkStats(unittest.TestCase):
    """Test suite for customer SDK stats core functionality."""

    def setUp(self):
        """Set up test environment and ensure customer SDKStats is enabled."""
        # Enable customer SDK stats for testing
        os.environ[_APPLICATIONINSIGHTS_SDKSTATS_DISABLED] = "false"

        # Reset the customer stats manager for each test
        manager = get_customer_stats_manager()
        manager.shutdown()

    def tearDown(self):
        """Clean up test environment."""
        # Clean up environment variables
        os.environ.pop(_APPLICATIONINSIGHTS_SDKSTATS_DISABLED, None)

        # Shutdown customer stats
        manager = get_customer_stats_manager()
        manager.shutdown()

    def test_collect_customer_sdkstats(self):
        """Test collecting customer SDK stats initializes the manager."""
        # Create a mock exporter
        mock_exporter = mock.Mock()
        mock_exporter._connection_string = (
            "InstrumentationKey=12345678-1234-5678-abcd-12345678abcd"  # pylint: disable=protected-access
        )

        # Collect customer SDK stats
        collect_customer_sdkstats(mock_exporter)

        # Verify manager is initialized
        manager = get_customer_stats_manager()
        self.assertTrue(manager.is_initialized)

    def test_collect_customer_sdkstats_multiple_calls(self):  # pylint: disable=name-too-long
        """Test that multiple calls to collect_customer_sdkstats don't cause issues."""
        # Create a mock exporter
        mock_exporter = mock.Mock()
        mock_exporter._connection_string = (
            "InstrumentationKey=12345678-1234-5678-abcd-12345678abcd"  # pylint: disable=protected-access
        )

        # Call collect multiple times
        collect_customer_sdkstats(mock_exporter)
        collect_customer_sdkstats(mock_exporter)
        collect_customer_sdkstats(mock_exporter)

        # Verify manager is still properly initialized
        manager = get_customer_stats_manager()
        self.assertTrue(manager.is_initialized)

    def test_shutdown_customer_sdkstats_metrics(self):
        """Test shutting down customer SDK stats metrics."""
        # Initialize first
        manager = get_customer_stats_manager()
        manager.initialize("InstrumentationKey=12345678-1234-5678-abcd-12345678abcd")
        self.assertTrue(manager.is_initialized)

        # Shutdown
        shutdown_customer_sdkstats_metrics()

        # Verify shutdown
        self.assertFalse(manager.is_initialized)

    def test_shutdown_customer_sdkstats_metrics_when_not_initialized(self):  # pylint: disable=name-too-long
        """Test shutting down customer SDK stats when not initialized doesn't cause issues."""
        # Ensure manager is not initialized
        manager = get_customer_stats_manager()
        manager.shutdown()
        self.assertFalse(manager.is_initialized)

        # Shutdown when already shut down should not cause issues
        shutdown_customer_sdkstats_metrics()

        # Verify still shut down
        self.assertFalse(manager.is_initialized)

    def test_collect_and_shutdown_cycle(self):
        """Test a complete cycle of collect and shutdown operations."""
        # Create a mock exporter
        mock_exporter = mock.Mock()
        mock_exporter._connection_string = (
            "InstrumentationKey=12345678-1234-5678-abcd-12345678abcd"  # pylint: disable=protected-access
        )

        # Collect customer SDK stats
        collect_customer_sdkstats(mock_exporter)
        manager = get_customer_stats_manager()
        self.assertTrue(manager.is_initialized)

        # Shutdown
        shutdown_customer_sdkstats_metrics()
        self.assertFalse(manager.is_initialized)

        # Collect again
        collect_customer_sdkstats(mock_exporter)
        self.assertTrue(manager.is_initialized)

        # Final shutdown
        shutdown_customer_sdkstats_metrics()
        self.assertFalse(manager.is_initialized)


if __name__ == "__main__":
    unittest.main()
