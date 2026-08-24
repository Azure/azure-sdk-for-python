# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import unittest
import time
import json
import base64
from unittest.mock import patch, Mock
from typing import Dict, Any

from azure.appconfiguration import FeatureFlagConfigurationSetting
from azure.appconfiguration import (
    FeatureFlag,
    FeatureFlagAllocation,
    FeatureFlagConditions,
    FeatureFilter,
    FeatureFlagTelemetryConfiguration,
    FeatureFlagVariantDefinition,
    GroupAllocation,
    PercentileAllocation,
    UserAllocation,
)
from azure.appconfiguration.provider._azureappconfigurationproviderbase import (
    is_json_content_type,
    _build_watched_setting,
    AzureAppConfigurationProviderBase,
)
from azure.appconfiguration.provider._models import SettingSelector, FeatureFlagSelector
from azure.appconfiguration.provider._constants import (
    NULL_CHAR,
    TELEMETRY_KEY,
    METADATA_KEY,
    ETAG_KEY,
    FEATURE_FLAG_REFERENCE_KEY,
    FEATURE_MANAGEMENT_KEY,
    FEATURE_FLAG_KEY,
    REQUIRED_API_VERSION,
)
from azure.appconfiguration.provider._refresh_timer import _RefreshTimer


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

    def test_two_character_string_input(self):
        """Test with a two-character string input is treated as a key, not unpacked character-by-character."""
        result = _build_watched_setting("ab")
        self.assertEqual(result, ("ab", NULL_CHAR))

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

    def test_enhanced_feature_flag_selectors_excludes_snapshot_selectors(self):
        key_select = SettingSelector(key_filter="app:*")
        snapshot_select = SettingSelector(snapshot_name="my-snapshot")
        feature_flag_selectors = [snapshot_select, key_select]

        provider = AzureAppConfigurationProviderBase(
            endpoint="https://test.azconfig.io",
            feature_flag_selectors=feature_flag_selectors,
        )

        self.assertEqual(provider._feature_flag_selectors, feature_flag_selectors)
        self.assertEqual(len(provider._enhanced_feature_flag_selectors), 1)
        self.assertIsInstance(provider._enhanced_feature_flag_selectors[0], FeatureFlagSelector)
        self.assertEqual(provider._enhanced_feature_flag_selectors[0].name_filter, key_select.key_filter)
        self.assertEqual(provider._enhanced_feature_flag_selectors[0].label_filter, key_select.label_filter)

    def test_feature_flag_selectors_none_defaults_to_all_unlabeled_flags(self):
        provider = AzureAppConfigurationProviderBase(endpoint="https://test.azconfig.io")

        self.assertEqual(len(provider._feature_flag_selectors), 1)
        self.assertEqual(provider._feature_flag_selectors[0].key_filter, "*")
        self.assertEqual(len(provider._enhanced_feature_flag_selectors), 1)
        self.assertEqual(provider._enhanced_feature_flag_selectors[0].name_filter, "*")

    def test_feature_flag_selectors_explicit_empty_list_loads_none(self):
        provider = AzureAppConfigurationProviderBase(
            endpoint="https://test.azconfig.io",
            feature_flag_selectors=[],
        )

        self.assertEqual(provider._feature_flag_selectors, [])
        self.assertEqual(provider._enhanced_feature_flag_selectors, [])

    def test_feature_flag_enabled_with_required_api_version_succeeds(self):
        provider = AzureAppConfigurationProviderBase(
            endpoint="https://test.azconfig.io",
            feature_flag_enabled=True,
            api_version=REQUIRED_API_VERSION,
        )

        self.assertTrue(provider._feature_flag_enabled)

    def test_feature_flag_enabled_with_no_api_version_succeeds(self):
        # No explicit api_version means the SDK client's own default will be used, which already supports enhanced
        # feature flags, so no validation error should be raised.
        provider = AzureAppConfigurationProviderBase(
            endpoint="https://test.azconfig.io",
            feature_flag_enabled=True,
        )

        self.assertTrue(provider._feature_flag_enabled)

    def test_feature_flag_enabled_with_outdated_api_version_raises_error(self):
        with self.assertRaises(ValueError) as context:
            AzureAppConfigurationProviderBase(
                endpoint="https://test.azconfig.io",
                feature_flag_enabled=True,
                api_version="2023-11-01",
            )

        self.assertIn("2023-11-01", str(context.exception))
        self.assertIn(REQUIRED_API_VERSION, str(context.exception))

    def test_feature_flag_disabled_with_outdated_api_version_does_not_raise(self):
        # api_version validation only applies when feature_flag_enabled is True, since enhanced feature flags are
        # only loaded in that case.
        provider = AzureAppConfigurationProviderBase(
            endpoint="https://test.azconfig.io",
            feature_flag_enabled=False,
            api_version="2023-11-01",
        )

        self.assertFalse(provider._feature_flag_enabled)

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
        feature_flag = FeatureFlagConfigurationSetting("test_feature")

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
            except Exception:  # pylint: disable=broad-except
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


