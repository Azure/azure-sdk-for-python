# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import gzip
import unittest
from unittest.mock import patch, MagicMock

from azure.monitor.opentelemetry._browser_sdk_loader._config import BrowserSDKConfig
from azure.monitor.opentelemetry._browser_sdk_loader.snippet_injector import WebSnippetInjector


class TestWebSnippetInjector(unittest.TestCase):
    """Test cases for WebSnippetInjector class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = BrowserSDKConfig(
            enabled=True,
            connection_string="InstrumentationKey=12345678-1234-1234-1234-123456789012;IngestionEndpoint=https://test.in.applicationinsights.azure.com/"
        )
        self.injector = WebSnippetInjector(self.config)

    def test_injector_initialization(self):
        """Test WebSnippetInjector initialization."""
        self.assertEqual(self.injector.config, self.config)
        self.assertIsNone(self.injector._web_sdk_snippet_cache)
        self.assertIsNone(self.injector._decompressed_content_cache)
        self.assertIsNone(self.injector._cache_key)

    def test_should_inject_disabled_config(self):
        """Test should_inject returns False when config is disabled."""
        disabled_config = BrowserSDKConfig(enabled=False)
        injector = WebSnippetInjector(disabled_config)
        
        result = injector.should_inject("GET", "text/html", b"<html></html>")
        self.assertFalse(result)

    def test_should_inject_non_get_request(self):
        """Test should_inject returns False for non-GET requests."""
        result = self.injector.should_inject("POST", "text/html", b"<html></html>")
        self.assertFalse(result)

    def test_should_inject_non_html_content_type(self):
        """Test should_inject returns False for non-HTML content types."""
        test_cases = [
            ("application/json", b'{"key": "value"}'),
            ("text/plain", b"plain text"),
            ("image/png", b"binary image data"),
            (None, b"<html></html>"),
            ("", b"<html></html>"),
        ]
        
        for content_type, content in test_cases:
            with self.subTest(content_type=content_type):
                result = self.injector.should_inject("GET", content_type, content)
                self.assertFalse(result)

    def test_should_inject_html_content_type_variations(self):
        """Test should_inject returns True for various HTML content types."""
        html_content = b"<html><head></head><body></body></html>"
        html_content_types = [
            "text/html",
            "text/html; charset=utf-8",
            "Text/HTML",
            "TEXT/HTML; CHARSET=UTF-8",
            "application/xhtml+xml",
        ]
        
        for content_type in html_content_types:
            with self.subTest(content_type=content_type):
                result = self.injector.should_inject("GET", content_type, html_content)
                self.assertTrue(result)

    def test_should_inject_existing_app_insights_sdk(self):
        """Test should_inject returns False when App Insights SDK is already present."""
        test_cases = [
            b"<html><script>appInsights.trackPageView();</script></html>",
            b"<html><script>ApplicationInsights.init();</script></html>",
            b"<html><script src='https://js.monitor.azure.com/scripts/b/ai.2.min.js'></script></html>",
            b"<html><!-- appinsights snippet already here --></html>",
        ]
        
        for content in test_cases:
            with self.subTest(content=content):
                result = self.injector.should_inject("GET", "text/html", content)
                self.assertFalse(result)

    def test_should_inject_compressed_content(self):
        """Test should_inject works with compressed content."""
        html_content = b"<html><head></head><body><h1>Test</h1></body></html>"
        compressed_content = gzip.compress(html_content)
        
        result = self.injector.should_inject("GET", "text/html", compressed_content, "gzip")
        self.assertTrue(result)

    def test_should_inject_compressed_with_existing_sdk(self):
        """Test should_inject returns False for compressed content with existing SDK."""
        html_content = b"<html><script>appInsights.trackPageView();</script></html>"
        compressed_content = gzip.compress(html_content)
        
        result = self.injector.should_inject("GET", "text/html", compressed_content, "gzip")
        self.assertFalse(result)

    def test_inject_snippet_basic_html(self):
        """Test inject_snippet with basic HTML content."""
        html_content = b"<html><head></head><body><h1>Test</h1></body></html>"
        
        result = self.injector.inject_snippet(html_content)
        
        # Verify the content contains both original HTML and injected script
        result_str = result.decode('utf-8')
        self.assertIn("<h1>Test</h1>", result_str)
        self.assertIn("appInsightsSDK", result_str)
        self.assertIn("https://js.monitor.azure.com/scripts/b/ai.2.min.js", result_str)

    def test_inject_snippet_no_head_tag(self):
        """Test inject_snippet handles HTML without head tag."""
        html_content = b"<html><body><h1>No head tag</h1></body></html>"
        
        result = self.injector.inject_snippet(html_content)
        
        # Should still inject the snippet somewhere
        result_str = result.decode('utf-8')
        self.assertIn("appInsightsSDK", result_str)

    def test_inject_snippet_multiple_calls_uses_cache(self):
        """Test inject_snippet uses cache for repeated calls."""
        html_content = b"<html><head></head><body></body></html>"
        
        # First call
        result1 = self.injector.inject_snippet(html_content)
        # Second call should use cache
        result2 = self.injector.inject_snippet(html_content)
        
        self.assertEqual(result1, result2)
        # Verify cache was populated
        self.assertIsNotNone(self.injector._web_sdk_snippet_cache)

    def test_inject_snippet_with_connection_string_config(self):
        """Test inject_snippet includes connection string configuration."""
        html_content = b"<html><head></head><body></body></html>"
        
        result = self.injector.inject_snippet(html_content)
        result_str = result.decode('utf-8')
        
        # Should contain connection string configuration
        self.assertIn("connectionString", result_str)
        self.assertIn("test.in.applicationinsights.azure.com", result_str)

    def test_appears_compressed_detection(self):
        """Test _appears_compressed method with various content types."""
        # Test with uncompressed content
        uncompressed = b"<html>normal content</html>"
        self.assertFalse(self.injector._appears_compressed(uncompressed))
        
        # Test with gzip compressed content
        gzip_content = gzip.compress(b"<html>compressed</html>")
        self.assertTrue(self.injector._appears_compressed(gzip_content))

    def test_get_decompressed_content_uncompressed(self):
        """Test _get_decompressed_content with uncompressed content."""
        content = b"<html>test content</html>"
        
        result = self.injector._get_decompressed_content(content, None)
        
        self.assertEqual(result, content)

    def test_get_decompressed_content_gzip(self):
        """Test _get_decompressed_content with gzip compressed content."""
        original = b"<html>test content</html>"
        compressed = gzip.compress(original)
        
        result = self.injector._get_decompressed_content(compressed, "gzip")
        
        self.assertEqual(result, original)

    def test_decompress_content_invalid_encoding(self):
        """Test _decompress_content with invalid encoding."""
        content = b"some content"
        
        result = self.injector._decompress_content(content, "invalid")
        
        # Should return original content when encoding is unsupported
        self.assertEqual(result, content)

    @patch('azure.monitor.opentelemetry._browser_sdk_loader.snippet_injector.HAS_BROTLI', False)
    def test_decompress_content_brotli_not_available(self):
        """Test _decompress_content when brotli is not available."""
        content = b"some content"
        
        with patch('azure.monitor.opentelemetry._browser_sdk_loader.snippet_injector._logger') as mock_logger:
            result = self.injector._decompress_content(content, "br")
            
            # Should log warning and return original content
            mock_logger.warning.assert_called_once()
            self.assertEqual(result, content)

    def test_compress_content_gzip(self):
        """Test _compress_content with gzip encoding."""
        content = b"<html>test content</html>"
        
        result = self.injector._compress_content(content, "gzip")
        
        # Verify the content was compressed
        decompressed = gzip.decompress(result)
        self.assertEqual(decompressed, content)

    @patch('azure.monitor.opentelemetry._browser_sdk_loader.snippet_injector.HAS_BROTLI', False)
    def test_compress_content_brotli_not_available(self):
        """Test _compress_content when brotli is not available."""
        content = b"some content"
        
        with patch('azure.monitor.opentelemetry._browser_sdk_loader.snippet_injector._logger') as mock_logger:
            result = self.injector._compress_content(content, "br")
            
            # Should log warning and return original content
            mock_logger.warning.assert_called_once()
            self.assertEqual(result, content)

    def test_format_config_value_string(self):
        """Test _format_config_value with string values."""
        result = self.injector._format_config_value("test_string")
        self.assertEqual(result, '"test_string"')

    def test_format_config_value_boolean(self):
        """Test _format_config_value with boolean values."""
        self.assertEqual(self.injector._format_config_value(True), "true")
        self.assertEqual(self.injector._format_config_value(False), "false")

    def test_format_config_value_numbers(self):
        """Test _format_config_value with numeric values."""
        self.assertEqual(self.injector._format_config_value(42), "42")
        self.assertEqual(self.injector._format_config_value(3.14), "3.14")

    def test_clear_decompression_cache(self):
        """Test _clear_decompression_cache method."""
        # Populate cache
        self.injector._decompressed_content_cache = b"cached content"
        self.injector._cache_key = ("test", "key")
        
        self.injector._clear_decompression_cache()
        
        # Verify cache was cleared
        self.assertIsNone(self.injector._decompressed_content_cache)
        self.assertIsNone(self.injector._cache_key)

    def test_inject_with_compression_uncompressed(self):
        """Test inject_with_compression with uncompressed content."""
        html_content = b"<html><head></head><body><h1>Test</h1></body></html>"
        
        result_content, result_encoding = self.injector.inject_with_compression(html_content)
        
        # Should inject snippet and return no encoding for uncompressed content
        result_str = result_content.decode('utf-8')
        self.assertIn("appInsightsSDK", result_str)
        self.assertIn("<h1>Test</h1>", result_str)
        self.assertIsNone(result_encoding)

    def test_inject_with_compression_gzip(self):
        """Test inject_with_compression with gzip compressed content."""
        html_content = b"<html><head></head><body><h1>Test</h1></body></html>"
        compressed_content = gzip.compress(html_content)
        
        result_content, result_encoding = self.injector.inject_with_compression(compressed_content, "gzip")
        
        # Should return gzip compressed content with injected snippet
        self.assertEqual(result_encoding, "gzip")
        
        # Decompress to verify injection occurred
        decompressed_result = gzip.decompress(result_content)
        result_str = decompressed_result.decode('utf-8')
        self.assertIn("appInsightsSDK", result_str)
        self.assertIn("<h1>Test</h1>", result_str)

    def test_inject_with_compression_existing_sdk(self):
        """Test inject_with_compression skips injection when SDK already exists."""
        html_with_sdk = b"<html><script>appInsights.trackPageView();</script></html>"
        
        result_content, result_encoding = self.injector.inject_with_compression(html_with_sdk)
        
        # Should return original content unchanged
        self.assertEqual(result_content, html_with_sdk)
        self.assertIsNone(result_encoding)

    def test_inject_with_compression_exception_handling(self):
        """Test inject_with_compression handles exceptions gracefully."""
        with patch.object(self.injector, '_get_decompressed_content', side_effect=Exception("Test exception")):
            html_content = b"<html><body>Test</body></html>"
            
            result_content, result_encoding = self.injector.inject_with_compression(html_content)
            
            # Should return original content on exception
            self.assertEqual(result_content, html_content)
            self.assertIsNone(result_encoding)

    def test_should_inject_html_comments_detection(self):
        """Test detection of HTML comments indicating Application Insights is already present."""
        # Test cases that should be detected (should_inject returns False)
        positive_cases = [
            b"<html><!-- AppInsights snippet already here --></html>",
            b"<html><!-- APPINSIGHTS SNIPPET PRESENT --></html>",
            b"<html><!-- appinsights snippet here already --></html>",
            b"<html><!-- Application Insights snippet already present --></html>",
        ]
        
        for content in positive_cases:
            with self.subTest(content=content):
                result = self.injector.should_inject("GET", "text/html", content)
                self.assertFalse(result, f"Should detect existing snippet in: {content}")

    def test_should_inject_html_comments_false_positives(self):
        """Test that descriptive text doesn't trigger false positive detection."""
        # Test cases that should NOT be detected (should_inject returns True)
        negative_cases = [
            b"<html><!-- This page needs Application Insights tracking --></html>",
            b"<html><!-- TODO: Add appinsights configuration --></html>",
            b"<html><!-- Remember to configure the application insights library --></html>",
            b"<html><!-- appinsights documentation available online --></html>",
            b"<html><p>This application uses appinsights for monitoring</p></html>",
        ]
        
        for content in negative_cases:
            with self.subTest(content=content):
                result = self.injector.should_inject("GET", "text/html", content)
                self.assertTrue(result, f"Should NOT detect existing snippet in: {content}")

    def test_should_inject_javascript_detection_patterns(self):
        """Test detection of actual JavaScript Application Insights code."""
        # Test cases with actual JavaScript patterns
        javascript_cases = [
            b"<html><script>var appInsights = new ApplicationInsights();</script></html>",
            b"<html><script>appInsights = {};</script></html>",
            b"<html><script>window.appInsights.trackPageView();</script></html>",
            b"<html><script>ApplicationInsights.init({});</script></html>",
            b"<html><script>Microsoft.ApplicationInsights.Telemetry.track();</script></html>",
        ]
        
        for content in javascript_cases:
            with self.subTest(content=content):
                result = self.injector.should_inject("GET", "text/html", content)
                self.assertFalse(result, f"Should detect existing JavaScript in: {content}")

    def test_should_inject_script_url_detection(self):
        """Test detection of Application Insights script URLs."""
        # Test cases with script URLs
        url_cases = [
            b"<html><script src='https://js.monitor.azure.com/scripts/b/ai.2.min.js'></script></html>",
            b"<html><script src='/static/ai.2.min.js'></script></html>",
            b"<html><script src='//cdn.example.com/js.monitor.azure.com/ai.js'></script></html>",
        ]
        
        for content in url_cases:
            with self.subTest(content=content):
                result = self.injector.should_inject("GET", "text/html", content)
                self.assertFalse(result, f"Should detect existing script URL in: {content}")


if __name__ == "__main__":
    unittest.main()
