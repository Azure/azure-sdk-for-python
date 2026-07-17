# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import json
import unittest
from unittest.mock import Mock, patch
import requests

from azure.monitor.opentelemetry.exporter._configuration._utils import (
    _ConfigurationProfile,
    OneSettingsResponse,
    make_onesettings_request,
    _parse_onesettings_response,
    evaluate_feature,
    _matches_override_rule,
    _matches_condition,
)
from azure.monitor.opentelemetry.exporter._constants import (
    _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS,
)


class TestConfigurationProfile(unittest.TestCase):
    """Test cases for _ConfigurationProfile class."""

    def setUp(self):
        """Reset profile before each test."""
        _ConfigurationProfile.os = ""
        _ConfigurationProfile.rp = ""
        _ConfigurationProfile.attach = ""
        _ConfigurationProfile.version = ""
        _ConfigurationProfile.component = ""
        _ConfigurationProfile.region = ""
        _ConfigurationProfile.ikey = ""

    def test_fill_empty_profile(self):
        """Test filling an empty profile with all parameters."""
        _ConfigurationProfile.fill(
            os="windows",
            rp="fn",
            attach="manual",
            version="1.0.0",
            component="ext",
            region="westus",
            ikey="12345678-1234-1234-1234-123456789abc",
        )

        self.assertEqual(_ConfigurationProfile.os, "windows")
        self.assertEqual(_ConfigurationProfile.rp, "fn")
        self.assertEqual(_ConfigurationProfile.attach, "manual")
        self.assertEqual(_ConfigurationProfile.version, "1.0.0")
        self.assertEqual(_ConfigurationProfile.component, "ext")
        self.assertEqual(_ConfigurationProfile.region, "westus")
        self.assertEqual(_ConfigurationProfile.ikey, "12345678-1234-1234-1234-123456789abc")

    def test_fill_partial_profile(self):
        """Test filling profile with only some parameters."""
        _ConfigurationProfile.fill(os="linux", version="2.0.0")

        self.assertEqual(_ConfigurationProfile.os, "linux")
        self.assertEqual(_ConfigurationProfile.version, "2.0.0")
        self.assertEqual(_ConfigurationProfile.rp, "")
        self.assertEqual(_ConfigurationProfile.attach, "")
        self.assertEqual(_ConfigurationProfile.component, "")
        self.assertEqual(_ConfigurationProfile.region, "")

    def test_fill_no_overwrite(self):
        """Test that fill doesn't overwrite existing values."""
        # Set initial values
        _ConfigurationProfile.os = "windows"
        _ConfigurationProfile.version = "1.0.0"

        # Try to overwrite - should be ignored
        _ConfigurationProfile.fill(os="linux", version="2.0.0", rp="fn")

        # Original values should be preserved
        self.assertEqual(_ConfigurationProfile.os, "windows")
        self.assertEqual(_ConfigurationProfile.version, "1.0.0")
        # New value should be set
        self.assertEqual(_ConfigurationProfile.rp, "fn")


