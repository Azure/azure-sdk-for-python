# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os
from typing import Dict, Optional
from importlib.metadata import version, PackageNotFoundError
from ._constants import (
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
    PERCENTAGE_FILTER_NAMES,
    TIME_WINDOW_FILTER_NAMES,
    TARGETING_FILTER_NAMES,
    FEATURE_FLAG_USES_SEED_TAG,
    FEATURE_FLAG_USES_VARIANT_CONFIGURATION_REFERENCE_TAG,
    FEATURE_FLAG_USES_TELEMETRY_TAG,
)

Delimiter = "+"

class _RequestTracingContext:
    """
    Encapsulates request tracing and telemetry configuration values.
    """

    def __init__(self, load_balancing_enabled: bool = False) -> None:
        self.uses_load_balancing = load_balancing_enabled
        self.uses_ai_configuration = False
        self.uses_aicc_configuration = False  # AI Chat Completion
        self.uses_telemetry = False
        self.uses_seed = False
        self.uses_variant_configuration_reference = False
        self.max_variants: Optional[int] = None
        self.feature_filter_usage: Dict[str, bool] = {}

    def update_max_variants(self, size: int) -> None:
        """Update max_variants if the new size is larger."""
        if self.max_variants is None or size > self.max_variants:
            self.max_variants = size

    def get_features_string(self) -> str:
        """Generate the features string for correlation context."""
        features_list = []
        
        if self.uses_load_balancing:
            features_list.append("LB")
        if self.uses_ai_configuration:
            features_list.append("AI")
        if self.uses_aicc_configuration:
            features_list.append("AICC")
        
        return Delimiter.join(features_list)

    def create_features_string(self) -> str:
        """
        Generate the features string for feature flag usage tracking.
        
        :return: A string containing feature flag usage tags separated by delimiters.
        :rtype: str
        """
        features_list = []

        if self.uses_seed:
            features_list.append(FEATURE_FLAG_USES_SEED_TAG)

        if self.uses_variant_configuration_reference:
            features_list.append(FEATURE_FLAG_USES_VARIANT_CONFIGURATION_REFERENCE_TAG)

        if self.uses_telemetry:
            features_list.append(FEATURE_FLAG_USES_TELEMETRY_TAG)

        return Delimiter.join(features_list)
    


    def update_correlation_context_header(
        self,
        headers: Dict[str, str],
        request_type: str,
        replica_count: int,
        uses_key_vault: bool,
        feature_flag_enabled: bool,
        is_failover_request: bool = False,
    ) -> Dict[str, str]:
        """
        Update the correlation context header with telemetry information.

        :param headers: The headers dictionary to update.
        :type headers: Dict[str, str]
        :param request_type: The type of request (e.g., "Startup", "Watch").
        :type request_type: str
        :param replica_count: The number of replica endpoints.
        :type replica_count: int
        :param uses_key_vault: Whether this request uses Key Vault.
        :type uses_key_vault: bool
        :param feature_flag_enabled: Whether feature flags are enabled.
        :type feature_flag_enabled: bool
        :param is_failover_request: Whether this is a failover request.
        :type is_failover_request: bool
        :return: The updated headers dictionary.
        :rtype: Dict[str, str]
        """
        if os.environ.get(REQUEST_TRACING_DISABLED_ENVIRONMENT_VARIABLE, default="").lower() == "true":
            return headers
        correlation_context = f"RequestType={request_type}"

        if len(self.feature_filter_usage) > 0:
            filters_used = ""
            if CUSTOM_FILTER_KEY in self.feature_filter_usage:
                filters_used = CUSTOM_FILTER_KEY
            if PERCENTAGE_FILTER_KEY in self.feature_filter_usage:
                filters_used += ("+" if filters_used else "") + PERCENTAGE_FILTER_KEY
            if TIME_WINDOW_FILTER_KEY in self.feature_filter_usage:
                filters_used += ("+" if filters_used else "") + TIME_WINDOW_FILTER_KEY
            if TARGETING_FILTER_KEY in self.feature_filter_usage:
                filters_used += ("+" if filters_used else "") + TARGETING_FILTER_KEY
            correlation_context += f",Filters={filters_used}"

        correlation_context += self._get_feature_flags_version(feature_flag_enabled)

        if uses_key_vault:
            correlation_context += ",UsesKeyVault"
        host_type = ""
        if AzureFunctionEnvironmentVariable in os.environ:
            host_type = "AzureFunction"
        elif AzureWebAppEnvironmentVariable in os.environ:
            host_type = "AzureWebApp"
        elif ContainerAppEnvironmentVariable in os.environ:
            host_type = "ContainerApp"
        elif KubernetesEnvironmentVariable in os.environ:
            host_type = "Kubernetes"
        elif ServiceFabricEnvironmentVariable in os.environ:
            host_type = "ServiceFabric"
        if host_type:
            correlation_context += f",Host={host_type}"

        if replica_count > 0:
            correlation_context += f",ReplicaCount={replica_count}"

        if is_failover_request:
            correlation_context += ",Failover"

        features = self.get_features_string()
        if features:
            correlation_context += f",Features={features}"

        headers["Correlation-Context"] = correlation_context
        return headers

    def update_feature_filter_telemetry(self, feature_flag) -> None:
        """
        Track feature filter usage for App Configuration telemetry.

        :param feature_flag: The feature flag to analyze for filter usage.
        """
        # Constants are already imported at module level
        
        if feature_flag.filters:
            for filter in feature_flag.filters:
                if filter.get("name") in PERCENTAGE_FILTER_NAMES:
                    self.feature_filter_usage[PERCENTAGE_FILTER_KEY] = True
                elif filter.get("name") in TIME_WINDOW_FILTER_NAMES:
                    self.feature_filter_usage[TIME_WINDOW_FILTER_KEY] = True
                elif filter.get("name") in TARGETING_FILTER_NAMES:
                    self.feature_filter_usage[TARGETING_FILTER_KEY] = True
                else:
                    self.feature_filter_usage[CUSTOM_FILTER_KEY] = True

    def reset_feature_filter_usage(self) -> None:
        """Reset the feature filter usage tracking."""
        self.feature_filter_usage = {}

    def _get_feature_flags_version(self, feature_flag_enabled: bool) -> str:
        """Get feature flags version string for correlation context."""
        if not feature_flag_enabled:
            return ""
        package_name = "featuremanagement"
        try:
            feature_management_version = version(package_name)
            return f",FMPyVer={feature_management_version}"
        except PackageNotFoundError:
            pass
        return ""