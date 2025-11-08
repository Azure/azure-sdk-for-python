# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import unittest
import time
import datetime
import json
import base64
from unittest.mock import patch, Mock
from typing import Dict, Any

from azure.appconfiguration import FeatureFlagConfigurationSetting
from azure.appconfiguration.provider._azureappconfigurationproviderbase import (
    delay_failure,
    is_json_content_type,
    _build_watched_setting,
    sdk_allowed_kwargs,
    AzureAppConfigurationProviderBase,
)
from azure.appconfiguration.provider._models import SettingSelector
from azure.appconfiguration.provider._constants import (
    NULL_CHAR,
    TELEMETRY_KEY,
    METADATA_KEY,
    ETAG_KEY,
    FEATURE_FLAG_REFERENCE_KEY,
)
from azure.appconfiguration.provider._refresh_timer import _RefreshTimer


class TestDelayFailure(unittest.TestCase):
    """Test the delay_failure function."""

    def test_delay_failure_when_enough_time_passed(self):
        """Test that no delay occurs when enough time has passed."""
        start_time = datetime.datetime.now() - datetime.timedelta(seconds=10)
        with patch("time.sleep") as mock_sleep:
            delay_failure(start_time)
            mock_sleep.assert_not_called()

    def test_delay_failure_when_insufficient_time_passed(self):
        """Test that delay occurs when insufficient time has passed."""
        start_time = datetime.datetime.now() - datetime.timedelta(seconds=2)
        with patch("time.sleep") as mock_sleep:
            delay_failure(start_time)
            mock_sleep.assert_called_once()
            # Verify the delay is approximately correct (around 3 seconds)
            called_delay = mock_sleep.call_args[0][0]
            self.assertGreater(called_delay, 2)
            self.assertLess(called_delay, 4)


class TestIsJsonContentType(unittest.TestCase):
    """Test the is_json_content_type function."""

    def test_valid_json_content_types(self):
        """Test various valid JSON content types."""
        valid_types = [
            "application/json",
            "application/json; charset=utf-8",
            "APPLICATION/JSON",
            "application/vnd.api+json",
            "application/ld+json",
        ]
        for content_type in valid_types:
            with self.subTest(content_type=content_type):
                self.assertTrue(is_json_content_type(content_type))

    def test_invalid_json_content_types(self):
        """Test various invalid JSON content types."""
        invalid_types = [
            "",
            None,
            "text/plain",
            "application/xml",
            "text/json",  # Wrong main type
            "application",  # Malformed
            "application/",  # Malformed
        ]
        for content_type in invalid_types:
            with self.subTest(content_type=content_type):
                self.assertFalse(is_json_content_type(content_type))


class TestBuildWatchedSetting(unittest.TestCase):
    """Test the _build_watched_setting function."""

    def test_string_input(self):
        """Test with string input."""
        result = _build_watched_setting("test_key")
        self.assertEqual(result, ("test_key", NULL_CHAR))

    def test_tuple_input(self):
        """Test with tuple input."""
        result = _build_watched_setting(("test_key", "test_label"))
        self.assertEqual(result, ("test_key", "test_label"))

    def test_wildcard_key_raises_error(self):
        """Test that wildcard in key raises ValueError."""
        with self.assertRaises(ValueError):
            _build_watched_setting("test*key")

    def test_wildcard_label_raises_error(self):
        """Test that wildcard in label raises ValueError."""
        with self.assertRaises(ValueError):
            _build_watched_setting(("test_key", "test*label"))


class TestSdkAllowedKwargs(unittest.TestCase):
    """Test the sdk_allowed_kwargs function."""

    def test_filters_allowed_kwargs(self):
        """Test that only allowed kwargs are returned."""
        kwargs = {
            "headers": {"test": "value"},
            "timeout": 30,
            "invalid_param": "should_be_filtered",
            "user_agent": "test_agent",
            "unknown_param": "filtered_out",
        }
        result = sdk_allowed_kwargs(kwargs)
        expected = {"headers": {"test": "value"}, "timeout": 30, "user_agent": "test_agent"}
        self.assertEqual(result, expected)

    def test_empty_kwargs(self):
        """Test with empty kwargs."""
        result = sdk_allowed_kwargs({})
        self.assertEqual(result, {})


