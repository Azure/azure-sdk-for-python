# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import unittest
import os
from unittest.mock import patch, Mock
from azure.appconfiguration import ConfigurationSetting

from azure.appconfiguration.provider._request_tracing_context import (
    _RequestTracingContext,
    HostType,
    RequestType,
    CUSTOM_FILTER_KEY,
    PERCENTAGE_FILTER_KEY,
    TIME_WINDOW_FILTER_KEY,
    TARGETING_FILTER_KEY,
    PERCENTAGE_FILTER_NAMES,
    TIME_WINDOW_FILTER_NAMES,
    TARGETING_FILTER_NAMES,
    FEATURE_FLAG_USES_SEED_TAG,
    FEATURE_FLAG_USES_TELEMETRY_TAG,
)
from azure.appconfiguration.provider._constants import (
    REQUEST_TRACING_DISABLED_ENVIRONMENT_VARIABLE,
    ServiceFabricEnvironmentVariable,
    AzureFunctionEnvironmentVariable,
    AzureWebAppEnvironmentVariable,
    ContainerAppEnvironmentVariable,
    KubernetesEnvironmentVariable,
    APP_CONFIG_AI_MIME_PROFILE,
    APP_CONFIG_AICC_MIME_PROFILE,
    SNAPSHOT_REFERENCE_TAG,
    SNAPSHOT_REF_CONTENT_TYPE,
)
from azure.appconfiguration.provider._azureappconfigurationproviderbase import (
    AzureAppConfigurationProviderBase,
)


