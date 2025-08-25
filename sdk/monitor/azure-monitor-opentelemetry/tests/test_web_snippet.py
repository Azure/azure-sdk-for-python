# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# -------------------------------------------------------------------------

import unittest
from unittest.mock import patch, MagicMock
import gzip
import brotli

from azure.monitor.opentelemetry._web_snippet import (
    WebSnippetConfig,
    WebSnippetInjector,
)


class TestWebSnippetConfig(unittest.TestCase):
    """Tests for WebSnippetConfig class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = WebSnippetConfig()
        self.assertFalse(config.enabled)
        self.assertIsNone(config.connection_string)
        self.assertTrue(config.instrument_user_interactions)
        self.assertTrue(config.cors_correlation)
        self.assertEqual(config.sdk_extension, "a")
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = WebSnippetConfig(
            enabled=True,
            connection_string="InstrumentationKey=test-key;IngestionEndpoint=https://test.com/",
        )
        
        self.assertTrue(config.enabled)
        self.assertEqual(config.connection_string, "InstrumentationKey=test-key;IngestionEndpoint=https://test.com/")
    
    def test_extract_instrumentation_key(self):
        """Test extraction of instrumentation key from connection string."""
        config = WebSnippetConfig(
            connection_string="InstrumentationKey=12345678-1234-1234-1234-123456789012;IngestionEndpoint=https://test.com/"
        )
        
        key = config._extract_instrumentation_key()
        self.assertEqual(key, "12345678-1234-1234-1234-123456789012")
    
    def test_extract_instrumentation_key_no_connection_string(self):
        """Test instrumentation key extraction with no connection string."""
        config = WebSnippetConfig()
        
        key = config._extract_instrumentation_key()
        self.assertIsNone(key)
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = WebSnippetConfig(
            enabled=True,
            connection_string="InstrumentationKey=test-key;IngestionEndpoint=https://test.com/",
        )
        
        result = config.to_dict()
        
        self.assertTrue(result["enabled"])
        self.assertEqual(result["connectionString"], "InstrumentationKey=test-key;IngestionEndpoint=https://test.com/")
        self.assertEqual(result["cfg"]["instrumentationKey"], "test-key")
        self.assertEqual(result["cfg"]["sdkExtension"], "a")


class TestWebSnippetInjector(unittest.TestCase):
    """Tests for WebSnippetInjector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = WebSnippetConfig(
            enabled=True,
            connection_string="InstrumentationKey=test-key;IngestionEndpoint=https://test.com/"
        )
        self.injector = WebSnippetInjector(self.config)
    
    def test_should_inject_valid_request(self):
        """Test should_inject with valid HTML GET request."""
        content = b"<html><head></head><body></body></html>"
        
        result = self.injector.should_inject("GET", "text/html", content)
        
        self.assertTrue(result)
    
    def test_should_inject_valid_request_with_encoding(self):
        """Test should_inject with valid HTML GET request and content encoding."""
        content = b"<html><head></head><body></body></html>"
        
        result = self.injector.should_inject("GET", "text/html", content, "gzip")
        
        self.assertTrue(result)
    
    def test_should_inject_disabled_config(self):
        """Test should_inject with disabled configuration."""
        disabled_config = WebSnippetConfig(enabled=False)
        disabled_injector = WebSnippetInjector(disabled_config)
        content = b"<html><head></head><body></body></html>"
        
        result = disabled_injector.should_inject("GET", "text/html", content)
        
        self.assertFalse(result)
    
    def test_should_inject_non_get_request(self):
        """Test should_inject with non-GET request."""
        content = b"<html><head></head><body></body></html>"
        
        result = self.injector.should_inject("POST", "text/html", content)
        
        self.assertFalse(result)
    
    def test_should_inject_non_html_content(self):
        """Test should_inject with non-HTML content."""
        content = b'{"message": "hello"}'
        
        result = self.injector.should_inject("GET", "application/json", content)
        
        self.assertFalse(result)
    
    def test_should_inject_existing_web_sdk(self):
        """Test should_inject with existing Web SDK."""
        content = b"<html><head><script>appInsights.trackPageView()</script></head><body></body></html>"
        
        result = self.injector.should_inject("GET", "text/html", content)
        
        self.assertFalse(result)
    
    def test_should_inject_existing_web_sdk_compressed(self):
        """Test should_inject with existing Web SDK in compressed content."""
        content = b"<html><head><script>appInsights.trackPageView()</script></head><body></body></html>"
        compressed_content = gzip.compress(content)
        
        result = self.injector.should_inject("GET", "text/html", compressed_content, "gzip")
        
        self.assertFalse(result)
    
    def test_inject_snippet_before_head_end(self):
        """Test snippet injection before </head> tag."""
        content = b"<html><head><title>Test</title></head><body></body></html>"
        
        result = self.injector.inject_snippet(content)
        
        result_str = result.decode("utf-8")
        self.assertIn("appInsights", result_str)
        self.assertIn("</head>", result_str)
        # Check that snippet is before </head>
        snippet_pos = result_str.find("appInsights")
        head_end_pos = result_str.find("</head>")
        self.assertLess(snippet_pos, head_end_pos)
    
    def test_inject_snippet_before_body_start(self):
        """Test snippet injection before <body> tag when no </head>."""
        content = b"<html><body></body></html>"
        
        result = self.injector.inject_snippet(content)
        
        result_str = result.decode("utf-8")
        self.assertIn("appInsights", result_str)
        # Check that snippet is before <body>
        snippet_pos = result_str.find("appInsights")
        body_pos = result_str.find("<body")
        self.assertLess(snippet_pos, body_pos)
    
    def test_inject_with_gzip_compression(self):
        """Test snippet injection with gzip compression."""
        content = b"<html><head></head><body></body></html>"
        compressed_content = gzip.compress(content)
        
        result, encoding = self.injector.inject_with_compression(
            compressed_content, 
            "gzip"
        )
        
        # Decompress and check result
        decompressed = gzip.decompress(result)
        result_str = decompressed.decode("utf-8")
        self.assertIn("appInsights", result_str)
        self.assertEqual(encoding, "gzip")
    
    def test_inject_with_brotli_compression(self):
        """Test snippet injection with brotli compression."""
        content = b"<html><head></head><body></body></html>"
        compressed_content = brotli.compress(content)
        
        result, encoding = self.injector.inject_with_compression(
            compressed_content,
            "br"
        )
        
        # Decompress and check result
        decompressed = brotli.decompress(result)
        result_str = decompressed.decode("utf-8")
        self.assertIn("appInsights", result_str)
        self.assertEqual(encoding, "br")
    
    def test_inject_no_compression(self):
        """Test snippet injection without compression."""
        content = b"<html><head></head><body></body></html>"
        
        result, encoding = self.injector.inject_with_compression(content, None)
        
        result_str = result.decode("utf-8")
        self.assertIn("appInsights", result_str)
        self.assertIsNone(encoding)
    
    def test_dict_to_js_object(self):
        """Test dictionary to JavaScript object conversion."""
        test_dict = {
            "string": "value",
            "number": 42,
            "boolean": True,
            "nested": {"key": "value"}
        }
        
        result = self.injector._dict_to_js_object(test_dict)
        
        expected = 'string: "value", number: 42, boolean: true, nested: {key: "value"}'
        # Check individual parts since order might vary
        self.assertIn('"value"', result)
        self.assertIn('42', result)
        self.assertIn('true', result)
        self.assertIn('nested:', result)


if __name__ == "__main__":
    unittest.main()