class TestRefreshTimer(unittest.TestCase):
    """Test the _RefreshTimer class."""

    def test_default_initialization(self):
        """Test default initialization."""
        timer = _RefreshTimer()
        self.assertEqual(timer._interval, 30)
        self.assertEqual(timer._attempts, 1)
        self.assertEqual(timer._min_backoff, 30)
        self.assertEqual(timer._max_backoff, 30)

    def test_custom_initialization(self):
        """Test custom initialization."""
        timer = _RefreshTimer(refresh_interval=60, min_backoff=10, max_backoff=300)
        self.assertEqual(timer._interval, 60)
        self.assertEqual(timer._min_backoff, 10)
        # max_backoff is constrained by the interval, so it should be 60, not 300
        self.assertEqual(timer._max_backoff, 60)

    def test_invalid_refresh_interval_raises_error(self):
        """Test that invalid refresh interval raises ValueError."""
        with self.assertRaises(ValueError):
            _RefreshTimer(refresh_interval=0)

    def test_needs_refresh_initially_false(self):
        """Test that needs_refresh is initially false."""
        timer = _RefreshTimer(refresh_interval=1)
        self.assertFalse(timer.needs_refresh())

    def test_needs_refresh_after_interval(self):
        """Test that needs_refresh becomes true after interval."""
        timer = _RefreshTimer(refresh_interval=1)
        # Manually set the next refresh time to the past
        timer._next_refresh_time = time.time() - 1
        self.assertTrue(timer.needs_refresh())

    def test_reset_functionality(self):
        """Test the reset functionality."""
        timer = _RefreshTimer(refresh_interval=1)
        timer._attempts = 5
        timer.reset()
        self.assertEqual(timer._attempts, 1)
        # Next refresh time should be reset to future
        self.assertGreater(timer._next_refresh_time, time.time())

    def test_backoff_increases_attempts(self):
        """Test that backoff increases attempts."""
        timer = _RefreshTimer(refresh_interval=60, min_backoff=1, max_backoff=60)
        initial_attempts = timer._attempts
        timer.backoff()
        self.assertEqual(timer._attempts, initial_attempts + 1)
        self.assertGreater(timer._next_refresh_time, time.time())

    def test_calculate_backoff_progression(self):
        """Test that backoff calculation progresses correctly."""
        timer = _RefreshTimer(refresh_interval=60, min_backoff=1, max_backoff=60)

        # Test multiple backoff calculations to verify exponential progression
        # Since backoff includes randomization, we test the range of possible values
        min_backoff_ms = 1000  # min_backoff in milliseconds
        max_backoff_ms = 60000  # max_backoff in milliseconds

        # For attempts=1, calculated value should be min_backoff * 2^1 = 2000ms
        # Random component can range from min_backoff (1000) to calculated (2000)
        backoff1 = timer._calculate_backoff()
        self.assertGreaterEqual(backoff1, min_backoff_ms)
        self.assertLessEqual(backoff1, 2000)  # min_backoff * 2^1

        timer._attempts += 1
        # For attempts=2, calculated value should be min_backoff * 2^2 = 4000ms
        # Random component can range from min_backoff (1000) to calculated (4000)
        backoff2 = timer._calculate_backoff()
        self.assertGreaterEqual(backoff2, min_backoff_ms)
        self.assertLessEqual(backoff2, 4000)  # min_backoff * 2^2

        # Both should be within overall min/max bounds
        self.assertLessEqual(backoff1, max_backoff_ms)
        self.assertLessEqual(backoff2, max_backoff_ms)