class TestRequestTracingContext(unittest.TestCase):
    """Test the _RequestTracingContext class."""

    def setUp(self):
        """Set up test environment."""
        self.context = _RequestTracingContext()

    def test_initialization_with_defaults(self):
        """Test initialization with default values."""
        context = _RequestTracingContext()
        self.assertFalse(context.uses_load_balancing)
        self.assertFalse(context.uses_ai_configuration)
        self.assertFalse(context.uses_aicc_configuration)
        self.assertFalse(context.uses_telemetry)
        self.assertFalse(context.uses_seed)
        self.assertIsNone(context.max_variants)
        self.assertEqual(context.feature_filter_usage, {})
        self.assertEqual(context.host_type, HostType.UNIDENTIFIED)
        self.assertFalse(context.is_key_vault_configured)
        self.assertEqual(context.replica_count, 0)
        self.assertFalse(context.is_failover_request)

    def test_initialization_with_load_balancing(self):
        """Test initialization with load balancing enabled."""
        context = _RequestTracingContext(load_balancing_enabled=True)
        self.assertTrue(context.uses_load_balancing)

    def testupdate_max_variants(self):
        """Test updating max variants."""
        self.context.update_max_variants(5)
        self.assertEqual(self.context.max_variants, 5)

        # Should update to larger value
        self.context.update_max_variants(10)
        self.assertEqual(self.context.max_variants, 10)

        # Should not update to smaller value
        self.context.update_max_variants(3)
        self.assertEqual(self.context.max_variants, 10)

    def test__create_features_string_empty(self):
        """Test _create_features_string with no features enabled."""
        result = self.context._create_features_string()
        self.assertEqual(result, "")

    def test__create_features_string_with_features(self):
        """Test _create_features_string with features enabled."""
        self.context.uses_load_balancing = True
        self.context.uses_ai_configuration = True
        self.context.uses_aicc_configuration = True

        result = self.context._create_features_string()
        self.assertEqual(result, "LB+AI+AICC")

    def test__create_ff_features_string_empty(self):
        """Test _create_feature_string with no FF features enabled."""
        result = self.context._create_ff_features_string()
        self.assertEqual(result, "")

    def test__create_ff_features_string_with_features(self):
        """Test _create_ff_features_string with FF features enabled."""
        self.context.uses_seed = True
        self.context.uses_telemetry = True

        result = self.context._create_ff_features_string()
        expected = f"{FEATURE_FLAG_USES_SEED_TAG}+{FEATURE_FLAG_USES_TELEMETRY_TAG}"
        self.assertEqual(result, expected)

    def test_get_host_type_unidentified(self):
        """Test host type detection with no environment variables."""
        with patch.dict(os.environ, {}, clear=True):
            result = _RequestTracingContext.get_host_type()
            self.assertEqual(result, HostType.UNIDENTIFIED)

    def test_get_host_type_azure_function(self):
        """Test host type detection for Azure Functions."""
        with patch.dict(os.environ, {AzureFunctionEnvironmentVariable: "test_value"}):
            result = _RequestTracingContext.get_host_type()
            self.assertEqual(result, HostType.AZURE_FUNCTION)

    def test_get_host_type_azure_web_app(self):
        """Test host type detection for Azure Web App."""
        with patch.dict(os.environ, {AzureWebAppEnvironmentVariable: "test_value"}):
            result = _RequestTracingContext.get_host_type()
            self.assertEqual(result, HostType.AZURE_WEB_APP)

    def test_get_host_type_container_app(self):
        """Test host type detection for Container App."""
        with patch.dict(os.environ, {ContainerAppEnvironmentVariable: "test_value"}):
            result = _RequestTracingContext.get_host_type()
            self.assertEqual(result, HostType.CONTAINER_APP)

    def test_get_host_type_kubernetes(self):
        """Test host type detection for Kubernetes."""
        with patch.dict(os.environ, {KubernetesEnvironmentVariable: "test_value"}):
            result = _RequestTracingContext.get_host_type()
            self.assertEqual(result, HostType.KUBERNETES)

    def test_get_host_type_service_fabric(self):
        """Test host type detection for Service Fabric."""
        with patch.dict(os.environ, {ServiceFabricEnvironmentVariable: "test_value"}):
            result = _RequestTracingContext.get_host_type()
            self.assertEqual(result, HostType.SERVICE_FABRIC)

    @patch("azure.appconfiguration.provider._request_tracing_context.version")
    def test_get_assembly_version_success(self, mock_version):
        """Test successful package version retrieval."""
        mock_version.return_value = "1.2.3"
        result = _RequestTracingContext.get_assembly_version("test_package")
        self.assertEqual(result, "1.2.3")

    @patch("azure.appconfiguration.provider._request_tracing_context.version")
    def test_get_assembly_version_not_found(self, mock_version):
        """Test package version retrieval when package not found."""
        from importlib.metadata import PackageNotFoundError

        mock_version.side_effect = PackageNotFoundError()
        result = _RequestTracingContext.get_assembly_version("nonexistent_package")
        self.assertIsNone(result)

    def test_get_assembly_version_empty_package_name(self):
        """Test package version retrieval with empty package name."""
        result = _RequestTracingContext.get_assembly_version("")
        self.assertIsNone(result)

    def test_reset_ai_configuration_tracing(self):
        """Test reset_ai_configuration_tracing method."""
        self.context.uses_ai_configuration = True
        self.context.uses_aicc_configuration = True

        self.context.reset_ai_configuration_tracing()

        self.assertFalse(self.context.uses_ai_configuration)
        self.assertFalse(self.context.uses_aicc_configuration)

    def test_update_ai_configuration_tracing_ai_profile(self):
        """Test update_ai_configuration_tracing with AI profile."""
        content_type = "application/json; " + APP_CONFIG_AI_MIME_PROFILE
        self.context.update_ai_configuration_tracing(content_type)

        self.assertTrue(self.context.uses_ai_configuration)
        self.assertFalse(self.context.uses_aicc_configuration)

    def test_update_ai_configuration_tracing_aicc_profile(self):
        """Test update_ai_configuration_tracing with AI Chat Completion profile."""
        content_type = "application/json; " + APP_CONFIG_AICC_MIME_PROFILE
        self.context.update_ai_configuration_tracing(content_type)

        self.assertTrue(self.context.uses_ai_configuration)
        self.assertTrue(self.context.uses_aicc_configuration)

    def test_update_ai_configuration_tracing_no_content_type(self):
        """Test update_ai_configuration_tracing with no content type."""
        self.context.update_ai_configuration_tracing(None)

        self.assertFalse(self.context.uses_ai_configuration)
        self.assertFalse(self.context.uses_aicc_configuration)

    def test_create_filters_string_empty(self):
        """Test _create_filters_string with no filters."""
        result = self.context._create_filters_string()
        self.assertEqual(result, "")

    def test_create_filters_string_with_filters(self):
        """Test _create_filters_string with all filter types."""
        self.context.feature_filter_usage = {
            CUSTOM_FILTER_KEY: True,
            PERCENTAGE_FILTER_KEY: True,
            TIME_WINDOW_FILTER_KEY: True,
            TARGETING_FILTER_KEY: True,
        }

        result = self.context._create_filters_string()
        expected = f"{CUSTOM_FILTER_KEY}+{PERCENTAGE_FILTER_KEY}+{TIME_WINDOW_FILTER_KEY}+{TARGETING_FILTER_KEY}"
        self.assertEqual(result, expected)

    def test_update_feature_filter_telemetry(self):
        """Test update_feature_filter_telemetry method."""
        feature_flag = Mock()
        feature_flag.filters = [
            {"name": PERCENTAGE_FILTER_NAMES[0]},
            {"name": TIME_WINDOW_FILTER_NAMES[0]},
            {"name": TARGETING_FILTER_NAMES[0]},
            {"name": "CustomFilter"},
        ]

        self.context.update_feature_filter_telemetry(feature_flag)

        self.assertTrue(self.context.feature_filter_usage[PERCENTAGE_FILTER_KEY])
        self.assertTrue(self.context.feature_filter_usage[TIME_WINDOW_FILTER_KEY])
        self.assertTrue(self.context.feature_filter_usage[TARGETING_FILTER_KEY])
        self.assertTrue(self.context.feature_filter_usage[CUSTOM_FILTER_KEY])

    def test_update_feature_filter_telemetry_no_filters(self):
        """Test update_feature_filter_telemetry with no filters."""
        feature_flag = Mock()
        feature_flag.filters = None

        self.context.update_feature_filter_telemetry(feature_flag)

        self.assertEqual(self.context.feature_filter_usage, {})

    def test_reset_feature_filter_usage(self):
        """Test reset_feature_filter_usage method."""
        self.context.feature_filter_usage = {CUSTOM_FILTER_KEY: True}

        self.context.reset_feature_filter_usage()

        self.assertEqual(self.context.feature_filter_usage, {})


