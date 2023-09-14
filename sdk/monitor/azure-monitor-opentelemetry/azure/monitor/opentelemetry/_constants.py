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
DISABLED_INSTRUMENTATIONS_ARG = "disabled_instrumentations"
SAMPLING_RATIO_ARG = "sampling_ratio"


# --------------------Diagnostic/status logging------------------------------

_LOG_PATH_LINUX = "/var/log/applicationinsights"
_LOG_PATH_WINDOWS = "\\LogFiles\\ApplicationInsights"
_IS_ON_APP_SERVICE = "WEBSITE_SITE_NAME" in environ
# TODO: Add environment variable to enabled diagnostics off of App Service
_IS_DIAGNOSTICS_ENABLED = _IS_ON_APP_SERVICE
# TODO: Enabled when duplicate logging issue is solved
# _EXPORTER_DIAGNOSTICS_ENABLED_ENV_VAR = (
#     "AZURE_MONITOR_OPENTELEMETRY_DISTRO_ENABLE_EXPORTER_DIAGNOSTICS"
# )
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


# TODO: Enabled when duplicate logging issue is solved
# def _is_exporter_diagnostics_enabled():
#     return (
#         _EXPORTER_DIAGNOSTICS_ENABLED_ENV_VAR in environ
#         and environ[_EXPORTER_DIAGNOSTICS_ENABLED_ENV_VAR] == "True"
#     )


_EXTENSION_VERSION = _env_var_or_default(
    "ApplicationInsightsAgent_EXTENSION_VERSION", "disabled"
)
# TODO: Enabled when duplicate logging issue is solved
# _EXPORTER_DIAGNOSTICS_ENABLED = _is_exporter_diagnostics_enabled()


def _is_attach_enabled():
    return isdir("/agents/python/")