class TestAzureAppConfigurationProviderBase(unittest.TestCase):
    """Test the AzureAppConfigurationProviderBase class."""

    def setUp(self):
        """Set up test environment."""
        self.provider = AzureAppConfigurationProviderBase(endpoint="https://test.azconfig.io")

    def test_initialization_with_defaults(self):
        """Test initialization with default values."""
        provider = AzureAppConfigurationProviderBase()
        self.assertEqual(provider._origin_endpoint, "")
        self.assertEqual(provider._dict, {})
        self.assertIsInstance(provider._selects, list)
        self.assertEqual(len(provider._selects), 1)
        self.assertEqual(provider._trim_prefixes, [])
        self.assertFalse(provider._feature_flag_enabled)

    def test_initialization_with_custom_values(self):
        """Test initialization with custom values."""
        selects = [SettingSelector(key_filter="app:*")]
        trim_prefixes = ["app:", "config:"]
        refresh_on = ["refresh_key"]

        provider = AzureAppConfigurationProviderBase(
            endpoint="https://test.azconfig.io",
            selects=selects,
            trim_prefixes=trim_prefixes,
            refresh_on=refresh_on,
            feature_flag_enabled=True,
            refresh_interval=60,
        )

        self.assertEqual(provider._origin_endpoint, "https://test.azconfig.io")
        self.assertEqual(provider._selects, selects)
        self.assertEqual(provider._trim_prefixes, ["config:", "app:"])  # Should be sorted by length
        self.assertTrue(provider._feature_flag_enabled)
        self.assertEqual(provider._refresh_timer._interval, 60)

    def test_process_key_name_with_no_prefix(self):
        """Test key name processing with no matching prefix."""
        config = Mock()
        config.key = "test_key"

        result = self.provider._process_key_name(config)
        self.assertEqual(result, "test_key")

    def test_process_key_name_with_matching_prefix(self):
        """Test key name processing with matching prefix."""
        provider = AzureAppConfigurationProviderBase(trim_prefixes=["app:", "config:"])
        config = Mock()
        config.key = "app:test_key"

        result = provider._process_key_name(config)
        self.assertEqual(result, "test_key")

    def test_process_key_name_with_longest_matching_prefix(self):
        """Test key name processing uses longest matching prefix."""
        provider = AzureAppConfigurationProviderBase(trim_prefixes=["app:", "app:config:"])
        config = Mock()
        config.key = "app:config:test_key"

        result = provider._process_key_name(config)
        self.assertEqual(result, "test_key")

    def test_mapping_interface_empty(self):
        """Test mapping interface with empty provider."""
        self.assertEqual(len(self.provider), 0)
        self.assertNotIn("test_key", self.provider)
        self.assertEqual(list(self.provider.keys()), [])
        self.assertEqual(list(self.provider.values()), [])
        self.assertEqual(list(self.provider.items()), [])

    def test_mapping_interface_with_data(self):
        """Test mapping interface with data."""
        # Manually add data to test mapping interface
        with self.provider._update_lock:
            self.provider._dict = {"key1": "value1", "key2": {"nested": "value"}}

        self.assertEqual(len(self.provider), 2)
        self.assertIn("key1", self.provider)
        self.assertNotIn("key3", self.provider)
        self.assertEqual(self.provider["key1"], "value1")
        self.assertEqual(self.provider.get("key1"), "value1")
        self.assertEqual(self.provider.get("key3", "default"), "default")

        keys = list(self.provider.keys())
        self.assertIn("key1", keys)
        self.assertIn("key2", keys)

        values = list(self.provider.values())
        self.assertIn("value1", values)
        self.assertIn({"nested": "value"}, values)

    def test_process_key_value_base_plain_text(self):
        """Test processing non-keyvault plain text value."""
        config = Mock()
        config.content_type = "text/plain"
        config.value = "plain text value"

        result = self.provider._process_key_value_base(config)
        self.assertEqual(result, "plain text value")

    def test_process_key_value_base_json(self):
        """Test processing non-keyvault JSON value."""
        config = Mock()
        config.content_type = "application/json"
        config.value = '{"key": "value", "number": 42}'

        result = self.provider._process_key_value_base(config)
        expected = {"key": "value", "number": 42}
        self.assertEqual(result, expected)

    def test_process_key_value_base_invalid_json(self):
        """Test processing non-keyvault invalid JSON value."""
        config = Mock()
        config.content_type = "application/json"
        config.value = '{"invalid": json}'

        # Mock the remove_json_comments import to avoid dependency issues
        with patch("azure.appconfiguration.provider._azureappconfigurationproviderbase.json.loads") as mock_json_loads:
            mock_json_loads.side_effect = [
                json.JSONDecodeError("test", "test", 0),
                json.JSONDecodeError("test", "test", 0),
            ]
            result = self.provider._process_key_value_base(config)
            self.assertEqual(result, '{"invalid": json}')  # Should return as string

    def test_update_ff_telemetry_metadata(self):
        """Test feature flag telemetry processing."""
        feature_flag = Mock(spec=FeatureFlagConfigurationSetting)
        feature_flag.etag = "test_etag"
        feature_flag.key = "test_feature"
        feature_flag.label = "test_label"

        feature_flag_value: Dict[str, Any] = {TELEMETRY_KEY: {"enabled": True}}

        endpoint = "https://test.azconfig.io"

        self.provider._update_ff_telemetry_metadata(endpoint, feature_flag, feature_flag_value)

        # Verify telemetry structure was created
        self.assertIn(TELEMETRY_KEY, feature_flag_value)
        self.assertIn(METADATA_KEY, feature_flag_value[TELEMETRY_KEY])

        metadata = feature_flag_value[TELEMETRY_KEY][METADATA_KEY]
        self.assertEqual(metadata[ETAG_KEY], "test_etag")
        self.assertIn(FEATURE_FLAG_REFERENCE_KEY, metadata)
        self.assertIn("test_feature", metadata[FEATURE_FLAG_REFERENCE_KEY])

    def test_update_ff_telemetry_metadata_max_variants(self):
        """Test that max_variants only increases, never decreases."""
        feature_flag = Mock(spec=FeatureFlagConfigurationSetting)
        feature_flag.etag = "test_etag"

        self.assertIsNone(self.provider._tracing_context.max_variants)

        feature_flag_value: Dict[str, Any] = {}

        self.provider._update_ff_telemetry_metadata("", feature_flag, feature_flag_value)

        # Verify max_variants remains None
        self.assertIsNone(self.provider._tracing_context.max_variants)

        # First call with 3 variants
        feature_flag_value_3: Dict[str, Any] = {"variants": [{}, {}, {}]}  # 3 variants

        self.provider._update_ff_telemetry_metadata("", feature_flag, feature_flag_value_3)
        self.assertEqual(self.provider._tracing_context.max_variants, 3)

        # Second call with 1 variant (should not decrease)
        feature_flag_value_1: Dict[str, Any] = {"variants": [{}]}  # 1 variant

        self.provider._update_ff_telemetry_metadata("", feature_flag, feature_flag_value_1)
        self.assertEqual(self.provider._tracing_context.max_variants, 3)  # Should remain 3

        # Third call with 5 variants (should increase)
        feature_flag_value_5: Dict[str, Any] = {"variants": [{}, {}, {}, {}, {}]}  # 5 variants

        self.provider._update_ff_telemetry_metadata("", feature_flag, feature_flag_value_5)
        self.assertEqual(self.provider._tracing_context.max_variants, 5)  # Should increase to 5

    def test_generate_allocation_id_no_allocation(self):
        """Test allocation ID generation with no allocation."""
        feature_flag_value: Dict[str, Any] = {"no_allocation": "here"}
        result = AzureAppConfigurationProviderBase._generate_allocation_id(feature_flag_value)
        self.assertIsNone(result)

    def test_generate_allocation_id_with_allocation(self):
        """Test allocation ID generation with allocation."""
        feature_flag_value: Dict[str, Any] = {
            "allocation": {
                "seed": "test_seed",
                "default_when_enabled": "Control",
                "percentile": [{"from": 0, "to": 50, "variant": "Control"}, {"from": 50, "to": 100, "variant": "Test"}],
            },
            "variants": [
                {"name": "Control", "configuration_value": {"key": "control_value"}},
                {"name": "Test", "configuration_value": {"key": "test_value"}},
            ],
        }

        result = AzureAppConfigurationProviderBase._generate_allocation_id(feature_flag_value)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        # Should be a base64 encoded string
        if result is not None:
            try:
                base64.urlsafe_b64decode(result.encode() + b"==")  # Add padding if needed
            except Exception:
                self.fail("Result should be valid base64")

    def test_generate_allocation_id_no_variants_no_seed(self):
        """Test allocation ID generation with no variants and no seed."""
        feature_flag_value: Dict[str, Any] = {
            "allocation": {
                # Only having default_when_enabled means allocated_variants won't be empty
                # So this should actually return an allocation ID, not None
                "default_when_enabled": "Control"
            }
        }
        result = AzureAppConfigurationProviderBase._generate_allocation_id(feature_flag_value)
        # Since default_when_enabled is provided, allocated_variants won't be empty
        # so this should return a valid allocation ID
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)

    def test_generate_allocation_id_truly_empty(self):
        """Test allocation ID generation with truly empty allocation."""
        feature_flag_value: Dict[str, Any] = {
            "allocation": {
                # No seed and no default_when_enabled
            }
        }
        result = AzureAppConfigurationProviderBase._generate_allocation_id(feature_flag_value)
        # This should return None because allocated_variants is empty and no seed
        self.assertIsNone(result)