class TestOneSettingsResponse(unittest.TestCase):
    """Test cases for OneSettingsResponse class."""

    def test_default_initialization(self):
        """Test OneSettingsResponse with default values."""
        response = OneSettingsResponse()

        self.assertIsNone(response.etag)
        self.assertEqual(response.refresh_interval_s, _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS)
        self.assertEqual(response.settings, {})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.has_exception)

    def test_custom_initialization(self):
        """Test OneSettingsResponse with custom values."""
        settings = {"key": "value"}
        response = OneSettingsResponse(etag="test-etag", refresh_interval_s=3600, settings=settings, status_code=304)

        self.assertEqual(response.etag, "test-etag")
        self.assertEqual(response.refresh_interval_s, 3600)
        self.assertEqual(response.settings, settings)
        self.assertEqual(response.status_code, 304)
        self.assertFalse(response.has_exception)

    def test_exception_initialization(self):
        """Test OneSettingsResponse with exception indicator."""
        response = OneSettingsResponse(has_exception=True, status_code=500)

        self.assertIsNone(response.etag)
        self.assertEqual(response.refresh_interval_s, _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS)
        self.assertEqual(response.settings, {})
        self.assertEqual(response.status_code, 500)
        self.assertTrue(response.has_exception)

    def test_timeout_initialization(self):
        """Test OneSettingsResponse with timeout indicator."""
        response = OneSettingsResponse(has_exception=True)

        self.assertIsNone(response.etag)
        self.assertEqual(response.refresh_interval_s, _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS)
        self.assertEqual(response.settings, {})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.has_exception)

    def test_all_error_indicators(self):
        """Test OneSettingsResponse with all error indicators set."""
        response = OneSettingsResponse(
            status_code=408,
            has_exception=True,
        )

        self.assertEqual(response.status_code, 408)
        self.assertTrue(response.has_exception)