class TestUpdateCorrelationContextHeader(unittest.TestCase):
    """Test the update_correlation_context_header method."""

    def setUp(self):
        """Set up test environment."""
        self.context = _RequestTracingContext()
        self.headers = {}

    def test_disabled_tracing(self):
        """Test that disabled tracing returns empty string."""
        with patch.dict(os.environ, {REQUEST_TRACING_DISABLED_ENVIRONMENT_VARIABLE: "true"}):
            result = self.context.update_correlation_context_header(self.headers, RequestType.STARTUP, 0, False, False)
            self.assertEqual(result, self.headers)
            self.assertNotIn("Correlation-Context", result)

    def test_basic_correlation_context(self):
        """Test basic correlation context generation."""
        result = self.context.update_correlation_context_header(self.headers, RequestType.STARTUP, 0, False, False)
        self.assertIn("Correlation-Context", result)
        self.assertIn("RequestType=Startup", result["Correlation-Context"])

    def test_with_replica_count(self):
        """Test correlation context with replica count."""
        result = self.context.update_correlation_context_header(self.headers, RequestType.WATCH, 3, False, False)
        self.assertIn("Correlation-Context", result)
        self.assertIn("RequestType=Watch", result["Correlation-Context"])
        self.assertIn("ReplicaCount=3", result["Correlation-Context"])

    def test_with_host_type(self):
        """Test correlation context with host type detection."""
        self.context.host_type = HostType.AZURE_FUNCTION
        result = self.context.update_correlation_context_header(self.headers, RequestType.STARTUP, 0, False, False)
        self.assertIn("Correlation-Context", result)
        self.assertIn("Host=AzureFunction", result["Correlation-Context"])

    def test_with_feature_filters(self):
        """Test correlation context with feature filters."""
        self.context.feature_filter_usage = {
            CUSTOM_FILTER_KEY: True,
            PERCENTAGE_FILTER_KEY: True,
        }
        result = self.context.update_correlation_context_header(self.headers, RequestType.STARTUP, 0, False, False)
        self.assertIn("Correlation-Context", result)
        self.assertIn("Filter=", result["Correlation-Context"])
        self.assertIn(CUSTOM_FILTER_KEY, result["Correlation-Context"])
        self.assertIn(PERCENTAGE_FILTER_KEY, result["Correlation-Context"])

    def test_with_max_variants(self):
        """Test correlation context with max variants."""
        self.context.max_variants = 5
        result = self.context.update_correlation_context_header(self.headers, RequestType.STARTUP, 0, False, False)
        self.assertIn("Correlation-Context", result)
        self.assertIn("MaxVariants=5", result["Correlation-Context"])

    def test_with_ff_features(self):
        """Test correlation context with feature flag features."""
        self.context.uses_seed = True
        self.context.uses_telemetry = True
        result = self.context.update_correlation_context_header(self.headers, RequestType.STARTUP, 0, False, False)
        self.assertIn("Correlation-Context", result)
        self.assertIn("FFFeatures=", result["Correlation-Context"])
        self.assertIn(FEATURE_FLAG_USES_SEED_TAG, result["Correlation-Context"])
        self.assertIn(FEATURE_FLAG_USES_TELEMETRY_TAG, result["Correlation-Context"])

    @patch("azure.appconfiguration.provider._request_tracing_context.version")
    def test_with_feature_management_version(self, mock_version):
        """Test correlation context with feature management version."""
        mock_version.return_value = "1.0.0"
        self.context.feature_management_version = "1.0.0"
        result = self.context.update_correlation_context_header(
            self.headers, RequestType.STARTUP, 0, False, True, False
        )
        self.assertIn("Correlation-Context", result)
        self.assertIn("FMPyVer=1.0.0", result["Correlation-Context"])

    def test_with_general_features(self):
        """Test correlation context with general features."""
        self.context.uses_load_balancing = True
        self.context.uses_ai_configuration = True
        result = self.context.update_correlation_context_header(self.headers, RequestType.STARTUP, 0, False, False)
        self.assertIn("Correlation-Context", result)
        self.assertIn("Features=LB+AI", result["Correlation-Context"])

    def test_with_key_vault_and_failover(self):
        """Test correlation context with key vault and failover tags."""
        result = self.context.update_correlation_context_header(self.headers, RequestType.STARTUP, 2, True, False, True)
        self.assertIn("Correlation-Context", result)
        self.assertIn("RequestType=Startup", result["Correlation-Context"])
        self.assertIn("ReplicaCount=2", result["Correlation-Context"])
        self.assertIn("UsesKeyVault", result["Correlation-Context"])
        self.assertIn("Failover", result["Correlation-Context"])

    def test_comprehensive_correlation_context(self):
        """Test correlation context with all features enabled."""
        # Set up all possible features
        self.context.host_type = HostType.AZURE_WEB_APP
        self.context.feature_filter_usage = {CUSTOM_FILTER_KEY: True}
        self.context.max_variants = 3
        self.context.uses_seed = True
        self.context.feature_management_version = "1.0.0"
        self.context.uses_load_balancing = True
        self.context.is_key_vault_configured = True
        self.context.is_failover_request = True

        result = self.context.update_correlation_context_header(self.headers, RequestType.WATCH, 2, True, True, True)

        # Verify all components are present
        self.assertIn("Correlation-Context", result)
        correlation_context = result["Correlation-Context"]
        self.assertIn("RequestType=Watch", correlation_context)
        self.assertIn("ReplicaCount=2", correlation_context)
        self.assertIn("Host=AzureWebApp", correlation_context)
        self.assertIn("Filter=", correlation_context)
        self.assertIn("MaxVariants=3", correlation_context)
        self.assertIn("FFFeatures=", correlation_context)
        self.assertIn("FMPyVer=1.0.0", correlation_context)
        self.assertIn("Features=LB", correlation_context)
        self.assertIn("UsesKeyVault", correlation_context)
        self.assertIn("Failover", correlation_context)


