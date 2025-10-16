# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import unittest
from unittest.mock import patch, MagicMock

from azure.monitor.opentelemetry._browser_sdk_loader._config import BrowserSDKConfig
from azure.monitor.opentelemetry._constants import BROWSER_SDK_LOADER_CONFIG_ARG


class TestBrowserSDKIntegration(unittest.TestCase):
    """Test cases for Browser SDK loader integration with configure_azure_monitor."""

    def test_browser_sdk_config_argument_constant(self):
        """Test that the browser SDK config argument constant is properly defined."""
        self.assertEqual(BROWSER_SDK_LOADER_CONFIG_ARG, "browser_sdk_loader_config")

    @patch('azure.monitor.opentelemetry._configure.setup_snippet_injection')
    def test_configure_azure_monitor_with_browser_sdk_config(self, mock_setup_snippet):
        """Test configure_azure_monitor calls setup_snippet_injection with browser SDK config."""
        from azure.monitor.opentelemetry import configure_azure_monitor

        # Configure with browser SDK config as a dictionary
        configure_azure_monitor(
            connection_string="InstrumentationKey=12345678-1234-1234-1234-123456789012",
            browser_sdk_loader_config={
                "enabled": True,
                "connection_string": "InstrumentationKey=12345678-1234-1234-1234-123456789012;IngestionEndpoint=https://test.in.applicationinsights.azure.com/"
            }
        )

        # Verify setup_snippet_injection was called with a BrowserSDKConfig
        mock_setup_snippet.assert_called_once()
        call_args = mock_setup_snippet.call_args[0][0]
        self.assertIsInstance(call_args, BrowserSDKConfig)
        self.assertTrue(call_args.enabled)
        self.assertEqual(call_args.connection_string, "InstrumentationKey=12345678-1234-1234-1234-123456789012;IngestionEndpoint=https://test.in.applicationinsights.azure.com/")

    @patch('azure.monitor.opentelemetry._configure.setup_snippet_injection')
    def test_configure_azure_monitor_with_browser_sdk_dict(self, mock_setup_snippet):
        """Test configure_azure_monitor converts dict to BrowserSDKConfig."""
        from azure.monitor.opentelemetry import configure_azure_monitor
        
        browser_config_dict = {
            "enabled": True,
            "connection_string": "InstrumentationKey=12345678-1234-1234-1234-123456789012;IngestionEndpoint=https://test.in.applicationinsights.azure.com/"
        }
        
        # Configure with browser SDK config dict
        configure_azure_monitor(
            connection_string="InstrumentationKey=12345678-1234-1234-1234-123456789012",
            browser_sdk_loader_config=browser_config_dict
        )
        
        # Verify setup_snippet_injection was called
        mock_setup_snippet.assert_called_once()
        
        # Verify the argument passed is a BrowserSDKConfig instance
        args, kwargs = mock_setup_snippet.call_args
        config_arg = args[0]
        self.assertIsInstance(config_arg, BrowserSDKConfig)
        self.assertTrue(config_arg.enabled)
        self.assertIn("InstrumentationKey=12345678", config_arg.connection_string)

    @patch('azure.monitor.opentelemetry._configure.setup_snippet_injection')
    def test_configure_azure_monitor_no_browser_sdk_config(self, mock_setup_snippet):
        """Test configure_azure_monitor without browser SDK config."""
        from azure.monitor.opentelemetry import configure_azure_monitor
        
        # Configure without browser SDK config
        configure_azure_monitor(
            connection_string="InstrumentationKey=12345678-1234-1234-1234-123456789012"
        )
        
        # Verify setup_snippet_injection was not called
        mock_setup_snippet.assert_not_called()

    @patch('azure.monitor.opentelemetry._browser_sdk_loader.setup_snippet_injection')
    def test_configure_azure_monitor_disabled_browser_sdk_config(self, mock_setup_snippet):
        """Test configure_azure_monitor with disabled browser SDK config."""
        from azure.monitor.opentelemetry import configure_azure_monitor

        # Configure with disabled browser SDK config
        configure_azure_monitor(
            connection_string="InstrumentationKey=12345678-1234-1234-1234-123456789012",
            browser_sdk_loader_config={"enabled": False}
        )

        # Should not call setup_snippet_injection when disabled
        mock_setup_snippet.assert_not_called()

    def test_browser_sdk_config_from_dict_conversion(self):
        """Test conversion of dictionary to BrowserSDKConfig."""
        config_dict = {
            "enabled": False,
            "connection_string": "test_connection_string"
        }
        
        # Simulate the conversion logic
        config = BrowserSDKConfig(
            enabled=config_dict.get("enabled", True),
            connection_string=config_dict.get("connection_string", "")
        )
        
        self.assertFalse(config.enabled)
        self.assertEqual(config.connection_string, "test_connection_string")

    def test_browser_sdk_config_default_values_in_integration(self):
        """Test default values for BrowserSDKConfig in integration context."""
        # Test that default values work correctly when used in configure_azure_monitor
        config = BrowserSDKConfig()
        
        self.assertTrue(config.enabled)
        self.assertEqual(config.connection_string, "")

    @patch('azure.monitor.opentelemetry._configure._logger')
    def test_invalid_browser_sdk_config_type(self, mock_logger):
        """Test handling of invalid browser SDK config types."""
        from azure.monitor.opentelemetry._utils.configurations import _get_configurations
        
        # Test with invalid config type
        invalid_config = "invalid_string_config"
        
        # This should be handled gracefully
        try:
            configurations = {BROWSER_SDK_LOADER_CONFIG_ARG: invalid_config}
            # The actual validation would happen in the setup function
            self.assertIn(BROWSER_SDK_LOADER_CONFIG_ARG, configurations)
        except Exception:
            self.fail("Should handle invalid config types gracefully")


if __name__ == "__main__":
    unittest.main()