class TestProcessEnhancedFeatureFlag(unittest.TestCase):
    """Test processing of feature flags loaded from the dedicated enhanced feature flag endpoint."""

    def setUp(self):
        self.provider = AzureAppConfigurationProviderBase(endpoint="https://test.azconfig.io")

    def test_process_enhanced_feature_flag_minimal(self):
        """Test processing a minimal enhanced feature flag."""
        feature_flag = FeatureFlag(name="MyFeature", enabled=True)

        result = self.provider._process_enhanced_feature_flag(feature_flag)

        self.assertEqual(result["id"], "MyFeature")
        self.assertTrue(result["enabled"])
        self.assertNotIn("label", result)
        self.assertNotIn("description", result)
        self.assertNotIn("conditions", result)
        self.assertNotIn("variants", result)
        self.assertNotIn("allocation", result)
        self.assertNotIn("tags", result)
        # Telemetry metadata (ETag) is always attached during processing, even without an explicit
        # telemetry configuration on the enhanced feature flag.
        self.assertIn("telemetry", result)
        self.assertNotIn("enabled", result["telemetry"])

    def test_process_enhanced_feature_flag_sets_uses_enhanced_feature_flags_tracing(self):
        """Processing and merging enhanced feature flags should mark the tracing context as having used the
        enhanced feature flag endpoint, for the Correlation-Context telemetry header. The flag should reset to
        False if a subsequent refresh returns no enhanced feature flags."""
        self.assertFalse(self.provider._tracing_context.uses_enhanced_feature_flags)

        feature_flag = FeatureFlag(name="MyFeature", enabled=True)
        self.provider._process_and_merge_feature_flags({}, [], [], [feature_flag])

        self.assertTrue(self.provider._tracing_context.uses_enhanced_feature_flags)

        self.provider._process_and_merge_feature_flags({}, [], [], [])

        self.assertFalse(self.provider._tracing_context.uses_enhanced_feature_flags)

    def test_uses_enhanced_feature_flags_tracing_not_reset_when_enhanced_flags_not_refreshed(self):
        """Regression test: if a refresh only touches key-value feature flags (enhanced_feature_flags=None,
        meaning the enhanced feature flag source was not refreshed this time), the tracing context must not be
        reset to False when enhanced feature flags are already loaded from a previous refresh."""
        feature_flag = FeatureFlag(name="MyFeature", enabled=True)
        self.provider._process_and_merge_feature_flags({}, [], [], [feature_flag])
        self.assertTrue(self.provider._tracing_context.uses_enhanced_feature_flags)

        # Simulate a refresh where only key-value feature flags were refreshed; enhanced_feature_flags=None
        # indicates that source wasn't touched this time.
        self.provider._process_and_merge_feature_flags({}, [], [], None)

        self.assertTrue(self.provider._tracing_context.uses_enhanced_feature_flags)

    def test_process_enhanced_feature_flag_with_label_and_description(self):
        """Test processing an enhanced feature flag with label and description."""
        feature_flag = FeatureFlag(name="MyFeature", enabled=False, label="prod", description="A test feature")

        result = self.provider._process_enhanced_feature_flag(feature_flag)

        self.assertEqual(result["id"], "MyFeature")
        self.assertFalse(result["enabled"])
        self.assertEqual(result["label"], "prod")
        self.assertEqual(result["description"], "A test feature")

    def test_process_enhanced_feature_flag_with_conditions(self):
        """Test processing an enhanced feature flag with conditions/client filters."""
        feature_flag = FeatureFlag(
            name="MyFeature",
            enabled=True,
            conditions=FeatureFlagConditions(
                requirement_type="All",
                filters=[FeatureFilter(name="Percentage", parameters={"Value": "50"})],
            ),
        )

        result = self.provider._process_enhanced_feature_flag(feature_flag)

        self.assertEqual(result["conditions"]["requirement_type"], "All")
        self.assertEqual(len(result["conditions"]["client_filters"]), 1)
        self.assertEqual(result["conditions"]["client_filters"][0]["name"], "Percentage")
        self.assertEqual(result["conditions"]["client_filters"][0]["parameters"], {"Value": "50"})

    def test_process_enhanced_feature_flag_filter_parameter_json_object_is_parsed(self):
        """Test that a filter parameter value that looks like a JSON object is parsed as JSON."""
        feature_flag = FeatureFlag(
            name="MyFeature",
            enabled=True,
            conditions=FeatureFlagConditions(
                filters=[FeatureFilter(name="Audience", parameters={"Users": '{"a": 1}'})],
            ),
        )

        result = self.provider._process_enhanced_feature_flag(feature_flag)

        self.assertEqual(result["conditions"]["client_filters"][0]["parameters"], {"Users": {"a": 1}})

    def test_process_enhanced_feature_flag_filter_parameter_json_array_is_parsed(self):
        """Test that a filter parameter value that looks like a JSON array is parsed as JSON."""
        feature_flag = FeatureFlag(
            name="MyFeature",
            enabled=True,
            conditions=FeatureFlagConditions(
                filters=[FeatureFilter(name="Audience", parameters={"Groups": "[1, 2, 3]"})],
            ),
        )

        result = self.provider._process_enhanced_feature_flag(feature_flag)

        self.assertEqual(result["conditions"]["client_filters"][0]["parameters"], {"Groups": [1, 2, 3]})

    def test_process_enhanced_feature_flag_filter_parameter_invalid_json_falls_back_to_string(self):
        """Test that a filter parameter value that looks like JSON but fails to parse falls back to the raw
        string, rather than raising, since the customer may have intended a literal string value."""
        feature_flag = FeatureFlag(
            name="MyFeature",
            enabled=True,
            conditions=FeatureFlagConditions(
                filters=[FeatureFilter(name="Audience", parameters={"Users": "{ invalid json"})],
            ),
        )

        result = self.provider._process_enhanced_feature_flag(feature_flag)

        self.assertEqual(result["conditions"]["client_filters"][0]["parameters"], {"Users": "{ invalid json"})

    def test_process_enhanced_feature_flag_filter_parameter_plain_string_is_not_parsed(self):
        """Test that a plain string filter parameter value (not starting with '{' or '[') is left unchanged."""
        feature_flag = FeatureFlag(
            name="MyFeature",
            enabled=True,
            conditions=FeatureFlagConditions(
                filters=[FeatureFilter(name="Audience", parameters={"Region": "US"})],
            ),
        )

        result = self.provider._process_enhanced_feature_flag(feature_flag)

        self.assertEqual(result["conditions"]["client_filters"][0]["parameters"], {"Region": "US"})

    def test_process_enhanced_feature_flag_with_variants_and_allocation(self):
        """Test processing an enhanced feature flag with variants and allocation. Variant values, like regular
        key-value settings, are raw strings on the wire: a variant with a JSON content type is parsed into a JSON
        object, while a variant with no (or non-JSON) content type is kept as the raw string."""
        feature_flag = FeatureFlag(
            name="MyFeature",
            enabled=True,
            variants=[
                FeatureFlagVariantDefinition(name="Control", value="control_value"),
                FeatureFlagVariantDefinition(
                    name="Test", value='{"key": "test_value"}', content_type="application/json"
                ),
            ],
            allocation=FeatureFlagAllocation(
                default_when_disabled="Control",
                default_when_enabled="Test",
                percentile=[PercentileAllocation(variant="Control", percentile_from=0, percentile_to=50)],
                user=[UserAllocation(variant="Test", users=["user1"])],
                group=[GroupAllocation(variant="Test", groups=["group1"])],
                seed="1234",
            ),
        )

        result = self.provider._process_enhanced_feature_flag(feature_flag)

        self.assertEqual(len(result["variants"]), 2)
        self.assertEqual(result["variants"][0]["name"], "Control")
        # No content type: falls back to the raw string value, unparsed.
        self.assertEqual(result["variants"][0]["configuration_value"], "control_value")
        self.assertEqual(result["variants"][1]["content_type"], "application/json")
        # JSON content type: the raw string value is parsed into a JSON object.
        self.assertEqual(result["variants"][1]["configuration_value"], {"key": "test_value"})

        allocation = result["allocation"]
        self.assertEqual(allocation["default_when_disabled"], "Control")
        self.assertEqual(allocation["default_when_enabled"], "Test")
        self.assertEqual(allocation["percentile"], [{"variant": "Control", "from": 0, "to": 50}])
        self.assertEqual(allocation["user"], [{"variant": "Test", "users": ["user1"]}])
        self.assertEqual(allocation["group"], [{"variant": "Test", "groups": ["group1"]}])
        self.assertEqual(allocation["seed"], "1234")

    def test_process_enhanced_feature_flag_invalid_variant_json_raises_value_error(self):
        """If a variant's content type claims JSON but its value is invalid JSON, processing the enhanced feature
        flag should raise a clear ValueError identifying the offending flag, chained from the underlying
        JSONDecodeError."""
        feature_flag = FeatureFlag(
            name="InvalidVariant",
            enabled=True,
            variants=[
                FeatureFlagVariantDefinition(name="Variant", value="{ invalid json", content_type="application/json")
            ],
        )

        with self.assertRaises(ValueError) as context:
            self.provider._process_enhanced_feature_flag(feature_flag)

        self.assertIn("InvalidVariant", str(context.exception))
        self.assertIsInstance(context.exception.__cause__, json.JSONDecodeError)

    def test_process_enhanced_feature_flag_with_telemetry_and_tags(self):
        """Test processing an enhanced feature flag with telemetry settings and tags."""
        feature_flag = FeatureFlag(
            name="MyFeature",
            enabled=True,
            telemetry=FeatureFlagTelemetryConfiguration(enabled=True, metadata={"custom": "value"}),
            tags={"team": "infra"},
        )

        result = self.provider._process_enhanced_feature_flag(feature_flag)

        # Telemetry metadata gets ETag/FeatureFlagReference metadata appended by
        # _update_enhanced_feature_flag_telemetry_metadata as part of processing.
        self.assertTrue(result["telemetry"]["enabled"])
        self.assertEqual(result["telemetry"]["metadata"]["custom"], "value")
        self.assertEqual(result["tags"], {"team": "infra"})

    def test_process_enhanced_feature_flag_updates_telemetry_metadata(self):
        """Test that processing an enhanced feature flag adds ETag/FeatureFlagReference telemetry metadata."""
        feature_flag = FeatureFlag(
            name="MyFeature",
            enabled=True,
            label="prod",
            telemetry=FeatureFlagTelemetryConfiguration(enabled=True),
        )
        feature_flag.etag = "enhanced_etag"

        result = self.provider._process_enhanced_feature_flag(feature_flag)

        metadata = result["telemetry"][METADATA_KEY]
        self.assertEqual(metadata[ETAG_KEY], "enhanced_etag")
        self.assertIn(FEATURE_FLAG_REFERENCE_KEY, metadata)
        # The enhanced feature flag reference uses the "ff" path segment, not "kv".
        self.assertIn("/ff/MyFeature", metadata[FEATURE_FLAG_REFERENCE_KEY])
        self.assertIn("?label=prod", metadata[FEATURE_FLAG_REFERENCE_KEY])


