# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import unittest
import os
import time
import datetime
import json
import base64
from unittest.mock import patch, Mock
from typing import Dict, Any

from azure.appconfiguration import FeatureFlagConfigurationSetting
from azure.appconfiguration.provider._azureappconfigurationproviderbase import (
    _build_sentinel,
    AzureAppConfigurationProviderBase,
    process_load_arguments,
    process_key_vault_options,
)
from azure.appconfiguration.provider._models import SettingSelector
from azure.appconfiguration.provider._constants import (
    REQUEST_TRACING_DISABLED_ENVIRONMENT_VARIABLE,
    ServiceFabricEnvironmentVariable,
    AzureFunctionEnvironmentVariable,
    AzureWebAppEnvironmentVariable,
    ContainerAppEnvironmentVariable,
    KubernetesEnvironmentVariable,
    NULL_CHAR,
    CUSTOM_FILTER_KEY,
    PERCENTAGE_FILTER_KEY,
    TIME_WINDOW_FILTER_KEY,
    TARGETING_FILTER_KEY,
    PERCENTAGE_FILTER_NAMES,
    TIME_WINDOW_FILTER_NAMES,
    TARGETING_FILTER_NAMES,
    TELEMETRY_KEY,
    METADATA_KEY,
    ETAG_KEY,
    FEATURE_FLAG_REFERENCE_KEY,
    APP_CONFIG_AI_MIME_PROFILE,
    APP_CONFIG_AICC_MIME_PROFILE,
)


class TestBuildSentinel(unittest.TestCase):
    """Test the _build_sentinel function."""

    def test_string_input(self):
        """Test with string input."""
        result = _build_sentinel("test_key")
        self.assertEqual(result, ("test_key", NULL_CHAR))

    def test_tuple_input(self):
        """Test with tuple input."""
        result = _build_sentinel(("test_key", "test_label"))
        self.assertEqual(result, ("test_key", "test_label"))

    def test_wildcard_key_raises_error(self):
        """Test that wildcard in key raises ValueError."""
        with self.assertRaises(ValueError):
            _build_sentinel("test*key")

    def test_wildcard_label_raises_error(self):
        """Test that wildcard in label raises ValueError."""
        with self.assertRaises(ValueError):
            _build_sentinel(("test_key", "test*label"))


class TestValidateLoadArguments(unittest.TestCase):
    """Test the process_load_arguments function."""

    def test_no_args_valid(self):
        """Test that no arguments raises ValueError."""
        kwargs = {}
        with self.assertRaises(ValueError) as context:
            process_load_arguments(**kwargs)
        self.assertIn("Either 'endpoint' or 'connection_string' must be provided", str(context.exception))

    def test_endpoint_only_valid(self):
        """Test endpoint only is valid."""
        kwargs = {"endpoint": "https://test.azconfig.io"}
        result_kwargs = process_load_arguments(**kwargs)
        self.assertEqual(result_kwargs["endpoint"], "https://test.azconfig.io")

    def test_connection_string_only_valid(self):
        """Test connection string only is valid."""
        kwargs = {"connection_string": "Endpoint=https://test.azconfig.io;Id=test-id;Secret=test-secret"}
        result_kwargs = process_load_arguments(**kwargs)
        self.assertEqual(
            result_kwargs["connection_string"], "Endpoint=https://test.azconfig.io;Id=test-id;Secret=test-secret"
        )

    def test_positional_endpoint(self):
        """Test positional endpoint argument."""
        result_kwargs = process_load_arguments("https://test.azconfig.io")
        self.assertEqual(result_kwargs["endpoint"], "https://test.azconfig.io")

    def test_positional_endpoint_and_credential(self):
        """Test positional endpoint and credential arguments."""
        mock_credential = Mock()
        result_kwargs = process_load_arguments("https://test.azconfig.io", mock_credential)
        self.assertEqual(result_kwargs["endpoint"], "https://test.azconfig.io")
        self.assertEqual(result_kwargs["credential"], mock_credential)

    def test_too_many_positional_args_raises_error(self):
        """Test that too many positional arguments raises TypeError."""
        with self.assertRaises(TypeError):
            process_load_arguments("arg1", "arg2", "arg3")

    def test_duplicate_endpoint_raises_error(self):
        """Test that duplicate endpoint specification raises TypeError."""
        with self.assertRaises(TypeError):
            process_load_arguments("https://test.azconfig.io", endpoint="https://other.azconfig.io")

    def test_both_endpoint_and_connection_string_raises_error(self):
        """Test that both endpoint and connection string raises ValueError."""
        kwargs = {"endpoint": "https://test.azconfig.io", "connection_string": "test_connection_string"}
        with self.assertRaises(ValueError):
            process_load_arguments(**kwargs)


