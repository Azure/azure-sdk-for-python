# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os
from typing import Dict, Optional, List, Tuple
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
    FEATURE_FLAG_USES_TELEMETRY_TAG,
)


class HostType:
    UNIDENTIFIED = ""
    AZURE_WEB_APP = "AzureWebApp"
    AZURE_FUNCTION = "AzureFunction"
    CONTAINER_APP = "ContainerApp"
    KUBERNETES = "Kubernetes"
    SERVICE_FABRIC = "ServiceFabric"


class RequestType:
    STARTUP = "Startup"
    WATCH = "Watch"


Delimiter = "+"


class _RequestTracingContext:  # pylint: disable=too-many-instance-attributes
    """
    Encapsulates request tracing and telemetry configuration values.
    """

    def __init__(self, load_balancing_enabled: bool = False) -> None:
        # Main feature tracking properties
        self.uses_load_balancing = load_balancing_enabled
        self.uses_ai_configuration = False
        self.uses_aicc_configuration = False  # AI Chat Completion
        self.uses_telemetry = False
        self.uses_seed = False
        self.max_variants: Optional[int] = None
        self.feature_filter_usage: Dict[str, bool] = {}
        self.is_key_vault_configured: bool = False
        self.replica_count: int = 0
        self.is_failover_request: bool = False

        # Host and environment detection properties
        self.host_type: str = _RequestTracingContext.get_host_type()

        # Version tracking
        self.feature_management_version: Optional[str] = None

    def update_max_variants(self, size: int) -> None:
        """
        Update max_variants if the new size is larger.

        :param size: size of variant
        :type size: int
        """
        if self.max_variants is None or size > self.max_variants:
            self.max_variants = size

    def _get_features_string(self) -> str:
        """
        Generate the features string for correlation context.

        :return: A string containing features used separated by delimiters.
        :rtype: str
        """
        features_list = []

        if self.uses_load_balancing:
            features_list.append("LB")
        if self.uses_ai_configuration:
            features_list.append("AI")
        if self.uses_aicc_configuration:
            features_list.append("AICC")
        if self.get_assembly_version("azure-ai-projects"):
            features_list.append("USE_AI")

        return Delimiter.join(features_list)

    def _create_features_string(self) -> str:
        """
        Generate the features string for feature flag usage tracking.

        :return: A string containing feature flag usage tags separated by delimiters.
        :rtype: str
        """
        features_list = []

        if self.uses_seed:
            features_list.append(FEATURE_FLAG_USES_SEED_TAG)

        if self.uses_telemetry:
            features_list.append(FEATURE_FLAG_USES_TELEMETRY_TAG)

        return Delimiter.join(features_list)

    @staticmethod
    def get_host_type() -> str:
        """
        Detect the host environment type based on environment variables.

        :return: The detected host type.
        :rtype: str
        """
        if os.environ.get(AzureFunctionEnvironmentVariable):
            return HostType.AZURE_FUNCTION
        if os.environ.get(AzureWebAppEnvironmentVariable):
            return HostType.AZURE_WEB_APP
        if os.environ.get(ContainerAppEnvironmentVariable):
            return HostType.CONTAINER_APP
        if os.environ.get(KubernetesEnvironmentVariable):
            return HostType.KUBERNETES
        if os.environ.get(ServiceFabricEnvironmentVariable):
            return HostType.SERVICE_FABRIC

        return HostType.UNIDENTIFIED

    @staticmethod
    def get_assembly_version(package_name: str) -> Optional[str]:
        """
        Get the version of a Python package.

        :param package_name: The name of the package to get version for.
        :type package_name: str
        :return: Package version string or None if not found.
        :rtype: Optional[str]
        """
        if not package_name:
            return None

        try:
            return version(package_name)
        except PackageNotFoundError:
            pass

        return None

    def reset_ai_configuration_tracing(self) -> None:
        """
        Reset AI configuration tracing flags.
        """
        self.uses_ai_configuration = False
        self.uses_aicc_configuration = False

    def update_ai_configuration_tracing(self, content_type: Optional[str]) -> None:
        """
        Update AI configuration tracing based on content type.

        :param content_type: The content type to analyze.
        :type content_type: Optional[str]
        """
        if not content_type or self.uses_aicc_configuration:
            return

        # Check for AI mime profiles in content type
        if "https://azconfig.io/mime-profiles/ai" in content_type:
            self.uses_ai_configuration = True
            if "chat-completion" in content_type:
                self.uses_aicc_configuration = True

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
        if os.environ.get(REQUEST_TRACING_DISABLED_ENVIRONMENT_VARIABLE, "").lower() == "true":
            return headers

        # Update instance properties for the correlation context
        self.replica_count = replica_count
        self.is_key_vault_configured = uses_key_vault
        self.is_failover_request = is_failover_request

        # Update feature management version if needed and feature flags are enabled
        if feature_flag_enabled and not self.feature_management_version:
            self.feature_management_version = self.get_assembly_version("featuremanagement")

        # Key-value pairs for the correlation context
        key_values: List[Tuple[str, str]] = []
        tags: List[str] = []

        # Add request type
        key_values.append(("RequestType", request_type))

        # Add replica count if configured
        if self.replica_count > 0:
            key_values.append(("ReplicaCount", str(self.replica_count)))

        # Add host type if identified
        if self.host_type != HostType.UNIDENTIFIED:
            key_values.append(("Host", self.host_type))

        # Add feature filter information
        if len(self.feature_filter_usage) > 0:
            filters_string = self._create_filters_string()
            if filters_string:
                key_values.append(("Filter", filters_string))

        # Add max variants if present
        if self.max_variants and self.max_variants > 0:
            key_values.append(("MaxVariants", str(self.max_variants)))

        # Add feature flag features if present
        if self.uses_seed or self.uses_telemetry:
            ff_features_string = self._create_features_string()
            if ff_features_string:
                key_values.append(("FFFeatures", ff_features_string))

        # Add version information
        if self.feature_management_version:
            key_values.append(("FMPyVer", self.feature_management_version))

        # Add general features if present
        if self.uses_load_balancing or self.uses_ai_configuration or self.uses_aicc_configuration:
            features_string = self._get_features_string()
            if features_string:
                key_values.append(("Features", features_string))

        # Add tags
        if self.is_key_vault_configured:
            tags.append("UsesKeyVault")

        if self.is_failover_request:
            tags.append("Failover")

        # Build the correlation context string
        context_parts: List[str] = []

        # Add key-value pairs
        for key, value in key_values:
            context_parts.append(f"{key}={value}")

        # Add tags
        context_parts.extend(tags)

        correlation_context = ",".join(context_parts)

        if correlation_context:
            headers["Correlation-Context"] = correlation_context

        return headers

    def _create_filters_string(self) -> str:
        """
        Create a string representing the feature filters in use.

        :return: String of filter names separated by delimiters.
        :rtype: str
        """
        filters: List[str] = []

        if CUSTOM_FILTER_KEY in self.feature_filter_usage:
            filters.append(CUSTOM_FILTER_KEY)
        if PERCENTAGE_FILTER_KEY in self.feature_filter_usage:
            filters.append(PERCENTAGE_FILTER_KEY)
        if TIME_WINDOW_FILTER_KEY in self.feature_filter_usage:
            filters.append(TIME_WINDOW_FILTER_KEY)
        if TARGETING_FILTER_KEY in self.feature_filter_usage:
            filters.append(TARGETING_FILTER_KEY)

        return Delimiter.join(filters)

    def update_feature_filter_telemetry(self, feature_flag) -> None:
        """
        Track feature filter usage for App Configuration telemetry.

        :param feature_flag: The feature flag to analyze for filter usage.
        :type feature_flag: FeatureFlagConfigurationSetting
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