class TestParseVariantValue(unittest.TestCase):
    """Test the _parse_variant_value static method, used to interpret an enhanced feature flag variant's raw
    string value based on its content type, mirroring how regular key-value settings are processed."""

    def test_json_content_type_parses_object(self):
        result = AzureAppConfigurationProviderBase._parse_variant_value('{"key": "value"}', "application/json")
        self.assertEqual(result, {"key": "value"})

    def test_json_content_type_parses_array(self):
        result = AzureAppConfigurationProviderBase._parse_variant_value("[1, 2, 3]", "application/json")
        self.assertEqual(result, [1, 2, 3])

    def test_json_content_type_with_charset_parses_object(self):
        result = AzureAppConfigurationProviderBase._parse_variant_value(
            '{"key": "value"}', "application/json; charset=utf-8"
        )
        self.assertEqual(result, {"key": "value"})

    def test_json_content_type_with_structured_suffix_parses_object(self):
        """Content types using the '+json' structured syntax suffix (e.g. a vendor-specific media type) are
        also treated as JSON."""
        result = AzureAppConfigurationProviderBase._parse_variant_value(
            '{"key": "value"}', "application/vnd.microsoft.appconfig.ff+json"
        )
        self.assertEqual(result, {"key": "value"})

    def test_no_content_type_falls_back_to_raw_string(self):
        result = AzureAppConfigurationProviderBase._parse_variant_value("plain_value", None)
        self.assertEqual(result, "plain_value")

    def test_non_json_content_type_falls_back_to_raw_string(self):
        result = AzureAppConfigurationProviderBase._parse_variant_value("plain_value", "text/plain")
        self.assertEqual(result, "plain_value")

    def test_text_json_content_type_is_not_treated_as_json(self):
        """'text/json' is not an 'application/*' JSON media type, so it should be treated as a raw string, even
        though it contains the substring 'json'."""
        result = AzureAppConfigurationProviderBase._parse_variant_value("{ invalid json", "text/json")
        self.assertEqual(result, "{ invalid json")


