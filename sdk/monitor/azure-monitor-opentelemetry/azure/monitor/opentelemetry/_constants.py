# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
import platform
from os import environ
from os.path import isdir
from pathlib import Path

from azure.monitor.opentelemetry.exporter._connection_string_parser import (  # pylint: disable=import-error,no-name-in-module
    ConnectionStringParser,
)

# --------------------Configuration------------------------------------------

CONNECTION_STRING_ARG = "connection_string"
DISABLE_AZURE_CORE_TRACING_ARG = "disable_azure_core_tracing"
DISABLE_LOGGING_ARG = "disable_logging"
DISABLE_METRICS_ARG = "disable_metrics"
DISABLE_TRACING_ARG = "disable_tracing"
LOGGER_NAME_ARG = "logger_name"
INSTRUMENTATION_OPTIONS_ARG = "instrumentation_options"
SAMPLING_RATIO_ARG = "sampling_ratio"


# --------------------Diagnostic/status logging------------------------------

_LOG_PATH_LINUX = "/var/log/applicationinsights"
_LOG_PATH_WINDOWS = "\\LogFiles\\ApplicationInsights"
_IS_ON_APP_SERVICE = "WEBSITE_SITE_NAME" in environ
# TODO: Add environment variable to enabled diagnostics off of App Service
_IS_DIAGNOSTICS_ENABLED = _IS_ON_APP_SERVICE
_CUSTOMER_IKEY_ENV_VAR = None
_PREVIEW_ENTRY_POINT_WARNING = "Autoinstrumentation for the Azure Monitor OpenTelemetry Distro is in preview."
logger = logging.getLogger(__name__)


# pylint: disable=global-statement
def _get_customer_ikey_from_env_var():
    global _CUSTOMER_IKEY_ENV_VAR
    if not _CUSTOMER_IKEY_ENV_VAR:
        _CUSTOMER_IKEY_ENV_VAR = "unknown"
        try:
            _CUSTOMER_IKEY_ENV_VAR = (
                ConnectionStringParser().instrumentation_key
            )
        except ValueError as e:
            logger.error("Failed to parse Instrumentation Key: %s", e)
    return _CUSTOMER_IKEY_ENV_VAR


def _get_log_path(status_log_path=False):
    system = platform.system()
    if system == "Linux":
        return _LOG_PATH_LINUX
    if system == "Windows":
        log_path = str(Path.home()) + _LOG_PATH_WINDOWS
        if status_log_path:
            return log_path + "\\status"
        return log_path
    return None


def _env_var_or_default(var_name, default_val=""):
    try:
        return environ[var_name]
    except KeyError:
        return default_val


_EXTENSION_VERSION = _env_var_or_default(
    "ApplicationInsightsAgent_EXTENSION_VERSION", "disabled"
)

# Instrumentations

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

# Autoinstrumentation

def _is_attach_enabled():
    return isdir("/agents/python/")
