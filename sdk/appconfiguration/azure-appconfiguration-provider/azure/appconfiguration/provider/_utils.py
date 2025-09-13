# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os
import time
import datetime
from importlib.metadata import version, PackageNotFoundError
from typing import Dict
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
)


def delay_failure(start_time: datetime.datetime) -> None:
    """
    We want to make sure we are up a minimum amount of time before we kill the process.
    Otherwise, we could get stuck in a quick restart loop.

    :param start_time: The time when the process started.
    :type start_time: datetime.datetime
    """
    min_uptime = 5
    min_time = datetime.timedelta(seconds=min_uptime)
    current_time = datetime.datetime.now()
    if current_time - start_time < min_time:
        time.sleep((min_time - (current_time - start_time)).total_seconds())


def is_json_content_type(content_type: str) -> bool:
    """
    Determines if the given content type indicates JSON content.

    :param content_type: The content type string to check.
    :type content_type: str
    :return: True if the content type indicates JSON, False otherwise.
    :rtype: bool
    """
    if not content_type:
        return False

    content_type = content_type.strip().lower()
    mime_type = content_type.split(";")[0].strip()

    type_parts = mime_type.split("/")
    if len(type_parts) != 2:
        return False

    (main_type, sub_type) = type_parts
    if main_type != "application":
        return False

    sub_types = sub_type.split("+")
    if "json" in sub_types:
        return True

    return False


def sdk_allowed_kwargs(kwargs):
    """
    Filters kwargs to only include those allowed by the Azure SDK.

    :param kwargs: The keyword arguments to filter.
    :type kwargs: Dict[str, Any]
    :return: A dictionary containing only allowed keyword arguments.
    :rtype: Dict[str, Any]
    """
    allowed_kwargs = [
        "headers",
        "request_id",
        "user_agent",
        "logging_enable",
        "logger",
        "response_encoding",
        "raw_request_hook",
        "raw_response_hook",
        "network_span_namer",
        "tracing_attributes",
        "permit_redirects",
        "redirect_max",
        "retry_total",
        "retry_connect",
        "retry_read",
        "retry_status",
        "retry_backoff_factor",
        "retry_backoff_max",
        "retry_mode",
        "timeout",
        "connection_timeout",
        "read_timeout",
        "connection_verify",
        "connection_cert",
        "proxies",
        "cookies",
        "connection_data_block_size",
    ]
    return {k: v for k, v in kwargs.items() if k in allowed_kwargs}


def update_correlation_context_header(
    headers,
    request_type,
    replica_count,
    uses_feature_flags,
    feature_filters_used,
    uses_key_vault,
    uses_load_balancing,
    is_failover_request,
    uses_ai_configuration,
    uses_aicc_configuration,
) -> Dict[str, str]:
    """
    Updates the correlation context header with telemetry information.

    :param headers: The headers dictionary to update.
    :type headers: Dict[str, str]
    :param request_type: The type of request being made.
    :type request_type: str
    :param replica_count: The number of replicas.
    :type replica_count: int
    :param uses_feature_flags: Whether feature flags are being used.
    :type uses_feature_flags: bool
    :param feature_filters_used: Dictionary of feature filters being used.
    :type feature_filters_used: Dict[str, bool]
    :param uses_key_vault: Whether Key Vault is being used.
    :type uses_key_vault: bool
    :param uses_load_balancing: Whether load balancing is enabled.
    :type uses_load_balancing: bool
    :param is_failover_request: Whether this is a failover request.
    :type is_failover_request: bool
    :param uses_ai_configuration: Whether AI configuration is being used.
    :type uses_ai_configuration: bool
    :param uses_aicc_configuration: Whether AI Chat Completion configuration is being used.
    :type uses_aicc_configuration: bool
    :return: The updated headers dictionary.
    :rtype: Dict[str, str]
    """
    if os.environ.get(REQUEST_TRACING_DISABLED_ENVIRONMENT_VARIABLE, default="").lower() == "true":
        return headers
    correlation_context = "RequestType=" + request_type

    if len(feature_filters_used) > 0:
        filters_used = ""
        if CUSTOM_FILTER_KEY in feature_filters_used:
            filters_used = CUSTOM_FILTER_KEY
        if PERCENTAGE_FILTER_KEY in feature_filters_used:
            filters_used += ("+" if filters_used else "") + PERCENTAGE_FILTER_KEY
        if TIME_WINDOW_FILTER_KEY in feature_filters_used:
            filters_used += ("+" if filters_used else "") + TIME_WINDOW_FILTER_KEY
        if TARGETING_FILTER_KEY in feature_filters_used:
            filters_used += ("+" if filters_used else "") + TARGETING_FILTER_KEY
        correlation_context += ",Filters=" + filters_used

    correlation_context += _uses_feature_flags(uses_feature_flags)

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
        correlation_context += ",Host=" + host_type

    if replica_count > 0:
        correlation_context += ",ReplicaCount=" + str(replica_count)

    if is_failover_request:
        correlation_context += ",Failover"

    features = ""

    if uses_load_balancing:
        features += "LB+"

    if uses_ai_configuration:
        features += "AI+"

    if uses_aicc_configuration:
        features += "AICC+"

    if features:
        correlation_context += ",Features=" + features[:-1]

    headers["Correlation-Context"] = correlation_context
    return headers


def _uses_feature_flags(uses_feature_flags):
    """
    Determines the feature management version if feature flags are being used.

    :param uses_feature_flags: Whether feature flags are being used.
    :type uses_feature_flags: bool
    :return: Version string for feature management or empty string.
    :rtype: str
    """
    if not uses_feature_flags:
        return ""
    package_name = "featuremanagement"
    try:
        feature_management_version = version(package_name)
        if feature_management_version:
            return ",FMPyVer=" + feature_management_version
    except PackageNotFoundError:
        pass
    return ""