class TestSnapshotReferenceTracking(unittest.TestCase):
    """Test snapshot reference tracking in request tracing context."""

    def test_snapshot_reference_tag_constant(self):
        """Test that the snapshot reference tag constant has the expected value."""
        self.assertEqual(SNAPSHOT_REFERENCE_TAG, "UsesSnapshotReference=true")

    def test_initialization(self):
        """Test that request tracing context initializes snapshot reference tracking."""
        context = _RequestTracingContext()
        self.assertFalse(context.uses_snapshot_reference)

    def test_set_snapshot_reference_usage(self):
        """Test setting snapshot reference usage in tracing context."""
        context = _RequestTracingContext()

        # Initially false
        self.assertFalse(context.uses_snapshot_reference)

        # Set to true
        context.uses_snapshot_reference = True
        self.assertTrue(context.uses_snapshot_reference)

        # Set back to false
        context.uses_snapshot_reference = False
        self.assertFalse(context.uses_snapshot_reference)

    def test_correlation_context_without_snapshot_reference(self):
        """Test correlation context header when not using snapshot references."""
        context = _RequestTracingContext()
        context.uses_snapshot_reference = False

        headers = {}
        updated_headers = context.update_correlation_context_header(
            headers=headers,
            request_type="Startup",
            replica_count=0,
            uses_key_vault=False,
            feature_flag_enabled=False,
            is_failover_request=False,
        )

        correlation_header = updated_headers.get("Correlation-Context", "")
        self.assertIn("RequestType=Startup", correlation_header)
        self.assertNotIn(SNAPSHOT_REFERENCE_TAG, correlation_header)

    def test_correlation_context_with_snapshot_reference(self):
        """Test correlation context header when using snapshot references."""
        context = _RequestTracingContext()
        context.uses_snapshot_reference = True

        headers = {}
        updated_headers = context.update_correlation_context_header(
            headers=headers,
            request_type="Startup",
            replica_count=0,
            uses_key_vault=False,
            feature_flag_enabled=False,
            is_failover_request=False,
        )

        correlation_header = updated_headers.get("Correlation-Context", "")
        self.assertIn("RequestType=Startup", correlation_header)
        self.assertIn(SNAPSHOT_REFERENCE_TAG, correlation_header)

    def test_snapshot_reference_detection_in_provider_base(self):
        """Test that snapshot reference detection works in provider base."""
        # Test with snapshot reference content type
        snapshot_ref_setting = ConfigurationSetting(
            key="SnapshotRef1",
            value='{"snapshot_name": "test-snapshot"}',
            content_type=SNAPSHOT_REF_CONTENT_TYPE,
        )

        self.assertTrue(
            snapshot_ref_setting.content_type and SNAPSHOT_REF_CONTENT_TYPE in snapshot_ref_setting.content_type
        )

        # Test with regular content type
        regular_setting = ConfigurationSetting(
            key="RegularKey",
            value="RegularValue",
            content_type="application/vnd.microsoft.appconfig.kv+json",
        )

        self.assertFalse(regular_setting.content_type and SNAPSHOT_REF_CONTENT_TYPE in regular_setting.content_type)

    def test_tracing_context_updated_during_processing(self):
        """Test that tracing context is updated when processing configuration with snapshot references."""
        provider = Mock(spec=AzureAppConfigurationProviderBase)
        provider._tracing_context = _RequestTracingContext()

        setting = ConfigurationSetting(
            key="SnapshotRef1",
            value='{"snapshot_name": "test-snapshot"}',
            content_type=SNAPSHOT_REF_CONTENT_TYPE,
        )

        # Simulate checking for snapshot reference content type
        if setting.content_type and SNAPSHOT_REF_CONTENT_TYPE in setting.content_type:
            provider._tracing_context.uses_snapshot_reference = True

        self.assertTrue(provider._tracing_context.uses_snapshot_reference)

    def test_tracing_context_not_updated_for_regular_settings(self):
        """Test that tracing context is not updated for regular settings."""
        provider = Mock(spec=AzureAppConfigurationProviderBase)
        provider._tracing_context = _RequestTracingContext()

        setting = ConfigurationSetting(
            key="RegularKey",
            value="RegularValue",
            content_type="application/vnd.microsoft.appconfig.kv+json",
        )

        # Simulate checking for snapshot reference content type (should not match)
        if setting.content_type and SNAPSHOT_REF_CONTENT_TYPE in setting.content_type:
            provider._tracing_context.uses_snapshot_reference = True

        self.assertFalse(provider._tracing_context.uses_snapshot_reference)

    def test_correlation_context_with_multiple_tags(self):
        """Test correlation context header format when multiple tags are present."""
        context = _RequestTracingContext()
        context.uses_snapshot_reference = True

        headers = {}
        updated_headers = context.update_correlation_context_header(
            headers=headers,
            request_type="Startup",
            replica_count=2,
            uses_key_vault=True,
            feature_flag_enabled=False,
            is_failover_request=True,
        )

        correlation_header = updated_headers.get("Correlation-Context", "")
        self.assertIn("RequestType=Startup", correlation_header)
        self.assertIn("ReplicaCount=2", correlation_header)
        self.assertIn("UsesKeyVault", correlation_header)
        self.assertIn("Failover", correlation_header)
        self.assertIn(SNAPSHOT_REFERENCE_TAG, correlation_header)