class TestMakeOneSettingsRequest(unittest.TestCase):
    """Test cases for make_onesettings_request function."""

    @patch("azure.monitor.opentelemetry.exporter._configuration._utils.requests.get")
    def test_successful_request(self, mock_get):
        """Test successful OneSettings request."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"ETag": "test-etag", "x-ms-onesetinterval": "30"}
        mock_response.content = json.dumps({"settings": {"key": "value", "FEATURE_X": "enabled"}}).encode("utf-8")
        mock_get.return_value = mock_response

        # Make request
        result = make_onesettings_request("http://test.com", {"param": "value"}, {"header": "value"})

        # Verify request was made correctly
        mock_get.assert_called_once_with(
            "http://test.com",
            params={"param": "value"},
            headers={"header": "value"},
            timeout=10,
        )

        # Verify response
        self.assertEqual(result.etag, "test-etag")
        self.assertEqual(result.refresh_interval_s, 1800)  # 30 minutes * 60
        self.assertEqual(result.settings, {"key": "value", "FEATURE_X": "enabled"})
        self.assertEqual(result.status_code, 200)
        self.assertFalse(result.has_exception)

    @patch("azure.monitor.opentelemetry.exporter._configuration._utils.requests.get")
    def test_request_timeout_exception(self, mock_get):
        """Test OneSettings request with timeout exception."""
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

        result = make_onesettings_request("http://test.com")

        # Should return response with timeout and exception indicators
        self.assertIsNone(result.etag)
        self.assertEqual(result.refresh_interval_s, _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS)
        self.assertEqual(result.settings, {})
        self.assertEqual(result.status_code, 200)
        self.assertTrue(result.has_exception)

    @patch("azure.monitor.opentelemetry.exporter._configuration._utils.requests.get")
    def test_request_connection_exception(self, mock_get):
        """Test OneSettings request with connection exception."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

        result = make_onesettings_request("http://test.com")

        # Should return response with exception indicator but no timeout
        self.assertIsNone(result.etag)
        self.assertEqual(result.refresh_interval_s, _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS)
        self.assertEqual(result.settings, {})
        self.assertEqual(result.status_code, 200)
        self.assertTrue(result.has_exception)

    @patch("azure.monitor.opentelemetry.exporter._configuration._utils.requests.get")
    def test_request_http_exception(self, mock_get):
        """Test OneSettings request with HTTP exception."""
        mock_get.side_effect = requests.exceptions.HTTPError("HTTP 500 Error")

        result = make_onesettings_request("http://test.com")

        # Should return response with exception indicator
        self.assertIsNone(result.etag)
        self.assertEqual(result.refresh_interval_s, _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS)
        self.assertEqual(result.settings, {})
        self.assertEqual(result.status_code, 200)
        self.assertTrue(result.has_exception)

    @patch("azure.monitor.opentelemetry.exporter._configuration._utils.requests.get")
    def test_request_generic_exception(self, mock_get):
        """Test OneSettings request with generic exception."""
        mock_get.side_effect = Exception("Unexpected error")

        result = make_onesettings_request("http://test.com")

        # Should return response with exception indicator
        self.assertIsNone(result.etag)
        self.assertEqual(result.refresh_interval_s, _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS)
        self.assertEqual(result.settings, {})
        self.assertEqual(result.status_code, 200)
        self.assertTrue(result.has_exception)

    @patch("azure.monitor.opentelemetry.exporter._configuration._utils.requests.get")
    @patch("azure.monitor.opentelemetry.exporter._configuration._utils._parse_onesettings_response")
    def test_json_decode_exception(self, mock_parse, mock_get):
        """Test OneSettings request with JSON decode exception."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"ETag": "test-etag"}
        mock_response.content = b"invalid json content"
        mock_get.return_value = mock_response

        # Mock _parse_onesettings_response to raise JSONDecodeError
        from json import JSONDecodeError

        mock_parse.side_effect = JSONDecodeError("Expecting value", "invalid json content", 0)

        result = make_onesettings_request("http://test.com")

        # Should return response with exception indicator
        self.assertIsNone(result.etag)
        self.assertEqual(result.refresh_interval_s, _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS)
        self.assertEqual(result.settings, {})
        self.assertEqual(result.status_code, 200)
        self.assertTrue(result.has_exception)

    @patch("azure.monitor.opentelemetry.exporter._configuration._utils.requests.get")
    def test_http_error_status_codes(self, mock_get):
        """Test OneSettings request with various HTTP error status codes."""
        # Test different HTTP error codes
        error_codes = [400, 401, 403, 404, 429, 500, 502, 503, 504]

        for status_code in error_codes:
            with self.subTest(status_code=status_code):
                mock_response = Mock()
                mock_response.status_code = status_code
                mock_response.headers = {}
                mock_response.content = b""
                mock_get.return_value = mock_response

                result = make_onesettings_request("http://test.com")

                # HTTP errors are NOT surfaced as transient exceptions here; the real status code is
                # preserved so callers can classify retryable vs non-retryable. has_exception is
                # reserved for genuine network/timeout failures.
                self.assertFalse(result.has_exception)
                self.assertEqual(result.status_code, status_code)
                self.assertIsNone(result.etag)
                self.assertEqual(result.settings, {})

    @patch("azure.monitor.opentelemetry.exporter._configuration._utils.requests.get")
    def test_request_exception_legacy(self, mock_get):
        """Test OneSettings request with network exception (legacy behavior test)."""
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        result = make_onesettings_request("http://test.com")

        # Should return response with exception indicator
        self.assertIsNone(result.etag)
        self.assertEqual(result.refresh_interval_s, _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS)
        self.assertEqual(result.settings, {})
        self.assertEqual(result.status_code, 200)
        self.assertTrue(result.has_exception)


class TestParseOneSettingsResponse(unittest.TestCase):
    """Test cases for _parse_onesettings_response function."""

    def test_parse_200_response(self):
        """Test parsing successful 200 response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"ETag": "test-etag", "x-ms-onesetinterval": "45"}
        mock_response.content = json.dumps({"settings": {"feature": "enabled", "CHANGE_VERSION": "10"}}).encode("utf-8")

        result = _parse_onesettings_response(mock_response)

        self.assertEqual(result.etag, "test-etag")
        self.assertEqual(result.refresh_interval_s, 2700)  # 45 minutes * 60
        self.assertEqual(result.settings, {"feature": "enabled", "CHANGE_VERSION": "10"})
        self.assertEqual(result.status_code, 200)

    def test_parse_304_response(self):
        """Test parsing 304 Not Modified response."""
        mock_response = Mock()
        mock_response.status_code = 304
        mock_response.headers = {"ETag": "cached-etag", "x-ms-onesetinterval": "60"}
        mock_response.content = b""

        result = _parse_onesettings_response(mock_response)

        self.assertEqual(result.etag, "cached-etag")
        self.assertEqual(result.refresh_interval_s, 3600)  # 60 minutes * 60
        self.assertEqual(result.settings, {})
        self.assertEqual(result.status_code, 304)

    def test_parse_invalid_json(self):
        """Test parsing response with invalid JSON."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.content = b"invalid json"

        result = _parse_onesettings_response(mock_response)

        self.assertIsNone(result.etag)
        self.assertEqual(result.refresh_interval_s, _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS)
        self.assertEqual(result.settings, {})
        self.assertEqual(result.status_code, 200)


class TestEvaluateFeature(unittest.TestCase):
    """Test cases for evaluate_feature function."""

    def setUp(self):
        """Set up test configuration profile."""
        _ConfigurationProfile.os = "windows"
        _ConfigurationProfile.rp = "fn"
        _ConfigurationProfile.attach = "manual"
        _ConfigurationProfile.version = "1.0.0"
        _ConfigurationProfile.component = "ext"
        _ConfigurationProfile.region = "westus"
        _ConfigurationProfile.ikey = "12345678-1234-1234-1234-123456789abc"

    def tearDown(self):
        """Reset profile after each test."""
        _ConfigurationProfile.os = ""
        _ConfigurationProfile.rp = ""
        _ConfigurationProfile.attach = ""
        _ConfigurationProfile.version = ""
        _ConfigurationProfile.component = ""
        _ConfigurationProfile.region = ""
        _ConfigurationProfile.ikey = ""

    def test_feature_enabled_by_default(self):
        """Test feature that is enabled by default with no overrides."""
        settings = {"test_feature": {"default": "enabled"}}

        result = evaluate_feature("test_feature", settings)
        self.assertTrue(result)

    def test_feature_disabled_by_default(self):
        """Test feature that is disabled by default with no overrides."""
        settings = {"test_feature": {"default": "disabled"}}

        result = evaluate_feature("test_feature", settings)
        self.assertFalse(result)

    def test_feature_override_matches(self):
        """Test feature override that matches current profile."""
        settings = {
            "test_feature": {
                "default": "disabled",
                "override": [{"os": "windows", "component": "ext"}],
            }
        }

        result = evaluate_feature("test_feature", settings)
        self.assertTrue(result)  # Override flips disabled to enabled

    def test_feature_override_no_match(self):
        """Test feature override that doesn't match current profile."""
        settings = {
            "test_feature": {
                "default": "enabled",
                "override": [{"os": "linux", "component": "dst"}],
            }
        }

        result = evaluate_feature("test_feature", settings)
        self.assertTrue(result)  # No override, stays default

    def test_feature_multiple_overrides(self):
        """Test feature with multiple override rules."""
        settings = {
            "test_feature": {
                "default": "disabled",
                "override": [
                    {"os": "linux"},  # Doesn't match
                    {"component": "ext", "rp": "fn"},  # Matches
                    {"region": "eastus"},  # Doesn't match
                ],
            }
        }

        result = evaluate_feature("test_feature", settings)
        self.assertTrue(result)  # Second override matches

    def test_invalid_inputs(self):
        """Test evaluate_feature with invalid inputs."""
        # Empty feature key
        self.assertIsNone(evaluate_feature("", {}))

        # None settings
        self.assertIsNone(evaluate_feature("test", None))

        # Feature not in settings
        self.assertIsNone(evaluate_feature("missing", {}))

        # Invalid feature config
        self.assertIsNone(evaluate_feature("test", {"test": "invalid"}))


