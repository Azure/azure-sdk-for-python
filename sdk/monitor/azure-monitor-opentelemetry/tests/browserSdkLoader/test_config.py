# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import unittest
from unittest.mock import patch, MagicMock

from azure.monitor.opentelemetry._browser_sdk_loader._config import BrowserSDKConfig


class TestBrowserSDKConfig(unittest.TestCase):
    """Test cases for BrowserSDKConfig class."""

    def test_browser_sdk_config_default_values(self):
        """Test BrowserSDKConfig initialization with default values."""
        config = BrowserSDKConfig()
        
        self.assertTrue(config.enabled)
        self.assertEqual(config.connection_string, "")

    def test_browser_sdk_config_custom_values(self):
        """Test BrowserSDKConfig initialization with custom values."""
        connection_string = "InstrumentationKey=12345678-1234-1234-1234-123456789012;IngestionEndpoint=https://test.in.applicationinsights.azure.com/"
        
        config = BrowserSDKConfig(
            enabled=False,
            connection_string=connection_string
        )
        
        self.assertFalse(config.enabled)
        self.assertEqual(config.connection_string, connection_string)

    def test_browser_sdk_config_none_connection_string(self):
        """Test BrowserSDKConfig with None connection string."""
        config = BrowserSDKConfig(
            enabled=True,
            connection_string=None
        )
        
        self.assertTrue(config.enabled)
        self.assertEqual(config.connection_string, "")

    def test_browser_sdk_config_empty_connection_string(self):
        """Test BrowserSDKConfig with empty connection string."""
        config = BrowserSDKConfig(
            enabled=True,
            connection_string=""
        )
        
        self.assertTrue(config.enabled)
        self.assertEqual(config.connection_string, "")


if __name__ == "__main__":
    unittest.main()
