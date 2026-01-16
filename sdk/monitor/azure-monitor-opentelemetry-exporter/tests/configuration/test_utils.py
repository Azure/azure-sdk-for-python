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
    _compare_versions,
    _parse_version_with_beta,
)
from azure.monitor.opentelemetry.exporter._constants import (
    _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS,
    _ONE_SETTINGS_CHANGE_VERSION_KEY,
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

    def test_fill_empty_profile(self):
        """Test filling an empty profile with all parameters."""
        _ConfigurationProfile.fill(
            os="w",
            rp="f",
            attach="m",
            version="1.0.0",
            component="ext",
            region="westus",
        )

        self.assertEqual(_ConfigurationProfile.os, "w")
        self.assertEqual(_ConfigurationProfile.rp, "f")
        self.assertEqual(_ConfigurationProfile.attach, "m")
        self.assertEqual(_ConfigurationProfile.version, "1.0.0")
        self.assertEqual(_ConfigurationProfile.component, "ext")
        self.assertEqual(_ConfigurationProfile.region, "westus")

    def test_fill_partial_profile(self):
        """Test filling profile with only some parameters."""
        _ConfigurationProfile.fill(os="l", version="2.0.0")

        self.assertEqual(_ConfigurationProfile.os, "l")
        self.assertEqual(_ConfigurationProfile.version, "2.0.0")
        self.assertEqual(_ConfigurationProfile.rp, "")
        self.assertEqual(_ConfigurationProfile.attach, "")
        self.assertEqual(_ConfigurationProfile.component, "")
        self.assertEqual(_ConfigurationProfile.region, "")

    def test_fill_no_overwrite(self):
        """Test that fill doesn't overwrite existing values."""
        # Set initial values
        _ConfigurationProfile.os = "w"
        _ConfigurationProfile.version = "1.0.0"

        # Try to overwrite - should be ignored
        _ConfigurationProfile.fill(os="l", version="2.0.0", rp="f")

        # Original values should be preserved
        self.assertEqual(_ConfigurationProfile.os, "w")
        self.assertEqual(_ConfigurationProfile.version, "1.0.0")
        # New value should be set
        self.assertEqual(_ConfigurationProfile.rp, "f")


class TestOneSettingsResponse(unittest.TestCase):
    """Test cases for OneSettingsResponse class."""

    def test_default_initialization(self):
        """Test OneSettingsResponse with default values."""
        response = OneSettingsResponse()

        self.assertIsNone(response.etag)
        self.assertEqual(
            response.refresh_interval, _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS
        )
        self.assertEqual(response.settings, {})
        self.assertIsNone(response.version)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.has_exception)

    def test_custom_initialization(self):
        """Test OneSettingsResponse with custom values."""
        settings = {"key": "value"}
        response = OneSettingsResponse(
            etag="test-etag",
            refresh_interval=3600,
            settings=settings,
            version=5,
            status_code=304,
        )

        self.assertEqual(response.etag, "test-etag")
        self.assertEqual(response.refresh_interval, 3600)
        self.assertEqual(response.settings, settings)
        self.assertEqual(response.version, 5)
        self.assertEqual(response.status_code, 304)
        self.assertFalse(response.has_exception)

    def test_exception_initialization(self):
        """Test OneSettingsResponse with exception indicator."""
        response = OneSettingsResponse(has_exception=True, status_code=500)

        self.assertIsNone(response.etag)
        self.assertEqual(
            response.refresh_interval, _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS
        )
        self.assertEqual(response.settings, {})
        self.assertIsNone(response.version)
        self.assertEqual(response.status_code, 500)
        self.assertTrue(response.has_exception)

    def test_timeout_initialization(self):
        """Test OneSettingsResponse with timeout indicator."""
        response = OneSettingsResponse(has_exception=True)

        self.assertIsNone(response.etag)
        self.assertEqual(
            response.refresh_interval, _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS
        )
        self.assertEqual(response.settings, {})
        self.assertIsNone(response.version)
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
        mock_response.content = json.dumps(
            {"settings": {"key": "value", _ONE_SETTINGS_CHANGE_VERSION_KEY: "5"}}
        ).encode("utf-8")
        mock_get.return_value = mock_response

        # Make request
        result = make_onesettings_request(
            "http://test.com", {"param": "value"}, {"header": "value"}
        )

        # Verify request was made correctly
        mock_get.assert_called_once_with(
            "http://test.com",
            params={"param": "value"},
            headers={"header": "value"},
            timeout=10,
        )

        # Verify response
        self.assertEqual(result.etag, "test-etag")
        self.assertEqual(result.refresh_interval, 1800)  # 30 minutes * 60
        self.assertEqual(
            result.settings, {"key": "value", _ONE_SETTINGS_CHANGE_VERSION_KEY: "5"}
        )
        self.assertEqual(result.version, 5)
        self.assertEqual(result.status_code, 200)
        self.assertFalse(result.has_exception)

    @patch("azure.monitor.opentelemetry.exporter._configuration._utils.requests.get")
    def test_request_timeout_exception(self, mock_get):
        """Test OneSettings request with timeout exception."""
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

        result = make_onesettings_request("http://test.com")

        # Should return response with timeout and exception indicators
        self.assertIsNone(result.etag)
        self.assertEqual(
            result.refresh_interval, _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS
        )
        self.assertEqual(result.settings, {})
        self.assertIsNone(result.version)
        self.assertEqual(result.status_code, 200)
        self.assertTrue(result.has_exception)

    @patch("azure.monitor.opentelemetry.exporter._configuration._utils.requests.get")
    def test_request_connection_exception(self, mock_get):
        """Test OneSettings request with connection exception."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

        result = make_onesettings_request("http://test.com")

        # Should return response with exception indicator but no timeout
        self.assertIsNone(result.etag)
        self.assertEqual(
            result.refresh_interval, _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS
        )
        self.assertEqual(result.settings, {})
        self.assertIsNone(result.version)
        self.assertEqual(result.status_code, 200)
        self.assertTrue(result.has_exception)

    @patch("azure.monitor.opentelemetry.exporter._configuration._utils.requests.get")
    def test_request_http_exception(self, mock_get):
        """Test OneSettings request with HTTP exception."""
        mock_get.side_effect = requests.exceptions.HTTPError("HTTP 500 Error")

        result = make_onesettings_request("http://test.com")

        # Should return response with exception indicator
        self.assertIsNone(result.etag)
        self.assertEqual(
            result.refresh_interval, _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS
        )
        self.assertEqual(result.settings, {})
        self.assertIsNone(result.version)
        self.assertEqual(result.status_code, 200)
        self.assertTrue(result.has_exception)

    @patch("azure.monitor.opentelemetry.exporter._configuration._utils.requests.get")
    def test_request_generic_exception(self, mock_get):
        """Test OneSettings request with generic exception."""
        mock_get.side_effect = Exception("Unexpected error")

        result = make_onesettings_request("http://test.com")

        # Should return response with exception indicator
        self.assertIsNone(result.etag)
        self.assertEqual(
            result.refresh_interval, _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS
        )
        self.assertEqual(result.settings, {})
        self.assertIsNone(result.version)
        self.assertEqual(result.status_code, 200)
        self.assertTrue(result.has_exception)

    @patch("azure.monitor.opentelemetry.exporter._configuration._utils.requests.get")
    @patch(
        "azure.monitor.opentelemetry.exporter._configuration._utils._parse_onesettings_response"
    )
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

        mock_parse.side_effect = JSONDecodeError(
            "Expecting value", "invalid json content", 0
        )

        result = make_onesettings_request("http://test.com")

        # Should return response with exception indicator
        self.assertIsNone(result.etag)
        self.assertEqual(
            result.refresh_interval, _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS
        )
        self.assertEqual(result.settings, {})
        self.assertIsNone(result.version)
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
                mock_response.raise_for_status.side_effect = (
                    requests.exceptions.HTTPError(f"HTTP {status_code}")
                )
                mock_get.return_value = mock_response

                result = make_onesettings_request("http://test.com")

                # Should return response with exception indicator
                self.assertTrue(result.has_exception)
                self.assertEqual(
                    result.status_code, 200
                )  # Default status when exception occurs

    @patch("azure.monitor.opentelemetry.exporter._configuration._utils.requests.get")
    def test_request_exception_legacy(self, mock_get):
        """Test OneSettings request with network exception (legacy behavior test)."""
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        result = make_onesettings_request("http://test.com")

        # Should return response with exception indicator
        self.assertIsNone(result.etag)
        self.assertEqual(
            result.refresh_interval, _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS
        )
        self.assertEqual(result.settings, {})
        self.assertIsNone(result.version)
        self.assertEqual(result.status_code, 200)
        self.assertTrue(result.has_exception)


class TestParseOneSettingsResponse(unittest.TestCase):
    """Test cases for _parse_onesettings_response function."""

    def test_parse_200_response(self):
        """Test parsing successful 200 response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"ETag": "test-etag", "x-ms-onesetinterval": "45"}
        mock_response.content = json.dumps(
            {"settings": {"feature": "enabled", _ONE_SETTINGS_CHANGE_VERSION_KEY: "10"}}
        ).encode("utf-8")

        result = _parse_onesettings_response(mock_response)

        self.assertEqual(result.etag, "test-etag")
        self.assertEqual(result.refresh_interval, 2700)  # 45 minutes * 60
        self.assertEqual(
            result.settings,
            {"feature": "enabled", _ONE_SETTINGS_CHANGE_VERSION_KEY: "10"},
        )
        self.assertEqual(result.version, 10)
        self.assertEqual(result.status_code, 200)

    def test_parse_304_response(self):
        """Test parsing 304 Not Modified response."""
        mock_response = Mock()
        mock_response.status_code = 304
        mock_response.headers = {"ETag": "cached-etag", "x-ms-onesetinterval": "60"}
        mock_response.content = b""

        result = _parse_onesettings_response(mock_response)

        self.assertEqual(result.etag, "cached-etag")
        self.assertEqual(result.refresh_interval, 3600)  # 60 minutes * 60
        self.assertEqual(result.settings, {})
        self.assertIsNone(result.version)
        self.assertEqual(result.status_code, 304)

    def test_parse_invalid_json(self):
        """Test parsing response with invalid JSON."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.content = b"invalid json"

        result = _parse_onesettings_response(mock_response)

        self.assertIsNone(result.etag)
        self.assertEqual(
            result.refresh_interval, _ONE_SETTINGS_DEFAULT_REFRESH_INTERVAL_SECONDS
        )
        self.assertEqual(result.settings, {})
        self.assertIsNone(result.version)
        self.assertEqual(result.status_code, 200)


class TestEvaluateFeature(unittest.TestCase):
    """Test cases for evaluate_feature function."""

    def setUp(self):
        """Set up test configuration profile."""
        _ConfigurationProfile.os = "w"
        _ConfigurationProfile.rp = "f"
        _ConfigurationProfile.attach = "m"
        _ConfigurationProfile.version = "1.0.0"
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
                "override": [{"os": "w", "component": "ext"}],
            }
        }

        result = evaluate_feature("test_feature", settings)
        self.assertTrue(result)  # Override flips disabled to enabled

    def test_feature_override_no_match(self):
        """Test feature override that doesn't match current profile."""
        settings = {
            "test_feature": {
                "default": "enabled",
                "override": [{"os": "l", "component": "dst"}],
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
                    {"os": "l"},  # Doesn't match
                    {"component": "ext", "rp": "f"},  # Matches
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
        _ConfigurationProfile.os = "w"
        _ConfigurationProfile.version = "1.0.0"
        _ConfigurationProfile.component = "ext"

    def tearDown(self):
        """Reset profile after each test."""
        _ConfigurationProfile.os = ""
        _ConfigurationProfile.version = ""
        _ConfigurationProfile.component = ""

    def test_all_conditions_match(self):
        """Test rule where all conditions match."""
        rule = {"os": "w", "component": "ext"}
        self.assertTrue(_matches_override_rule(rule))

    def test_some_conditions_match(self):
        """Test rule where only some conditions match."""
        rule = {"os": "w", "component": "dst"}  # component doesn't match
        self.assertFalse(_matches_override_rule(rule))

    def test_empty_rule(self):
        """Test empty rule."""
        self.assertFalse(_matches_override_rule({}))
        self.assertFalse(_matches_override_rule(None))


class TestMatchesCondition(unittest.TestCase):
    """Test cases for _matches_condition function."""

    def setUp(self):
        """Set up test configuration profile."""
        _ConfigurationProfile.os = "w"
        _ConfigurationProfile.version = "1.0.0"
        _ConfigurationProfile.component = "ext"
        _ConfigurationProfile.rp = "f"
        _ConfigurationProfile.region = "westus"
        _ConfigurationProfile.attach = "m"

    def tearDown(self):
        """Reset profile after each test."""
        _ConfigurationProfile.os = ""
        _ConfigurationProfile.version = ""
        _ConfigurationProfile.component = ""
        _ConfigurationProfile.rp = ""
        _ConfigurationProfile.region = ""
        _ConfigurationProfile.attach = ""

    def test_os_condition_single_value(self):
        """Test OS condition with single value."""
        self.assertTrue(_matches_condition("os", "w"))
        self.assertFalse(_matches_condition("os", "l"))

    def test_os_condition_list_value(self):
        """Test OS condition with list value."""
        self.assertTrue(_matches_condition("os", ["w", "l"]))
        self.assertFalse(_matches_condition("os", ["l", "d"]))

    def test_version_condition_exact(self):
        """Test version condition with exact match."""
        self.assertTrue(_matches_condition("ver", "1.0.0"))
        self.assertFalse(_matches_condition("ver", "2.0.0"))

    def test_version_condition_range(self):
        """Test version condition with min/max range."""
        # Within range
        self.assertTrue(_matches_condition("ver", {"min": "0.9.0", "max": "1.1.0"}))
        # Below minimum
        self.assertFalse(_matches_condition("ver", {"min": "1.1.0", "max": "2.0.0"}))
        # Above maximum
        self.assertFalse(_matches_condition("ver", {"min": "0.5.0", "max": "0.9.0"}))

    def test_component_condition(self):
        """Test component condition."""
        self.assertTrue(_matches_condition("component", "ext"))
        self.assertFalse(_matches_condition("component", "dst"))

    def test_rp_condition_single_value(self):
        """Test runtime platform condition with single value."""
        self.assertTrue(_matches_condition("rp", "f"))
        self.assertFalse(_matches_condition("rp", "a"))

    def test_rp_condition_list_value(self):
        """Test runtime platform condition with list value."""
        self.assertTrue(_matches_condition("rp", ["f", "a"]))
        self.assertFalse(_matches_condition("rp", ["a", "k"]))

    def test_region_condition(self):
        """Test region condition."""
        self.assertTrue(_matches_condition("region", "westus"))
        self.assertTrue(_matches_condition("region", ["westus", "eastus"]))
        self.assertFalse(_matches_condition("region", "eastus"))
        self.assertFalse(_matches_condition("region", ["eastus", "centralus"]))

    def test_attach_condition(self):
        """Test attach condition."""
        self.assertTrue(_matches_condition("attach", "m"))
        self.assertTrue(_matches_condition("attach", ["m", "i"]))
        self.assertFalse(_matches_condition("attach", "i"))
        self.assertFalse(_matches_condition("attach", ["i"]))

    def test_invalid_condition(self):
        """Test invalid condition key."""
        self.assertFalse(_matches_condition("unknown", "value"))
        self.assertFalse(_matches_condition("", "value"))
        self.assertFalse(_matches_condition("os", None))


class TestCompareVersions(unittest.TestCase):
    """Test cases for _compare_versions function."""

    def test_basic_version_comparison(self):
        """Test basic semantic version comparison."""
        # Greater than
        self.assertTrue(_compare_versions("2.0.0", "1.0.0", ">="))
        self.assertTrue(_compare_versions("1.1.0", "1.0.0", ">"))

        # Less than
        self.assertTrue(_compare_versions("1.0.0", "2.0.0", "<="))
        self.assertTrue(_compare_versions("1.0.0", "1.1.0", "<"))

        # Equal
        self.assertTrue(_compare_versions("1.0.0", "1.0.0", "=="))
        self.assertTrue(_compare_versions("1.0.0", "1.0.0", ">="))
        self.assertTrue(_compare_versions("1.0.0", "1.0.0", "<="))

    def test_beta_version_comparison(self):
        """Test comparison with beta versions."""
        # Beta vs beta
        self.assertTrue(_compare_versions("1.0.0b2", "1.0.0b1", ">"))
        self.assertTrue(_compare_versions("1.0.0b1", "1.0.0b2", "<"))

        # Beta vs release
        self.assertTrue(_compare_versions("1.0.0", "1.0.0b1", ">"))
        self.assertTrue(_compare_versions("1.0.0b1", "1.0.0", "<"))

    def test_invalid_version_fallback(self):
        """Test fallback to string comparison for invalid versions."""
        # Should fall back to string comparison
        self.assertTrue(_compare_versions("invalid", "invalid", "=="))
        self.assertTrue(_compare_versions("z", "a", ">"))


class TestParseVersionWithBeta(unittest.TestCase):
    """Test cases for _parse_version_with_beta function."""

    def test_release_version(self):
        """Test parsing release version."""
        result = _parse_version_with_beta("1.2.3")
        self.assertEqual(result, (1, 2, 3, float("inf")))

    def test_beta_version(self):
        """Test parsing beta version."""
        result = _parse_version_with_beta("1.2.3b10")
        self.assertEqual(result, (1, 2, 3, 10))

    def test_beta_version_no_number(self):
        """Test parsing beta version without number."""
        result = _parse_version_with_beta("1.2.3b")
        self.assertEqual(result, (1, 2, 3, 0))


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

        for has_timeout, has_exception, status_code, description in test_cases:
            with self.subTest(description=description):
                response = OneSettingsResponse(
                    has_exception=has_exception, status_code=status_code
                )
                self.assertEqual(response.has_exception, has_exception)
                self.assertEqual(response.status_code, status_code)


class TestFeatureEvaluationIntegration(unittest.TestCase):
    """Integration tests for complete feature evaluation scenarios."""

    def setUp(self):
        """Set up test configuration profile."""
        _ConfigurationProfile.os = "w"
        _ConfigurationProfile.rp = "f"
        _ConfigurationProfile.attach = "m"
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
            "live_metrics": {
                "default": "disabled",
                "override": [
                    {"os": "w"},  # This should match
                    {"os": "l", "ver": {"min": "1.0.0b20"}},
                    {"component": "dst", "rp": "f"},
                ],
            },
            "sampling": {
                "default": "enabled",
                "override": [
                    {"os": ["w", "l"]},  # This should match and disable
                ],
            },
            "profiling": {
                "default": "disabled",
                "override": [
                    {
                        "os": "w",
                        "ver": {"min": "2.0.0", "max": "3.0.0"},
                    },  # Version doesn't match
                    {
                        "component": "ext",
                        "rp": ["f", "a"],
                        "region": ["westus", "eastus"],
                    },  # All match
                ],
            },
        }

        # live_metrics: disabled by default, but Windows override matches
        self.assertTrue(evaluate_feature("live_metrics", settings))

        # sampling: enabled by default, but OS override matches to disable
        self.assertFalse(evaluate_feature("sampling", settings))

        # profiling: disabled by default, second override matches to enable
        self.assertTrue(evaluate_feature("profiling", settings))


if __name__ == "__main__":
    unittest.main()
