# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
import threading
from os import makedirs
from os.path import exists, join

from azure.monitor.opentelemetry._utils import (
    _EXTENSION_VERSION,
    _IS_DIAGNOSTICS_ENABLED,
    _env_var_or_default,
    _get_customer_ikey_from_env_var,
    _get_log_path,
)
from azure.monitor.opentelemetry._version import VERSION

_DIAGNOSTIC_LOGGER_FILE_NAME = "applicationinsights-extension.log"
_SITE_NAME = _env_var_or_default("WEBSITE_SITE_NAME")
_SUBSCRIPTION_ID_ENV_VAR = _env_var_or_default("WEBSITE_OWNER_NAME")
_SUBSCRIPTION_ID = (
    _SUBSCRIPTION_ID_ENV_VAR.split("+")[0] if _SUBSCRIPTION_ID_ENV_VAR else None
)
_logger = logging.getLogger(__name__)
_logger.propagate = False
_logger.setLevel(logging.INFO)
_DIAGNOSTIC_LOG_PATH = _get_log_path()
_DISTRO_DETECTS_ATTACH = "4100"
_ATTACH_SUCCESS_DISTRO = "4200"
_ATTACH_SUCCESS_CONFIGURATOR = "4201"
_ATTACH_FAILURE_DISTRO = "4400"
_ATTACH_FAILURE_CONFIGURATOR = "4401"
_ATTACH_DETECTS_SDK = "4402"


class AzureDiagnosticLogging:
    _initialized = False
    _lock = threading.Lock()

    @classmethod
    def _initialize(cls):
        with AzureDiagnosticLogging._lock:
            if not AzureDiagnosticLogging._initialized:
                if _IS_DIAGNOSTICS_ENABLED and _DIAGNOSTIC_LOG_PATH:
                    log_format = (
                        "{"
                        + '"time":"%(asctime)s.%(msecs)03d", '
                        + '"level":"%(levelname)s", '
                        + '"logger":"%(name)s", '
                        + '"message":"%(message)s", '
                        + '"properties":{'
                        + '"operation":"Startup", '
                        + f'"siteName":"{_SITE_NAME}", '
                        + f'"ikey":"{_get_customer_ikey_from_env_var()}", '
                        + f'"extensionVersion":"{_EXTENSION_VERSION}", '
                        + f'"sdkVersion":"{VERSION}", '
                        + f'"subscriptionId":"{_SUBSCRIPTION_ID}", '
                        + '"msgId":"%(msgId)s", '
                        + '"language":"python"'
                        + "}"
                        + "}"
                    )
                    if not exists(_DIAGNOSTIC_LOG_PATH):
                        makedirs(_DIAGNOSTIC_LOG_PATH)
                    f_handler = logging.FileHandler(
                        join(
                            _DIAGNOSTIC_LOG_PATH, _DIAGNOSTIC_LOGGER_FILE_NAME
                        )
                    )
                    formatter = logging.Formatter(
                        fmt=log_format, datefmt="%Y-%m-%dT%H:%M:%S"
                    )
                    f_handler.setFormatter(formatter)
                    _logger.addHandler(f_handler)
                    AzureDiagnosticLogging._initialized = True

    @classmethod
    def info(cls, message: str, message_id: str):
        AzureDiagnosticLogging._initialize()
        _logger.info(message, extra={'msgId': message_id})

    @classmethod
    def warning(cls, message: str, message_id: str):
        AzureDiagnosticLogging._initialize()
        _logger.warning(message, extra={'msgId': message_id})

    @classmethod
    def error(cls, message: str, message_id: str):
        AzureDiagnosticLogging._initialize()
        _logger.error(message, extra={'msgId': message_id})