class TestMatchesOverrideRule(unittest.TestCase):
    """Test cases for _matches_override_rule function."""

    def setUp(self):
        """Set up test configuration profile."""
        _ConfigurationProfile.os = "windows"
        _ConfigurationProfile.version = "1.0.0"
        _ConfigurationProfile.component = "ext"

    def tearDown(self):
        """Reset profile after each test."""
        _ConfigurationProfile.os = ""
        _ConfigurationProfile.version = ""
        _ConfigurationProfile.component = ""

    def test_all_conditions_match(self):
        """Test rule where all conditions match."""
        rule = {"os": "windows", "component": "ext"}
        self.assertTrue(_matches_override_rule(rule))

    def test_some_conditions_match(self):
        """Test rule where only some conditions match."""
        rule = {"os": "windows", "component": "dst"}  # component doesn't match
        self.assertFalse(_matches_override_rule(rule))

    def test_ver_without_component_does_not_match(self):
        """Test that a ver condition without a component condition never matches."""
        # ver matches the profile, but component is absent -> rule is ignored
        rule = {"ver": "1.0.0"}
        self.assertFalse(_matches_override_rule(rule))
        # ver combined with a non-component field is still ignored
        rule = {"os": "windows", "ver": "1.0.0"}
        self.assertFalse(_matches_override_rule(rule))

    def test_ver_with_matching_component_matches(self):
        """Test that ver is honored when component is present and matches."""
        rule = {"ver": "1.0.0", "component": "ext"}
        self.assertTrue(_matches_override_rule(rule))

    def test_ver_with_non_matching_component_does_not_match(self):
        """Test that ver + component fails when the component does not match the profile."""
        rule = {"ver": "1.0.0", "component": "dst"}  # component doesn't match profile ("ext")
        self.assertFalse(_matches_override_rule(rule))

    def test_empty_rule(self):
        """Test empty rule."""
        self.assertFalse(_matches_override_rule({}))
        self.assertFalse(_matches_override_rule(None))


