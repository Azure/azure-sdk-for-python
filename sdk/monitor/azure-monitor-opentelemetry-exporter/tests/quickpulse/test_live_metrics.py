# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

# cSpell:disable

import unittest
from unittest import mock

from opentelemetry.sdk.resources import Resource

from azure.monitor.opentelemetry.exporter._quickpulse._live_metrics import enable_live_metrics


class TestLiveMetrics(unittest.TestCase):
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics.set_statsbeat_live_metrics_feature_set")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics.get_quickpulse_manager")
    def test_enable_live_metrics_basic(self, manager_mock, statsbeat_mock):
        """Test basic enable_live_metrics functionality."""
        mock_resource = Resource.create({"service.name": "test-service"})
        mock_manager_instance = mock.Mock()
        mock_manager_instance.initialize.return_value = True
        manager_mock.return_value = mock_manager_instance

        enable_live_metrics(
            connection_string="InstrumentationKey=test-key", resource=mock_resource, credential="test-credential"
        )

        # Verify manager was obtained (likely returns singleton instance)
        manager_mock.assert_called_once()

        # Verify manager was initialized with correct kwargs
        mock_manager_instance.initialize.assert_called_once_with(
            connection_string="InstrumentationKey=test-key",
            resource=mock_resource,
            credential="test-credential",
        )

        # Verify statsbeat feature was set
        statsbeat_mock.assert_called_once()

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics.set_statsbeat_live_metrics_feature_set")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics.get_quickpulse_manager")
    def test_enable_live_metrics_initialization_fails(self, manager_mock, statsbeat_mock):
        """Test enable_live_metrics when manager initialization fails."""
        mock_manager_instance = mock.Mock()
        mock_manager_instance.initialize.return_value = False
        manager_mock.return_value = mock_manager_instance

        enable_live_metrics(connection_string="InstrumentationKey=test-key")

        # Verify manager was obtained
        manager_mock.assert_called_once()

        # Verify manager was initialized with connection string
        mock_manager_instance.initialize.assert_called_once_with(connection_string="InstrumentationKey=test-key")

        # Verify statsbeat feature was still set (regardless of initialization success)
        statsbeat_mock.assert_called_once()

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics.set_statsbeat_live_metrics_feature_set")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics.get_quickpulse_manager")
    def test_enable_live_metrics_with_minimal_args(self, manager_mock, statsbeat_mock):
        """Test enable_live_metrics with minimal arguments."""
        mock_manager_instance = mock.Mock()
        mock_manager_instance.initialize.return_value = True
        manager_mock.return_value = mock_manager_instance

        enable_live_metrics()

        # Verify manager was obtained
        manager_mock.assert_called_once()

        # Verify initialization was attempted with no kwargs
        mock_manager_instance.initialize.assert_called_once_with()

        # Verify statsbeat feature was set
        statsbeat_mock.assert_called_once()

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics.set_statsbeat_live_metrics_feature_set")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics.get_quickpulse_manager")
    def test_enable_live_metrics_with_all_parameters(self, manager_mock, statsbeat_mock):
        """Test enable_live_metrics with all possible parameters."""
        mock_resource = Resource.create(
            {"service.name": "test-service", "service.version": "1.0.0", "deployment.environment": "test"}
        )
        mock_credential = mock.Mock()
        mock_manager_instance = mock.Mock()
        mock_manager_instance.initialize.return_value = True
        manager_mock.return_value = mock_manager_instance

        enable_live_metrics(
            connection_string="InstrumentationKey=test-key;EndpointSuffix=applicationinsights.azure.cn",
            credential=mock_credential,
            resource=mock_resource,
            custom_param="custom_value",  # Test that additional kwargs are passed through
        )

        # Verify manager was obtained
        manager_mock.assert_called_once()

        # Verify initialization was called with all parameters including custom ones
        mock_manager_instance.initialize.assert_called_once_with(
            connection_string="InstrumentationKey=test-key;EndpointSuffix=applicationinsights.azure.cn",
            credential=mock_credential,
            resource=mock_resource,
            custom_param="custom_value",
        )

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics.set_statsbeat_live_metrics_feature_set")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics.get_quickpulse_manager")
    def test_enable_live_metrics_with_none_values(self, manager_mock, statsbeat_mock):
        """Test enable_live_metrics with None values for optional parameters."""
        mock_manager_instance = mock.Mock()
        mock_manager_instance.initialize.return_value = True
        manager_mock.return_value = mock_manager_instance

        enable_live_metrics(connection_string=None, resource=None, credential=None)

        # Verify manager was obtained
        manager_mock.assert_called_once()

        # Verify initialization was called with None values
        mock_manager_instance.initialize.assert_called_once_with(connection_string=None, resource=None, credential=None)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics.set_statsbeat_live_metrics_feature_set")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics.get_quickpulse_manager")
    def test_enable_live_metrics_empty_string_connection(self, manager_mock, statsbeat_mock):
        """Test enable_live_metrics with empty string connection string."""
        mock_manager_instance = mock.Mock()
        mock_manager_instance.initialize.return_value = True
        manager_mock.return_value = mock_manager_instance

        enable_live_metrics(connection_string="")

        # Verify manager was obtained
        manager_mock.assert_called_once()

        # Verify initialization was called with empty string
        mock_manager_instance.initialize.assert_called_once_with(connection_string="")

        # Verify statsbeat feature was set
        statsbeat_mock.assert_called_once()

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics.set_statsbeat_live_metrics_feature_set")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics.get_quickpulse_manager")
    def test_enable_live_metrics_complex_resource(self, manager_mock, statsbeat_mock):
        """Test enable_live_metrics with complex resource attributes."""
        mock_resource = Resource.create(
            {
                "service.name": "test-service",
                "service.version": "1.2.3",
                "service.namespace": "test-namespace",
                "deployment.environment": "production",
                "cloud.provider": "azure",
                "cloud.platform": "azure_app_service",
                "host.name": "test-host",
                "process.pid": 12345,
                "telemetry.sdk.name": "opentelemetry",
                "telemetry.sdk.language": "python",
                "telemetry.sdk.version": "1.0.0",
            }
        )
        mock_manager_instance = mock.Mock()
        mock_manager_instance.initialize.return_value = True
        manager_mock.return_value = mock_manager_instance

        enable_live_metrics(connection_string="InstrumentationKey=test-key", resource=mock_resource)

        # Verify manager was obtained
        manager_mock.assert_called_once()

        # Verify initialization was called with complex resource
        mock_manager_instance.initialize.assert_called_once_with(
            connection_string="InstrumentationKey=test-key", resource=mock_resource
        )

        # Verify statsbeat feature was set
        statsbeat_mock.assert_called_once()

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics.set_statsbeat_live_metrics_feature_set")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics.get_quickpulse_manager")
    def test_enable_live_metrics_multiple_calls(self, manager_mock, statsbeat_mock):
        """Test multiple calls to enable_live_metrics."""
        mock_manager_instance = mock.Mock()
        mock_manager_instance.initialize.return_value = True
        manager_mock.return_value = mock_manager_instance

        # First call
        enable_live_metrics(connection_string="InstrumentationKey=test-key1")

        # Second call with different parameters
        enable_live_metrics(connection_string="InstrumentationKey=test-key2")

        # Verify manager was obtained twice (since it's likely a singleton, this tests the behavior)
        self.assertEqual(manager_mock.call_count, 2)

        # Verify initialization was called twice with different parameters
        expected_calls = [
            mock.call(connection_string="InstrumentationKey=test-key1"),
            mock.call(connection_string="InstrumentationKey=test-key2"),
        ]
        mock_manager_instance.initialize.assert_has_calls(expected_calls)

        # Verify statsbeat feature was set twice
        self.assertEqual(statsbeat_mock.call_count, 2)

    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics.set_statsbeat_live_metrics_feature_set")
    @mock.patch("azure.monitor.opentelemetry.exporter._quickpulse._live_metrics.get_quickpulse_manager")
    def test_enable_live_metrics_kwargs_preservation(self, manager_mock, statsbeat_mock):
        """Test that all kwargs are properly passed through to initialize."""
        mock_manager_instance = mock.Mock()
        mock_manager_instance.initialize.return_value = True
        manager_mock.return_value = mock_manager_instance

        custom_kwargs = {
            "connection_string": "InstrumentationKey=test-key",
            "custom_param1": "value1",
            "custom_param2": 42,
            "custom_param3": True,
            "custom_param4": ["list", "of", "values"],
            "custom_param5": {"nested": "dict"},
        }

        enable_live_metrics(**custom_kwargs)

        # Verify manager was obtained
        manager_mock.assert_called_once()

        # Verify all kwargs were passed through to initialize
        mock_manager_instance.initialize.assert_called_once_with(**custom_kwargs)

        # Verify statsbeat feature was set
        statsbeat_mock.assert_called_once()


# cSpell:enable
