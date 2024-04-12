# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.monitor.opentelemetry.exporter._constants import (  # pylint: disable=import-error,no-name-in-module
    _AZURE_MONITOR_DISTRO_VERSION_ARG,
)

# --------------------Configuration------------------------------------------

CONNECTION_STRING_ARG = "connection_string"
DISABLE_AZURE_CORE_TRACING_ARG = "disable_azure_core_tracing"
DISABLE_LOGGING_ARG = "disable_logging"
DISABLE_METRICS_ARG = "disable_metrics"
DISABLE_TRACING_ARG = "disable_tracing"
DISTRO_VERSION_ARG = _AZURE_MONITOR_DISTRO_VERSION_ARG
LOGGER_NAME_ARG = "logger_name"
INSTRUMENTATION_OPTIONS_ARG = "instrumentation_options"
RESOURCE_ARG = "resource"
SAMPLING_RATIO_ARG = "sampling_ratio"
SPAN_PROCESSORS_ARG = "span_processors"


# --------------------Diagnostic/status logging------------------------------

_LOG_PATH_LINUX = "/var/log/applicationinsights"
_LOG_PATH_WINDOWS = "\\LogFiles\\ApplicationInsights"
_PREVIEW_ENTRY_POINT_WARNING = "Autoinstrumentation for the Azure Monitor OpenTelemetry Distro is in preview."


# --------------------Instrumentations------------------------------

# Opt-out
_AZURE_SDK_INSTRUMENTATION_NAME = "azure_sdk"
_FULLY_SUPPORTED_INSTRUMENTED_LIBRARIES = (
    _AZURE_SDK_INSTRUMENTATION_NAME,
    "django",
    "fastapi",
    "flask",
    "psycopg2",
    "requests",
    "urllib",
    "urllib3",
)
# Opt-in
_PREVIEW_INSTRUMENTED_LIBRARIES = ()
_ALL_SUPPORTED_INSTRUMENTED_LIBRARIES = _FULLY_SUPPORTED_INSTRUMENTED_LIBRARIES + _PREVIEW_INSTRUMENTED_LIBRARIES

_AZURE_APP_SERVICE_RESOURCE_DETECTOR_NAME = "azure_app_service"
_AZURE_VM_RESOURCE_DETECTOR_NAME = "azure_vm"
