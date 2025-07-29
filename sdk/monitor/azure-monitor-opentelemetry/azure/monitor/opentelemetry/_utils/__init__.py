# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
import platform
from os import environ
from pathlib import Path

from azure.monitor.opentelemetry.exporter._connection_string_parser import (  # pylint: disable=import-error,no-name-in-module
    ConnectionStringParser,
)
from azure.monitor.opentelemetry.exporter._utils import (  # pylint: disable=import-error,no-name-in-module
    _is_on_app_service,
    _is_on_aks,
    _is_on_functions,
    _is_attach_enabled,
)
from azure.monitor.opentelemetry._constants import (
    _LOG_PATH_LINUX,
    _LOG_PATH_WINDOWS,
)


logger = logging.getLogger(__name__)


# --------------------Diagnostic/status logging------------------------------

_CUSTOMER_IKEY_ENV_VAR = None


# pylint: disable=global-statement
def _get_customer_ikey_from_env_var():
    global _CUSTOMER_IKEY_ENV_VAR
    if not _CUSTOMER_IKEY_ENV_VAR:
        _CUSTOMER_IKEY_ENV_VAR = "unknown"
        try:
            _CUSTOMER_IKEY_ENV_VAR = ConnectionStringParser().instrumentation_key
        except ValueError as e:
            logger.error("Failed to parse Instrumentation Key: %s", e)  # pylint: disable=C
    return _CUSTOMER_IKEY_ENV_VAR


# TODO: Add environment variable to enable/disable diagnostics
def _is_diagnostics_enabled():
    if _is_on_functions():
        return False
    if _is_on_app_service() or _is_on_aks():
        return _is_attach_enabled()
    return False


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


_EXTENSION_VERSION = _env_var_or_default("ApplicationInsightsAgent_EXTENSION_VERSION", "disabled")
