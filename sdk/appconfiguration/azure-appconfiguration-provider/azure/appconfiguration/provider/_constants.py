# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

FEATURE_MANAGEMENT_KEY = "feature_management"
FEATURE_FLAG_KEY = "feature_flags"
FEATURE_FLAG_PREFIX = ".appconfig.featureflag/"

NULL_CHAR = "\0"

REQUEST_TRACING_DISABLED_ENVIRONMENT_VARIABLE = "AZURE_APP_CONFIGURATION_TRACING_DISABLED"
AzureFunctionEnvironmentVariable = "FUNCTIONS_EXTENSION_VERSION"
AzureWebAppEnvironmentVariable = "WEBSITE_SITE_NAME"
ContainerAppEnvironmentVariable = "CONTAINER_APP_NAME"
KubernetesEnvironmentVariable = "KUBERNETES_PORT"
ServiceFabricEnvironmentVariable = "Fabric_NodeName"  # cspell:disable-line

TELEMETRY_KEY = "telemetry"
METADATA_KEY = "metadata"

ALLOCATION_ID_KEY = "AllocationId"
ETAG_KEY = "ETag"
FEATURE_FLAG_REFERENCE_KEY = "FeatureFlagReference"

# Mime profiles
APP_CONFIG_AI_MIME_PROFILE = "https://azconfig.io/mime-profiles/ai/"
APP_CONFIG_AICC_MIME_PROFILE = "https://azconfig.io/mime-profiles/ai/chat-completion"

# Startup retry constants
# Default startup timeout in seconds
DEFAULT_STARTUP_TIMEOUT = 100

# Minimum and maximum backoff durations for retry after failover
MIN_BACKOFF_DURATION = 30  # seconds
MAX_BACKOFF_DURATION = 600  # 10 minutes in seconds

# Minimum backoff duration for retries that occur after the fixed backoff window during startup
MIN_STARTUP_BACKOFF_DURATION = 30  # seconds

# Jitter ratio for randomizing backoff durations (25% jitter means +/- 25% variation)
JITTER_RATIO = 0.25

# Fixed backoff intervals for startup retries: (elapsed_time_threshold, backoff_duration)
# These define the fixed backoff durations to use based on how long startup has been attempting
STARTUP_BACKOFF_INTERVALS = [
    (100, 5),  # Within first 100 seconds: 5 second backoff
    (200, 10),  # Within first 200 seconds: 10 second backoff
    (600, MIN_STARTUP_BACKOFF_DURATION),  # Within first 600 seconds: 30 second backoff
]