class TestMatchesCondition(unittest.TestCase):
    """Test cases for _matches_condition function."""

    def setUp(self):
        """Set up test configuration profile."""
        _ConfigurationProfile.os = "windows"
        _ConfigurationProfile.version = "1.0.0"
        _ConfigurationProfile.component = "ext"
        _ConfigurationProfile.rp = "fn"
        _ConfigurationProfile.region = "westus"
        _ConfigurationProfile.attach = "manual"
        _ConfigurationProfile.ikey = "12345678-1234-1234-1234-123456789abc"

    def tearDown(self):
        """Reset profile after each test."""
        _ConfigurationProfile.os = ""
        _ConfigurationProfile.version = ""
        _ConfigurationProfile.component = ""
        _ConfigurationProfile.rp = ""
        _ConfigurationProfile.region = ""
        _ConfigurationProfile.attach = ""
        _ConfigurationProfile.ikey = ""

    def test_os_condition(self):
        """Test OS condition with exact match."""
        self.assertTrue(_matches_condition("os", "windows"))
        self.assertFalse(_matches_condition("os", "linux"))

    def test_version_condition_exact(self):
        """Test version condition with exact match."""
        self.assertTrue(_matches_condition("ver", "1.0.0"))
        self.assertFalse(_matches_condition("ver", "2.0.0"))

    def test_component_condition(self):
        """Test component condition."""
        self.assertTrue(_matches_condition("component", "ext"))
        self.assertFalse(_matches_condition("component", "dst"))

    def test_rp_condition(self):
        """Test resource provider condition with exact match."""
        self.assertTrue(_matches_condition("rp", "fn"))
        self.assertFalse(_matches_condition("rp", "appsvc"))  # cspell:ignore appsvc

    def test_region_condition(self):
        """Test region condition."""
        self.assertTrue(_matches_condition("region", "westus"))
        self.assertFalse(_matches_condition("region", "eastus"))

    def test_attach_condition(self):
        """Test attach condition."""
        self.assertTrue(_matches_condition("attach", "manual"))
        self.assertFalse(_matches_condition("attach", "integratedauto"))

    def test_ikey_condition(self):
        """Test instrumentation key condition (case-insensitive exact match)."""
        self.assertTrue(_matches_condition("ikey", "12345678-1234-1234-1234-123456789abc"))
        # Case-insensitive match
        self.assertTrue(_matches_condition("ikey", "12345678-1234-1234-1234-123456789ABC"))
        self.assertFalse(_matches_condition("ikey", "00000000-0000-0000-0000-000000000000"))

    def test_invalid_condition(self):
        """Test invalid condition key."""
        self.assertFalse(_matches_condition("unknown", "value"))
        self.assertFalse(_matches_condition("", "value"))
        self.assertFalse(_matches_condition("os", None))