class TestParseFilterParameterValue(unittest.TestCase):
    """Tests for _parse_filter_parameter_value, which parses enhanced feature flag filter parameter values as a
    best-effort attempt, always falling back to the raw string on failure since filter parameters have no
    content type to declare JSON intent (unlike variant values)."""

    def test_json_object_is_parsed(self):
        result = AzureAppConfigurationProviderBase._parse_filter_parameter_value('{"a": 1}')
        self.assertEqual(result, {"a": 1})

    def test_json_array_is_parsed(self):
        result = AzureAppConfigurationProviderBase._parse_filter_parameter_value("[1, 2, 3]")
        self.assertEqual(result, [1, 2, 3])

    def test_invalid_json_object_falls_back_to_string(self):
        result = AzureAppConfigurationProviderBase._parse_filter_parameter_value("{ invalid json")
        self.assertEqual(result, "{ invalid json")

    def test_invalid_json_array_falls_back_to_string(self):
        result = AzureAppConfigurationProviderBase._parse_filter_parameter_value("[ invalid json")
        self.assertEqual(result, "[ invalid json")

    def test_plain_string_is_not_parsed(self):
        result = AzureAppConfigurationProviderBase._parse_filter_parameter_value("US")
        self.assertEqual(result, "US")

    def test_empty_string_is_not_parsed(self):
        result = AzureAppConfigurationProviderBase._parse_filter_parameter_value("")
        self.assertEqual(result, "")

    def test_json_literal_null_string_is_not_parsed(self):
        """The literal string 'null' doesn't start with '{' or '[', so it should be left as a raw string, not
        parsed into JSON null."""
        result = AzureAppConfigurationProviderBase._parse_filter_parameter_value("null")
        self.assertEqual(result, "null")

    def test_non_string_value_is_returned_unchanged(self):
        result = AzureAppConfigurationProviderBase._parse_filter_parameter_value(None)
        self.assertIsNone(result)

    def test_json_content_type_with_invalid_json_raises(self):
        """If the content type claims JSON but the value is not valid JSON, parsing should raise instead of
        silently falling back to the raw string."""
        with self.assertRaises(json.JSONDecodeError):
            AzureAppConfigurationProviderBase._parse_variant_value("not valid json", "application/json")

    def test_none_value_returns_none(self):
        result = AzureAppConfigurationProviderBase._parse_variant_value(None, "application/json")
        self.assertIsNone(result)


