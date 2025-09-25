# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import unittest
from unittest.mock import patch, MagicMock, Mock

from azure.monitor.opentelemetry._browser_sdk_loader._config import BrowserSDKConfig


class TestDjangoMiddleware(unittest.TestCase):
    """Test cases for ApplicationInsightsWebSnippetMiddleware class."""

    def setUp(self):
        """Set up test fixtures."""
        self.get_response_mock = Mock()
        self.connection_string = "InstrumentationKey=12345678-1234-1234-1234-123456789012;IngestionEndpoint=https://test.in.applicationinsights.azure.com/"

    @patch('azure.monitor.opentelemetry._browser_sdk_loader.django_middleware.DJANGO_AVAILABLE', True)
    def test_middleware_initialization_django_available(self):
        """Test middleware initialization when Django is available."""
        from azure.monitor.opentelemetry._browser_sdk_loader.django_middleware import ApplicationInsightsWebSnippetMiddleware
        
        middleware = ApplicationInsightsWebSnippetMiddleware(self.get_response_mock)
        
        self.assertEqual(middleware.get_response, self.get_response_mock)
        self.assertIsNone(middleware._injector)

    @patch('azure.monitor.opentelemetry._browser_sdk_loader.django_middleware.DJANGO_AVAILABLE', False)
    @patch('azure.monitor.opentelemetry._browser_sdk_loader.django_middleware._logger')
    def test_middleware_initialization_django_not_available(self, mock_logger):
        """Test middleware initialization when Django is not available."""
        from azure.monitor.opentelemetry._browser_sdk_loader.django_middleware import ApplicationInsightsWebSnippetMiddleware
        
        middleware = ApplicationInsightsWebSnippetMiddleware(self.get_response_mock)
        
        # Should log warning when Django is not available
        mock_logger.warning.assert_called_once_with(
            "Django not available - ApplicationInsightsWebSnippetMiddleware will not function"
        )

    @patch('azure.monitor.opentelemetry._browser_sdk_loader.django_middleware.DJANGO_AVAILABLE', True)
    @patch('azure.monitor.opentelemetry._browser_sdk_loader.django_middleware.DJANGO_AVAILABLE', True)
    def test_configure_with_browser_sdk_config(self):
        """Test configure method with BrowserSDKConfig object."""
        from azure.monitor.opentelemetry._browser_sdk_loader.django_middleware import ApplicationInsightsWebSnippetMiddleware
        
        middleware = ApplicationInsightsWebSnippetMiddleware(self.get_response_mock)
        config = BrowserSDKConfig(enabled=True, connection_string=self.connection_string)
        
        middleware.configure(config)
        
        self.assertIsNotNone(middleware._injector)
        # Type narrowing assertion for the linter
        assert middleware._injector is not None
        self.assertEqual(middleware._injector.config, config)

    @patch('azure.monitor.opentelemetry._browser_sdk_loader.django_middleware.DJANGO_AVAILABLE', True)
    def test_configure_with_dict_config(self):
        """Test configure method with dictionary configuration."""
        from azure.monitor.opentelemetry._browser_sdk_loader.django_middleware import ApplicationInsightsWebSnippetMiddleware
        
        middleware = ApplicationInsightsWebSnippetMiddleware(self.get_response_mock)
        config_dict = {
            "enabled": True,
            "connection_string": self.connection_string
        }
        
        middleware.configure(config_dict)
        
        self.assertIsNotNone(middleware._injector)
        # Type narrowing assertion for the linter
        assert middleware._injector is not None
        self.assertTrue(middleware._injector.config.enabled)
        self.assertEqual(middleware._injector.config.connection_string, self.connection_string)

    @patch('azure.monitor.opentelemetry._browser_sdk_loader.django_middleware.DJANGO_AVAILABLE', True)
    def test_configure_with_connection_string_legacy(self):
        """Test configure method with connection string (legacy mode)."""
        from azure.monitor.opentelemetry._browser_sdk_loader.django_middleware import ApplicationInsightsWebSnippetMiddleware
        
        middleware = ApplicationInsightsWebSnippetMiddleware(self.get_response_mock)
        
        middleware.configure(self.connection_string)
        
        self.assertIsNotNone(middleware._injector)
        # Type narrowing assertion for the linter
        assert middleware._injector is not None
        self.assertTrue(middleware._injector.config.enabled)
        self.assertEqual(middleware._injector.config.connection_string, self.connection_string)

    @patch('azure.monitor.opentelemetry._browser_sdk_loader.django_middleware.DJANGO_AVAILABLE', True)
    @patch('azure.monitor.opentelemetry._browser_sdk_loader.django_middleware._logger')
    def test_configure_with_invalid_config(self, mock_logger):
        """Test configure method with invalid configuration."""
        from azure.monitor.opentelemetry._browser_sdk_loader.django_middleware import ApplicationInsightsWebSnippetMiddleware

        middleware = ApplicationInsightsWebSnippetMiddleware(self.get_response_mock)

        # Test with invalid config type (integer instead of BrowserSDKConfig/dict/str)
        middleware.configure(12345)  # type: ignore

        # Should log error and not set injector
        mock_logger.error.assert_called_once()
        self.assertIsNone(middleware._injector)

    @patch('azure.monitor.opentelemetry._browser_sdk_loader.django_middleware.DJANGO_AVAILABLE', True)
    def test_process_response_no_injector(self):
        """Test process_response when no injector is configured."""
        from azure.monitor.opentelemetry._browser_sdk_loader.django_middleware import ApplicationInsightsWebSnippetMiddleware
        
        middleware = ApplicationInsightsWebSnippetMiddleware(self.get_response_mock)
        
        # Mock request and response
        mock_request = Mock()
        mock_request.method = "GET"
        mock_response = Mock()
        mock_response.get.return_value = "text/html"
        mock_response.content = b"<html><body>Test</body></html>"
        
        result = middleware.process_response(mock_request, mock_response)
        
        # Should return response unchanged
        self.assertEqual(result, mock_response)

    @patch('azure.monitor.opentelemetry._browser_sdk_loader.django_middleware.DJANGO_AVAILABLE', True)
    def test_process_response_with_injection(self):
        """Test process_response with successful injection."""
        from azure.monitor.opentelemetry._browser_sdk_loader.django_middleware import ApplicationInsightsWebSnippetMiddleware
        
        middleware = ApplicationInsightsWebSnippetMiddleware(self.get_response_mock)
        
        # Configure the middleware
        config = BrowserSDKConfig(enabled=True, connection_string=self.connection_string)
        middleware.configure(config)
        
        # Mock request and response
        mock_request = Mock()
        mock_request.method = "GET"
        mock_response = Mock()
        # Set Content-Encoding to None
        def mock_get(header, default=''):
            if header == 'Content-Type':
                return "text/html"
            elif header == 'Content-Encoding':
                return None
            return default
        mock_response.get = mock_get
        original_content = b"<html><head></head><body>Test</body></html>"
        mock_response.content = original_content

        # Mock the injector's methods
        with patch.object(middleware._injector, 'should_inject', return_value=True), \
             patch.object(middleware._injector, 'inject_with_compression') as mock_inject_with_compression:

            modified_content = b"<html><head><script>injected</script></head><body>Test</body></html>"
            mock_inject_with_compression.return_value = (modified_content, None)

            result = middleware.process_response(mock_request, mock_response)

            # Verify injection was called and content was modified
            mock_inject_with_compression.assert_called_once_with(original_content, None)
            self.assertEqual(mock_response.content, modified_content)
            self.assertEqual(result, mock_response)

    @patch('azure.monitor.opentelemetry._browser_sdk_loader.django_middleware.DJANGO_AVAILABLE', True)
    def test_process_response_should_not_inject(self):
        """Test process_response when injection should not occur."""
        from azure.monitor.opentelemetry._browser_sdk_loader.django_middleware import ApplicationInsightsWebSnippetMiddleware
        
        middleware = ApplicationInsightsWebSnippetMiddleware(self.get_response_mock)
        
        # Configure the middleware
        config = BrowserSDKConfig(enabled=True, connection_string=self.connection_string)
        middleware.configure(config)
        
        # Mock request and response
        mock_request = Mock()
        mock_request.method = "POST"  # Non-GET request
        mock_response = Mock()
        mock_response.get.return_value = "application/json"
        original_content = b'{"message": "test"}'
        mock_response.content = original_content
        
        # Mock the injector's should_inject to return False
        with patch.object(middleware._injector, 'should_inject', return_value=False):
            result = middleware.process_response(mock_request, mock_response)
            
            # Content should remain unchanged
            self.assertEqual(mock_response.content, original_content)
            self.assertEqual(result, mock_response)

    @patch('azure.monitor.opentelemetry._browser_sdk_loader.django_middleware.DJANGO_AVAILABLE', True)
    @patch('azure.monitor.opentelemetry._browser_sdk_loader.django_middleware._logger')
    def test_process_response_injection_exception(self, mock_logger):
        """Test process_response handles injection exceptions gracefully."""
        from azure.monitor.opentelemetry._browser_sdk_loader.django_middleware import ApplicationInsightsWebSnippetMiddleware
        
        middleware = ApplicationInsightsWebSnippetMiddleware(self.get_response_mock)
        
        # Configure the middleware
        config = BrowserSDKConfig(enabled=True, connection_string=self.connection_string)
        middleware.configure(config)
        
        # Mock request and response
        mock_request = Mock()
        mock_request.method = "GET"
        mock_response = Mock()
        mock_response.get.return_value = "text/html"
        # Mock the response as a dict-like object
        response_data = {}
        mock_response.__setitem__ = response_data.__setitem__
        mock_response.__getitem__ = response_data.__getitem__
        original_content = b"<html><body>Test</body></html>"
        mock_response.content = original_content

        # Mock the injector to raise an exception
        with patch.object(middleware._injector, 'should_inject', return_value=True), \
             patch.object(middleware._injector, 'inject_with_compression', side_effect=Exception("Injection failed")):

            result = middleware.process_response(mock_request, mock_response)

            # Should log error and return original response
            mock_logger.warning.assert_called_once()
            self.assertEqual(mock_response.content, original_content)
            self.assertEqual(result, mock_response)

    @patch('azure.monitor.opentelemetry._browser_sdk_loader.django_middleware.DJANGO_AVAILABLE', True)
    def test_process_response_with_content_encoding(self):
        """Test process_response handles compressed content."""
        from azure.monitor.opentelemetry._browser_sdk_loader.django_middleware import ApplicationInsightsWebSnippetMiddleware
        
        middleware = ApplicationInsightsWebSnippetMiddleware(self.get_response_mock)
        
        # Configure the middleware
        config = BrowserSDKConfig(enabled=True, connection_string=self.connection_string)
        middleware.configure(config)
        
        # Mock request and response with gzip encoding
        mock_request = Mock()
        mock_request.method = "GET"
        mock_response = Mock()
        mock_response.get.side_effect = lambda key, default=None: {
            "Content-Type": "text/html",
            "Content-Encoding": "gzip"
        }.get(key, default)
        
        original_content = b"gzip_compressed_content"
        mock_response.content = original_content
        
        # Mock the injector's methods
        with patch.object(middleware._injector, 'should_inject', return_value=True) as mock_should_inject, \
             patch.object(middleware._injector, 'inject_with_compression') as mock_inject_with_compression:
            
            modified_content = b"modified_gzip_content"
            new_encoding = "gzip"
            mock_inject_with_compression.return_value = (modified_content, new_encoding)
            
            result = middleware.process_response(mock_request, mock_response)
            
            # Verify the methods were called correctly
            mock_should_inject.assert_called_once_with(
                "GET", "text/html", original_content, "gzip"
            )
            mock_inject_with_compression.assert_called_once_with(
                original_content, "gzip"
            )
            self.assertEqual(result, mock_response)

    @patch('azure.monitor.opentelemetry._browser_sdk_loader.django_middleware.DJANGO_AVAILABLE', False)
    def test_process_response_django_not_available(self):
        """Test process_response when Django is not available."""
        from azure.monitor.opentelemetry._browser_sdk_loader.django_middleware import ApplicationInsightsWebSnippetMiddleware
        
        middleware = ApplicationInsightsWebSnippetMiddleware(self.get_response_mock)
        
        # Mock request and response
        mock_request = Mock()
        mock_response = Mock()
        
        result = middleware.process_response(mock_request, mock_response)
        
        # Should return response unchanged
        self.assertEqual(result, mock_response)

    @patch('azure.monitor.opentelemetry._browser_sdk_loader.django_middleware.DJANGO_AVAILABLE', True)
    def test_configure_method_with_browser_sdk_config_object(self):
        """Test configure method handles BrowserSDKConfig objects correctly."""
        from azure.monitor.opentelemetry._browser_sdk_loader.django_middleware import ApplicationInsightsWebSnippetMiddleware
        
        middleware = ApplicationInsightsWebSnippetMiddleware(self.get_response_mock)
        config = BrowserSDKConfig(enabled=True, connection_string=self.connection_string)
        
        # This tests my fix where the method needs to handle BrowserSDKConfig objects
        middleware.configure(config)
        
        # Should configure with the BrowserSDKConfig object directly
        self.assertIsNotNone(middleware._injector)
        assert middleware._injector is not None
        self.assertEqual(middleware._injector.config, config)
        self.assertTrue(middleware._injector.config.enabled)
        self.assertEqual(middleware._injector.config.connection_string, self.connection_string)

    @patch('azure.monitor.opentelemetry._browser_sdk_loader.django_middleware.DJANGO_AVAILABLE', True)
    def test_configure_method_with_mixed_config_types(self):
        """Test that configure method can handle both dict and BrowserSDKConfig objects."""
        from azure.monitor.opentelemetry._browser_sdk_loader.django_middleware import ApplicationInsightsWebSnippetMiddleware
        
        middleware1 = ApplicationInsightsWebSnippetMiddleware(self.get_response_mock)
        middleware2 = ApplicationInsightsWebSnippetMiddleware(self.get_response_mock)
        
        # Test with dict config
        dict_config = {"enabled": True, "connection_string": self.connection_string}
        middleware1.configure(dict_config)
        
        # Test with BrowserSDKConfig object
        obj_config = BrowserSDKConfig(enabled=True, connection_string=self.connection_string)
        middleware2.configure(obj_config)
        
        # Both should work
        self.assertIsNotNone(middleware1._injector)
        self.assertIsNotNone(middleware2._injector)
        assert middleware1._injector is not None
        assert middleware2._injector is not None
        
        # Both should have the same connection string
        self.assertEqual(middleware1._injector.config.connection_string, self.connection_string)
        self.assertEqual(middleware2._injector.config.connection_string, self.connection_string)


if __name__ == "__main__":
    unittest.main()