class TestOneSettingsResponseErrorHandling(unittest.TestCase):
    """Test cases specifically for OneSettingsResponse error handling scenarios."""

    def test_response_with_timeout_only(self):
        """Test response that indicates timeout but not general exception."""
        # This scenario shouldn't normally happen but test for completeness
        response = OneSettingsResponse(has_exception=False, status_code=408)

        self.assertFalse(response.has_exception)
        self.assertEqual(response.status_code, 408)

    def test_response_error_combinations(self):
        """Test various combinations of error indicators."""
        test_cases = [
            # (has_timeout, has_exception, status_code, description)
            (True, True, 200, "timeout with exception"),
            (False, True, 500, "exception without timeout"),
            (True, False, 408, "timeout without exception flag"),
            (False, False, 429, "no error flags but error status"),
        ]

        for _has_timeout, has_exception, status_code, description in test_cases:
            with self.subTest(description=description):
                response = OneSettingsResponse(has_exception=has_exception, status_code=status_code)
                self.assertEqual(response.has_exception, has_exception)
                self.assertEqual(response.status_code, status_code)


class TestFeatureEvaluationIntegration(unittest.TestCase):
    """Integration tests for complete feature evaluation scenarios."""

    def setUp(self):
        """Set up test configuration profile."""
        _ConfigurationProfile.os = "windows"
        _ConfigurationProfile.rp = "fn"
        _ConfigurationProfile.attach = "manual"
        _ConfigurationProfile.version = "1.0.0b20"
        _ConfigurationProfile.component = "ext"
        _ConfigurationProfile.region = "westus"

    def tearDown(self):
        """Reset profile after each test."""
        _ConfigurationProfile.os = ""
        _ConfigurationProfile.rp = ""
        _ConfigurationProfile.attach = ""
        _ConfigurationProfile.version = ""
        _ConfigurationProfile.component = ""
        _ConfigurationProfile.region = ""

    def test_complex_feature_evaluation(self):
        """Test complex feature evaluation with multiple conditions."""
        settings = {
            "FEATURE_LIVE_METRICS": {
                "default": "disabled",
                "override": [
                    {"os": "windows"},  # This should match
                    {"os": "linux", "ver": "1.0.0b20", "component": "dst"},
                    {"component": "dst", "rp": "fn"},
                ],
            },
            "FEATURE_SDK_STATS": {
                "default": "enabled",
                "override": [
                    {"os": "windows"},  # This should match and disable
                ],
            },
            "FEATURE_PROFILING": {
                "default": "disabled",
                "override": [
                    {
                        "os": "windows",
                        "ver": "2.0.0",
                        "component": "ext",
                    },  # Version doesn't match
                    {
                        "component": "ext",
                        "rp": "fn",
                        "region": "westus",
                    },  # All match
                ],
            },
        }

        # FEATURE_LIVE_METRICS: disabled by default, but Windows override matches
        self.assertTrue(evaluate_feature("FEATURE_LIVE_METRICS", settings))

        # FEATURE_SDK_STATS: enabled by default, but OS override matches to disable
        self.assertFalse(evaluate_feature("FEATURE_SDK_STATS", settings))

        # FEATURE_PROFILING: disabled by default, second override matches to enable
        self.assertTrue(evaluate_feature("FEATURE_PROFILING", settings))


if __name__ == "__main__":
    unittest.main()