class TestUpdateEnhancedFeatureFlagTelemetryMetadata(unittest.TestCase):
    """Test the _update_enhanced_feature_flag_telemetry_metadata method."""

    def setUp(self):
        self.provider = AzureAppConfigurationProviderBase(endpoint="https://test.azconfig.io")

    def test_update_enhanced_feature_flag_telemetry_metadata(self):
        """Test enhanced feature flag telemetry processing uses the 'ff' reference segment."""
        feature_flag = FeatureFlag(name="test_feature", enabled=True, label="test_label")
        feature_flag.etag = "test_etag"

        feature_flag_value: Dict[str, Any] = {TELEMETRY_KEY: {"enabled": True}}
        endpoint = "https://test.azconfig.io"

        self.provider._update_enhanced_feature_flag_telemetry_metadata(endpoint, feature_flag, feature_flag_value)

        metadata = feature_flag_value[TELEMETRY_KEY][METADATA_KEY]
        self.assertEqual(metadata[ETAG_KEY], "test_etag")
        self.assertIn(FEATURE_FLAG_REFERENCE_KEY, metadata)
        self.assertIn("/ff/test_feature", metadata[FEATURE_FLAG_REFERENCE_KEY])
        self.assertIn("?label=test_label", metadata[FEATURE_FLAG_REFERENCE_KEY])


