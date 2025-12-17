# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import json
import unittest
from unittest.mock import Mock, patch
import requests

from azure.monitor.opentelemetry.exporter._configuration._utils import (
    OneSettingsResponse,
    make_onesettings_request,
    _parse_onesettings_response,
)
from azure.monitor.opentelemetry.exporter._constants import (
    _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS,
    _ONE_SETTINGS_CHANGE_VERSION_KEY,
)


class TestOneSettingsResponse(unittest.TestCase):
    """Test cases for OneSettingsResponse class."""

    def test_init_default_values(self):
        """Test OneSettingsResponse initialization with default values."""
        response = OneSettingsResponse()

        self.assertIsNone(response.etag)
        self.assertEqual(response.refresh_interval, _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS)
        self.assertEqual(response.settings, {})
        self.assertIsNone(response.version)
        self.assertEqual(response.status_code, 200)

    def test_init_custom_values(self):
        """Test OneSettingsResponse initialization with custom values."""
        etag = "test-etag"
        refresh_interval = 1800
        settings = {"key1": "value1", "key2": "value2"}
        version = 5
        status_code = 304

        response = OneSettingsResponse(etag, refresh_interval, settings, version, status_code)

        self.assertEqual(response.etag, etag)
        self.assertEqual(response.refresh_interval, refresh_interval)
        self.assertEqual(response.settings, settings)
        self.assertEqual(response.version, version)
        self.assertEqual(response.status_code, status_code)

    def test_init_empty_settings_dict(self):
        """Test OneSettingsResponse handles None settings correctly."""
        response = OneSettingsResponse(settings=None)

        self.assertEqual(response.settings, {})

    def test_init_custom_status_code(self):
        """Test OneSettingsResponse with custom status code."""
        response = OneSettingsResponse(status_code=404)

        self.assertEqual(response.status_code, 404)


class TestMakeOneSettingsRequest(unittest.TestCase):
    """Test cases for make_onesettings_request function."""

    @patch("azure.monitor.opentelemetry.exporter._configuration._utils.requests.get")
    @patch("azure.monitor.opentelemetry.exporter._configuration._utils._parse_onesettings_response")
    def test_successful_request(self, mock_parse, mock_get):
        """Test successful OneSettings request."""
        # Setup
        mock_response = Mock()
        mock_get.return_value = mock_response
        expected_response = OneSettingsResponse(etag="test-etag", status_code=200)
        mock_parse.return_value = expected_response

        url = "https://test.example.com"
        query_dict = {"param1": "value1"}
        headers = {"header1": "value1"}

        # Execute
        result = make_onesettings_request(url, query_dict, headers)

        # Verify
        mock_get.assert_called_once_with(url, params=query_dict, headers=headers, timeout=10)
        mock_response.raise_for_status.assert_called_once()
        mock_parse.assert_called_once_with(mock_response)
        self.assertEqual(result, expected_response)

    @patch("azure.monitor.opentelemetry.exporter._configuration._utils.requests.get")
    def test_request_with_none_params(self, mock_get):
        """Test OneSettings request with None parameters."""
        # Setup
        mock_response = Mock()
        mock_get.return_value = mock_response
        url = "https://test.example.com"

        # Execute
        make_onesettings_request(url, None, None)

        # Verify
        mock_get.assert_called_once_with(url, params={}, headers={}, timeout=10)

    @patch("azure.monitor.opentelemetry.exporter._configuration._utils.requests.get")
    def test_request_exception_handling(self, mock_get):
        """Test OneSettings request exception handling."""
        # Setup
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        url = "https://test.example.com"

        # Execute
        with patch("azure.monitor.opentelemetry.exporter._configuration._utils.logger") as mock_logger:
            result = make_onesettings_request(url)

        # Verify
        self.assertIsInstance(result, OneSettingsResponse)
        self.assertIsNone(result.etag)
        self.assertEqual(result.settings, {})
        self.assertEqual(result.status_code, 200)  # Default status code
        mock_logger.warning.assert_called_once()

    @patch("azure.monitor.opentelemetry.exporter._configuration._utils.requests.get")
    def test_json_decode_error_handling(self, mock_get):
        """Test OneSettings request JSON decode error handling."""
        # Setup
        mock_response = Mock()
        mock_get.return_value = mock_response
        mock_response.raise_for_status.return_value = None

        with patch(
            "azure.monitor.opentelemetry.exporter._configuration._utils._parse_onesettings_response"
        ) as mock_parse:
            mock_parse.side_effect = json.JSONDecodeError("Invalid JSON", "doc", 0)

            # Execute
            with patch("azure.monitor.opentelemetry.exporter._configuration._utils.logger") as mock_logger:
                result = make_onesettings_request("https://test.example.com")

        # Verify
        self.assertIsInstance(result, OneSettingsResponse)
        self.assertEqual(result.status_code, 200)  # Default status code
        mock_logger.warning.assert_called_once()

    @patch("azure.monitor.opentelemetry.exporter._configuration._utils.requests.get")
    def test_general_exception_handling(self, mock_get):
        """Test OneSettings request general exception handling."""
        # Setup
        mock_get.side_effect = Exception("Unexpected error")

        # Execute
        with patch("azure.monitor.opentelemetry.exporter._configuration._utils.logger") as mock_logger:
            result = make_onesettings_request("https://test.example.com")

        # Verify
        self.assertIsInstance(result, OneSettingsResponse)
        self.assertEqual(result.status_code, 200)  # Default status code
        mock_logger.warning.assert_called_once()