class TestProcessKeyVaultOptions(unittest.TestCase):
    """Test the process_key_vault_options function."""

    def test_no_key_vault_options(self):
        """Test with no key vault options."""
        kwargs = {"some_param": "value"}
        result = process_key_vault_options(**kwargs)
        self.assertEqual(result, {"some_param": "value", "uses_key_vault": False})

    def test_key_vault_options_processing(self):
        """Test key vault options are processed correctly."""
        mock_credential = Mock()
        mock_configs = {"config": "value"}

        key_vault_options = Mock()
        key_vault_options.credential = mock_credential
        key_vault_options.secret_resolver = None  # Don't set both credential and resolver
        key_vault_options.client_configs = mock_configs

        kwargs = {"key_vault_options": key_vault_options}
        result = process_key_vault_options(**kwargs)

        self.assertEqual(result["keyvault_credential"], mock_credential)
        self.assertEqual(result["secret_resolver"], None)
        self.assertEqual(result["keyvault_client_configs"], mock_configs)
        self.assertTrue(result["uses_key_vault"])
        self.assertNotIn("key_vault_options", result)

    def test_conflicting_options_raises_error(self):
        """Test that conflicting key vault options raise ValueError."""
        key_vault_options = Mock()
        kwargs = {"key_vault_options": key_vault_options, "keyvault_credential": Mock()}
        with self.assertRaises(ValueError):
            process_key_vault_options(**kwargs)

    def test_both_credential_and_resolver_raises_error(self):
        """Test that both credential and resolver raise ValueError."""
        kwargs = {"keyvault_credential": Mock(), "secret_resolver": Mock()}
        with self.assertRaises(ValueError):
            process_key_vault_options(**kwargs)

    def test_keyvault_credential_indicates_usage(self):
        """Test that keyvault_credential indicates key vault usage."""
        kwargs = {"keyvault_credential": Mock()}
        result = process_key_vault_options(**kwargs)
        self.assertTrue(result["uses_key_vault"])

    def test_keyvault_client_configs_indicates_usage(self):
        """Test that keyvault_client_configs indicates key vault usage."""
        kwargs = {"keyvault_client_configs": {"config": "value"}}
        result = process_key_vault_options(**kwargs)
        self.assertTrue(result["uses_key_vault"])

    def test_secret_resolver_indicates_usage(self):
        """Test that secret_resolver indicates key vault usage."""
        kwargs = {"secret_resolver": Mock()}
        result = process_key_vault_options(**kwargs)
        self.assertTrue(result["uses_key_vault"])

    def test_explicit_uses_key_vault_flag(self):
        """Test explicit uses_key_vault flag is preserved."""
        kwargs = {"uses_key_vault": True}
        result = process_key_vault_options(**kwargs)
        self.assertTrue(result["uses_key_vault"])

    def test_explicit_false_flag_overridden_by_credentials(self):
        """Test explicit false flag is overridden when credentials are present."""
        kwargs = {"uses_key_vault": False, "keyvault_credential": Mock()}
        result = process_key_vault_options(**kwargs)
        self.assertTrue(result["uses_key_vault"])


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

    def test_process_non_keyvault_value_plain_text(self):
        """Test processing non-keyvault plain text value."""
        config = Mock()
        config.content_type = "text/plain"
        config.value = "plain text value"

        result = self.provider._process_non_keyvault_value(config)
        self.assertEqual(result, "plain text value")

    def test_process_non_keyvault_value_json(self):
        """Test processing non-keyvault JSON value."""
        config = Mock()
        config.content_type = "application/json"
        config.value = '{"key": "value", "number": 42}'

        result = self.provider._process_non_keyvault_value(config)
        expected = {"key": "value", "number": 42}
        self.assertEqual(result, expected)

    def test_process_non_keyvault_value_invalid_json(self):
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
            result = self.provider._process_non_keyvault_value(config)
            self.assertEqual(result, '{"invalid": json}')  # Should return as string

    def test_process_non_keyvault_value_ai_configuration(self):
        """Test processing AI configuration content type."""
        config = Mock()
        config.content_type = f"application/json; {APP_CONFIG_AI_MIME_PROFILE}"
        config.value = '{"ai_config": "value"}'

        result = self.provider._process_non_keyvault_value(config)
        self.assertTrue(self.provider._uses_ai_configuration)
        self.assertEqual(result, {"ai_config": "value"})

    def test_process_non_keyvault_value_aicc_configuration(self):
        """Test processing AI Chat Completion configuration content type."""
        config = Mock()
        config.content_type = f"application/json; {APP_CONFIG_AICC_MIME_PROFILE}"
        config.value = '{"aicc_config": "value"}'

        result = self.provider._process_non_keyvault_value(config)
        self.assertTrue(self.provider._uses_aicc_configuration)
        self.assertEqual(result, {"aicc_config": "value"})

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

    def test_feature_flag_appconfig_telemetry(self):
        """Test feature flag app config telemetry tracking."""
        feature_flag = Mock(spec=FeatureFlagConfigurationSetting)
        feature_flag.filters = [
            {"name": PERCENTAGE_FILTER_NAMES[0]},
            {"name": TIME_WINDOW_FILTER_NAMES[0]},
            {"name": "CustomFilter"},
            {"name": TARGETING_FILTER_NAMES[0]},
        ]

        self.provider._feature_flag_appconfig_telemetry(feature_flag)

        self.assertTrue(self.provider._feature_filter_usage[PERCENTAGE_FILTER_KEY])
        self.assertTrue(self.provider._feature_filter_usage[TIME_WINDOW_FILTER_KEY])
        self.assertTrue(self.provider._feature_filter_usage[CUSTOM_FILTER_KEY])
        self.assertTrue(self.provider._feature_filter_usage[TARGETING_FILTER_KEY])

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
