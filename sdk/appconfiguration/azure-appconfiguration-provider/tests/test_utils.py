# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import unittest
import os
import datetime
from unittest.mock import patch
from importlib.metadata import PackageNotFoundError

from azure.appconfiguration.provider._utils import (
    delay_failure,
    is_json_content_type,
    sdk_allowed_kwargs,
    update_correlation_context_header,
    _uses_feature_flags,
)
from azure.appconfiguration.provider._constants import (
    REQUEST_TRACING_DISABLED_ENVIRONMENT_VARIABLE,
    ServiceFabricEnvironmentVariable,
    AzureFunctionEnvironmentVariable,
    AzureWebAppEnvironmentVariable,
    ContainerAppEnvironmentVariable,
    KubernetesEnvironmentVariable,
    CUSTOM_FILTER_KEY,
    PERCENTAGE_FILTER_KEY,
    TIME_WINDOW_FILTER_KEY,
    TARGETING_FILTER_KEY,
)


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


class TestUpdateCorrelationContextHeader(unittest.TestCase):
    """Test the update_correlation_context_header function."""

    def setUp(self):
        """Set up test environment."""
        self.headers = {}
        self.request_type = "Test"
        self.replica_count = 2
        self.uses_feature_flags = True
        self.feature_filters_used = {}
        self.uses_key_vault = False
        self.uses_load_balancing = False
        self.is_failover_request = False
        self.uses_ai_configuration = False
        self.uses_aicc_configuration = False

    def test_disabled_tracing_returns_unchanged_headers(self):
        """Test that tracing disabled returns headers unchanged."""
        with patch.dict(os.environ, {REQUEST_TRACING_DISABLED_ENVIRONMENT_VARIABLE: "true"}):
            result = update_correlation_context_header(
                self.headers,
                self.request_type,
                self.replica_count,
                self.uses_feature_flags,
                self.feature_filters_used,
                self.uses_key_vault,
                self.uses_load_balancing,
                self.is_failover_request,
                self.uses_ai_configuration,
                self.uses_aicc_configuration,
            )
            self.assertEqual(result, {})

    def test_basic_correlation_context(self):
        """Test basic correlation context generation."""
        result = update_correlation_context_header(
            self.headers,
            self.request_type,
            self.replica_count,
            self.uses_feature_flags,
            self.feature_filters_used,
            self.uses_key_vault,
            self.uses_load_balancing,
            self.is_failover_request,
            self.uses_ai_configuration,
            self.uses_aicc_configuration,
        )
        self.assertIn("Correlation-Context", result)
        self.assertIn("RequestType=Test", result["Correlation-Context"])
        self.assertIn("ReplicaCount=2", result["Correlation-Context"])

    def test_feature_filters_in_correlation_context(self):
        """Test feature filters are included in correlation context."""
        feature_filters_used = {
            CUSTOM_FILTER_KEY: True,
            PERCENTAGE_FILTER_KEY: True,
            TIME_WINDOW_FILTER_KEY: True,
            TARGETING_FILTER_KEY: True,
        }
        result = update_correlation_context_header(
            self.headers,
            self.request_type,
            self.replica_count,
            self.uses_feature_flags,
            feature_filters_used,
            self.uses_key_vault,
            self.uses_load_balancing,
            self.is_failover_request,
            self.uses_ai_configuration,
            self.uses_aicc_configuration,
        )
        context = result["Correlation-Context"]
        self.assertIn("Filters=", context)
        self.assertIn(CUSTOM_FILTER_KEY, context)
        self.assertIn(PERCENTAGE_FILTER_KEY, context)
        self.assertIn(TIME_WINDOW_FILTER_KEY, context)
        self.assertIn(TARGETING_FILTER_KEY, context)

    def test_host_type_detection(self):
        """Test host type detection in various environments."""
        test_cases = [
            (AzureFunctionEnvironmentVariable, "AzureFunction"),
            (AzureWebAppEnvironmentVariable, "AzureWebApp"),
            (ContainerAppEnvironmentVariable, "ContainerApp"),
            (KubernetesEnvironmentVariable, "Kubernetes"),
            (ServiceFabricEnvironmentVariable, "ServiceFabric"),
        ]

        for env_var, expected_host in test_cases:
            with patch.dict(os.environ, {env_var: "test_value"}, clear=True):
                result = update_correlation_context_header(
                    {},
                    self.request_type,
                    self.replica_count,
                    self.uses_feature_flags,
                    self.feature_filters_used,
                    self.uses_key_vault,
                    self.uses_load_balancing,
                    self.is_failover_request,
                    self.uses_ai_configuration,
                    self.uses_aicc_configuration,
                )
                self.assertIn(f"Host={expected_host}", result["Correlation-Context"])

    def test_features_in_correlation_context(self):
        """Test that features are included in correlation context."""
        result = update_correlation_context_header(
            self.headers,
            self.request_type,
            self.replica_count,
            self.uses_feature_flags,
            self.feature_filters_used,
            self.uses_key_vault,
            True,
            self.is_failover_request,
            True,
            True,
        )
        context = result["Correlation-Context"]
        self.assertIn("Features=LB+AI+AICC", context)

    def test_failover_request_in_correlation_context(self):
        """Test that failover request is included in correlation context."""
        result = update_correlation_context_header(
            self.headers,
            self.request_type,
            self.replica_count,
            self.uses_feature_flags,
            self.feature_filters_used,
            self.uses_key_vault,
            self.uses_load_balancing,
            True,
            self.uses_ai_configuration,
            self.uses_aicc_configuration,
        )
        self.assertIn("Failover", result["Correlation-Context"])


class TestUsesFeatureFlags(unittest.TestCase):
    """Test the _uses_feature_flags function."""

    def test_no_feature_flags_returns_empty(self):
        """Test that no feature flags returns empty string."""
        result = _uses_feature_flags(False)
        self.assertEqual(result, "")

    @patch("azure.appconfiguration.provider._utils.version")
    def test_feature_flags_with_version(self, mock_version):
        """Test that feature flags with version returns version string."""
        mock_version.return_value = "1.0.0"
        result = _uses_feature_flags(True)
        self.assertEqual(result, ",FMPyVer=1.0.0")

    @patch("azure.appconfiguration.provider._utils.version")
    def test_feature_flags_without_package(self, mock_version):
        """Test that feature flags without package returns empty string."""
        mock_version.side_effect = PackageNotFoundError()
        result = _uses_feature_flags(True)
        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()