class TestParseOneSettingsResponse(unittest.TestCase):
    """Test cases for _parse_onesettings_response function."""

    def test_parse_200_response_with_settings(self):
        """Test parsing 200 response with valid settings."""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {
            "ETag": "test-etag-123",
            "x-ms-onesetinterval": "60",  # Onesettings returns interval in minutes
        }

        settings_data = {"settings": {"key1": "value1", _ONE_SETTINGS_CHANGE_VERSION_KEY: "5"}}
        mock_response.content = json.dumps(settings_data).encode("utf-8")

        # Execute
        result = _parse_onesettings_response(mock_response)

        # Verify
        self.assertEqual(result.etag, "test-etag-123")
        self.assertEqual(result.refresh_interval, 3600)
        self.assertEqual(result.settings, settings_data["settings"])
        self.assertEqual(result.version, 5)
        self.assertEqual(result.status_code, 200)

    def test_parse_304_response(self):
        """Test parsing 304 Not Modified response."""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 304
        mock_response.headers = {"ETag": "test-etag-123"}
        mock_response.content = b""

        # Execute
        result = _parse_onesettings_response(mock_response)

        # Verify
        self.assertEqual(result.etag, "test-etag-123")
        self.assertEqual(result.settings, {})
        self.assertIsNone(result.version)
        self.assertEqual(result.status_code, 304)

    def test_parse_error_status_codes(self):
        """Test parsing various error status codes."""
        error_codes = [400, 404, 414, 500]

        for status_code in error_codes:
            with self.subTest(status_code=status_code):
                mock_response = Mock()
                mock_response.status_code = status_code
                mock_response.headers = {}
                mock_response.content = b"Error content"

                with patch("azure.monitor.opentelemetry.exporter._configuration._utils.logger") as mock_logger:
                    result = _parse_onesettings_response(mock_response)

                self.assertIsInstance(result, OneSettingsResponse)
                self.assertEqual(result.settings, {})
                self.assertEqual(result.status_code, status_code)
                mock_logger.warning.assert_called_once()

    def test_parse_invalid_refresh_interval(self):
        """Test parsing response with invalid refresh interval."""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"x-ms-onesetinterval": "invalid-number"}
        mock_response.content = b""

        # Execute
        with patch("azure.monitor.opentelemetry.exporter._configuration._utils.logger") as mock_logger:
            result = _parse_onesettings_response(mock_response)

        # Verify
        self.assertEqual(result.refresh_interval, _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS)
        self.assertEqual(result.status_code, 200)
        mock_logger.warning.assert_called_once()

    def test_parse_invalid_json_content(self):
        """Test parsing response with invalid JSON content."""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.content = b"invalid json content"

        # Execute
        with patch("azure.monitor.opentelemetry.exporter._configuration._utils.logger") as mock_logger:
            result = _parse_onesettings_response(mock_response)

        # Verify
        self.assertEqual(result.settings, {})
        self.assertEqual(result.status_code, 200)
        mock_logger.warning.assert_called_once()

    def test_parse_invalid_version_format(self):
        """Test parsing response with invalid version format."""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}

        settings_data = {"settings": {"key1": "value1", _ONE_SETTINGS_CHANGE_VERSION_KEY: "invalid-version"}}
        mock_response.content = json.dumps(settings_data).encode("utf-8")

        # Execute
        with patch("azure.monitor.opentelemetry.exporter._configuration._utils.logger") as mock_logger:
            result = _parse_onesettings_response(mock_response)

        # Verify
        self.assertEqual(result.settings, settings_data["settings"])
        self.assertIsNone(result.version)
        self.assertEqual(result.status_code, 200)
        mock_logger.warning.assert_called_once()

    def test_parse_unicode_decode_error(self):
        """Test parsing response with unicode decode error."""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.content = b"\x80\x81\x82"  # Invalid UTF-8

        # Execute
        with patch("azure.monitor.opentelemetry.exporter._configuration._utils.logger") as mock_logger:
            result = _parse_onesettings_response(mock_response)

        # Verify
        self.assertEqual(result.settings, {})
        self.assertEqual(result.status_code, 200)
        mock_logger.warning.assert_called_once()

    def test_parse_no_headers(self):
        """Test parsing response with no headers."""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = None
        mock_response.content = b""

        # Execute
        result = _parse_onesettings_response(mock_response)

        # Verify
        self.assertIsNone(result.etag)
        self.assertEqual(result.refresh_interval, _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS)
        self.assertEqual(result.status_code, 200)

    def test_parse_settings_without_version(self):
        """Test parsing response with settings but no version key."""
        # Setup
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}

        settings_data = {"settings": {"key1": "value1", "key2": "value2"}}
        mock_response.content = json.dumps(settings_data).encode("utf-8")

        # Execute
        result = _parse_onesettings_response(mock_response)

        # Verify
        self.assertEqual(result.settings, settings_data["settings"])
        self.assertIsNone(result.version)
        self.assertEqual(result.status_code, 200)


if __name__ == "__main__":
    unittest.main()
