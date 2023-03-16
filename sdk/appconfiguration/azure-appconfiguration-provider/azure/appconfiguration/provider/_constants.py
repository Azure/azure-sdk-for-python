# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

FEATURE_MANAGEMENT_KEY = "FeatureManagementFeatureFlags"
FEATURE_FLAG_PREFIX = ".appconfig.featureflag/"

EMPTY_LABEL = "\0"

RequestTracingDisabledEnvironmentVariable = "AZURE_APP_CONFIGURATION_TRACING_DISABLED"
AzureFunctionEnvironmentVariable = "FUNCTIONS_EXTENSION_VERSION"
AzureWebAppEnvironmentVariable = "WEBSITE_SITE_NAME"
ContainerAppEnvironmentVariable = "CONTAINER_APP_NAME"
KubernetesEnvironmentVariable = "KUBERNETES_PORT"
ServiceFabricEnvironmentVariable = "Fabric_NodeName"  # cspell:disable-line