class TestMergeFeatureFlags(unittest.TestCase):
    """Test the _merge_feature_flags static method."""

    def test_merge_no_overlap(self):
        """Test merging when there is no identifier overlap between the two sources."""
        kv_flags = [{"id": "KvFeature", "enabled": True}]
        enhanced_flags = [{"id": "EnhancedFeature", "enabled": False}]

        merged = AzureAppConfigurationProviderBase._merge_feature_flags(kv_flags, enhanced_flags)

        self.assertEqual(len(merged), 2)
        self.assertIn({"id": "KvFeature", "enabled": True}, merged)
        self.assertIn({"id": "EnhancedFeature", "enabled": False}, merged)

    def test_merge_enhanced_takes_precedence_on_collision(self):
        """Test that an enhanced feature flag overrides a key-value one with the same identifier."""
        kv_flags = [{"id": "SharedFeature", "enabled": False, "source": "kv"}]
        enhanced_flags = [{"id": "SharedFeature", "enabled": True, "source": "enhanced"}]

        merged = AzureAppConfigurationProviderBase._merge_feature_flags(kv_flags, enhanced_flags)

        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["source"], "enhanced")
        self.assertTrue(merged[0]["enabled"])

    def test_merge_empty_lists(self):
        """Test merging two empty lists returns an empty list."""
        merged = AzureAppConfigurationProviderBase._merge_feature_flags([], [])
        self.assertEqual(merged, [])

    def test_merge_only_kv_flags(self):
        """Test merging when only key-value based feature flags are present."""
        kv_flags = [{"id": "Feature1", "enabled": True}, {"id": "Feature2", "enabled": False}]

        merged = AzureAppConfigurationProviderBase._merge_feature_flags(kv_flags, [])

        self.assertEqual(len(merged), 2)

    def test_merge_only_enhanced_flags(self):
        """Test merging when only enhanced feature flags are present."""
        enhanced_flags = [{"id": "Feature1", "enabled": True}, {"id": "Feature2", "enabled": False}]

        merged = AzureAppConfigurationProviderBase._merge_feature_flags([], enhanced_flags)

        self.assertEqual(len(merged), 2)


