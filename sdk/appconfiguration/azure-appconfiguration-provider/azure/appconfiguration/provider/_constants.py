# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------


# ------------------------------------------------------------------------
# Feature Management Constants
# ------------------------------------------------------------------------
FEATURE_MANAGEMENT_KEY = "feature_management"
FEATURE_FLAG_KEY = "feature_flags"
FEATURE_FLAG_PREFIX = ".appconfig.featureflag/"
FEATURE_FLAG_REFERENCE_KEY = "FeatureFlagReference"
ALLOCATION_ID_KEY = "AllocationId"
ETAG_KEY = "ETag"

# ------------------------------------------------------------------------
# Environment Variable Constants
# ------------------------------------------------------------------------
REQUEST_TRACING_DISABLED_ENVIRONMENT_VARIABLE = "AZURE_APP_CONFIGURATION_TRACING_DISABLED"
AzureFunctionEnvironmentVariable = "FUNCTIONS_EXTENSION_VERSION"
AzureWebAppEnvironmentVariable = "WEBSITE_SITE_NAME"
ContainerAppEnvironmentVariable = "CONTAINER_APP_NAME"
KubernetesEnvironmentVariable = "KUBERNETES_PORT"
ServiceFabricEnvironmentVariable = "Fabric_NodeName"  # cspell:disable-line

# ------------------------------------------------------------------------
# Telemetry and Tracing Constants
# ------------------------------------------------------------------------
TELEMETRY_KEY = "telemetry"
METADATA_KEY = "metadata"
SNAPSHOT_REFERENCE_TAG = "SnapshotRef"

# ------------------------------------------------------------------------
# Content Type and Mime Profile Constants
# ------------------------------------------------------------------------
APP_CONFIG_AI_MIME_PROFILE = "https://azconfig.io/mime-profiles/ai/"
APP_CONFIG_AICC_MIME_PROFILE = "https://azconfig.io/mime-profiles/ai/chat-completion"
SNAPSHOT_REF_CONTENT_TYPE = 'application/json; profile="https://azconfig.io/mime-profiles/snapshot-ref"; charset=utf-8'

# ------------------------------------------------------------------------
# Snapshot Reference Constants
# ------------------------------------------------------------------------
SNAPSHOT_NAME_FIELD = "snapshot_name"

# ------------------------------------------------------------------------
# Miscellaneous Constants
# ------------------------------------------------------------------------
NULL_CHAR = "\0"
