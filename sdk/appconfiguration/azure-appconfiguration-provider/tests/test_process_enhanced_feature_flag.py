# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import unittest
import json

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
from azure.appconfiguration.provider._azureappconfigurationproviderbase import AzureAppConfigurationProviderBase
from azure.appconfiguration.provider._constants import (
    METADATA_KEY,
    ETAG_KEY,
    FEATURE_FLAG_REFERENCE_KEY,
)


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