class TestProcessAndMergeFeatureFlags(unittest.TestCase):
    """Test _process_and_merge_feature_flags distinguishes None (not loaded this round) from an explicitly
    empty list (loaded this round, zero found)."""

    def setUp(self):
        self.provider = AzureAppConfigurationProviderBase(
            endpoint="https://test.azconfig.io", feature_flag_enabled=True
        )

    def test_enhanced_feature_flags_none_preserves_previous_processed_flags(self):
        feature_flag = FeatureFlag(name="MyFeature", enabled=True)
        self.provider._process_and_merge_feature_flags({}, [], None, [feature_flag])
        self.assertEqual(len(self.provider._processed_enhanced_feature_flags), 1)

        # Passing None again should leave the previously processed enhanced feature flags untouched.
        self.provider._process_and_merge_feature_flags({}, [], None, None)
        self.assertEqual(len(self.provider._processed_enhanced_feature_flags), 1)

    def test_enhanced_feature_flags_explicit_empty_list_clears_previous_processed_flags(self):
        feature_flag = FeatureFlag(name="MyFeature", enabled=True)
        self.provider._process_and_merge_feature_flags({}, [], None, [feature_flag])
        self.assertEqual(len(self.provider._processed_enhanced_feature_flags), 1)

        # An explicitly empty list means the endpoint was queried and returned zero feature flags.
        self.provider._process_and_merge_feature_flags({}, [], None, [])
        self.assertEqual(self.provider._processed_enhanced_feature_flags, [])

    def test_kv_feature_flags_none_preserves_previous_processed_flags(self):
        """Same as the enhanced-flag case above, but for key-value based feature flags: passing None (not
        refreshed this round) must not clear or overwrite the previously cached key-value feature flags."""
        kv_flag = FeatureFlagConfigurationSetting(feature_id="MyFeature", enabled=True, label=NULL_CHAR)
        self.provider._process_and_merge_feature_flags({}, [], [kv_flag], None)
        self.assertEqual(len(self.provider._processed_kv_feature_flags), 1)

        # Passing None again should leave the previously processed key-value feature flags untouched.
        self.provider._process_and_merge_feature_flags({}, [], None, None)
        self.assertEqual(len(self.provider._processed_kv_feature_flags), 1)

    def test_kv_feature_flags_explicit_empty_list_clears_previous_processed_flags(self):
        """An explicitly empty list for key-value feature flags means the store was queried and returned zero
        feature flags, so the previously cached key-value feature flags should be cleared."""
        kv_flag = FeatureFlagConfigurationSetting(feature_id="MyFeature", enabled=True, label=NULL_CHAR)
        self.provider._process_and_merge_feature_flags({}, [], [kv_flag], None)
        self.assertEqual(len(self.provider._processed_kv_feature_flags), 1)

        self.provider._process_and_merge_feature_flags({}, [], [], None)
        self.assertEqual(self.provider._processed_kv_feature_flags, [])

    def test_both_none_preserves_merged_result_unchanged(self):
        """When neither source was refreshed (both None), the merge step should be skipped entirely and the
        previously merged/processed feature flag list should be returned untouched."""
        kv_flag = FeatureFlagConfigurationSetting(feature_id="KvFeature", enabled=True, label=NULL_CHAR)
        enhanced_flag = FeatureFlag(name="EnhancedFeature", enabled=False)

        settings = self.provider._process_and_merge_feature_flags({}, [], [kv_flag], [enhanced_flag])
        previous_merged = settings[FEATURE_MANAGEMENT_KEY][FEATURE_FLAG_KEY]
        self.assertEqual(len(previous_merged), 2)

        # Neither source refreshed this round: the previously merged list is passed through as
        # processed_feature_flags and should come back unchanged.
        settings = self.provider._process_and_merge_feature_flags({}, previous_merged, None, None)
        self.assertEqual(settings[FEATURE_MANAGEMENT_KEY][FEATURE_FLAG_KEY], previous_merged)

    def test_only_kv_refreshed_still_merges_with_cached_enhanced_flags(self):
        """If only key-value feature flags are refreshed (enhanced is None), the merge should still combine the
        newly refreshed kv flags with the previously cached enhanced feature flags."""
        enhanced_flag = FeatureFlag(name="EnhancedFeature", enabled=True)
        self.provider._process_and_merge_feature_flags({}, [], [], [enhanced_flag])
        self.assertEqual(len(self.provider._processed_enhanced_feature_flags), 1)

        kv_flag = FeatureFlagConfigurationSetting(feature_id="KvFeature", enabled=True, label=NULL_CHAR)
        settings = self.provider._process_and_merge_feature_flags({}, [], [kv_flag], None)
        merged_ids = {ff["id"] for ff in settings[FEATURE_MANAGEMENT_KEY][FEATURE_FLAG_KEY]}
        self.assertEqual(merged_ids, {"KvFeature", "EnhancedFeature"})


if __name__ == "__main__":
    unittest.main()
