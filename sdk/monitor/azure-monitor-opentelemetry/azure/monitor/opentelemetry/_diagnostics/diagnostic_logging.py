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
    _env_var_or_default,
    _get_customer_ikey_from_env_var,
    _get_log_path,
    _is_diagnostics_enabled,
)
from azure.monitor.opentelemetry._version import VERSION

# This logger is used for logging messages about the setup of AzureDiagnosticLogging
_logger = logging.getLogger("azure.monitor.opentelemetry._diagnostics")

_DIAGNOSTIC_LOGGER_FILE_NAME = "applicationinsights-extension.log"
_SITE_NAME = _env_var_or_default("WEBSITE_SITE_NAME")
_SUBSCRIPTION_ID_ENV_VAR = _env_var_or_default("WEBSITE_OWNER_NAME")
_SUBSCRIPTION_ID = _SUBSCRIPTION_ID_ENV_VAR.split("+")[0] if _SUBSCRIPTION_ID_ENV_VAR else None
# This logger is used for logging the diagnostic logs themselves to a log file
_diagnostic_file_logger = logging.getLogger(__name__)
_diagnostic_file_logger.propagate = False
_diagnostic_file_logger.setLevel(logging.DEBUG)
_DIAGNOSTIC_LOG_PATH = _get_log_path()

_DISTRO_DETECTS_ATTACH = "4100"
_INSTRUMENTATION_SKIPPED = "4101"
_INFO = "4102"

_ATTACH_SUCCESS_DISTRO = "4200"
_ATTACH_SUCCESS_CONFIGURATOR = "4201"
_INSTRUMENTATION_SUCCEEDED = "4202"

_DEPENDENCY_OVERLAP = "4300"
_BACKOFF_EXPORTER = "4301"
_BACKOFF_CONFLICT = "4302"
_BACKOFF_UNSUPPORTED_PYTHON_VERSION = "4303"

_ATTACH_FAILURE_DISTRO = "4400"
_ATTACH_FAILURE_CONFIGURATOR = "4401"
_ATTACH_DETECTS_SDK = "4402"
_INSTRUMENTATION_FAILED = "4403"
_EXCEPTION = "4404"


class AzureDiagnosticLogging:
    _instance = None
    _initialized = False
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(AzureDiagnosticLogging, cls).__new__(cls)
        return cls._instance

    @classmethod
    def _initialize(cls):
        with cls._lock:
            if not cls._initialized:
                if _is_diagnostics_enabled() and _DIAGNOSTIC_LOG_PATH:
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
                    try:
                        if not exists(_DIAGNOSTIC_LOG_PATH):
                            try:
                                makedirs(_DIAGNOSTIC_LOG_PATH)
                            # Multi-thread can create a race condition for creating the log file
                            except FileExistsError:
                                pass
                        f_handler = logging.FileHandler(join(_DIAGNOSTIC_LOG_PATH, _DIAGNOSTIC_LOGGER_FILE_NAME))
                        formatter = logging.Formatter(fmt=log_format, datefmt="%Y-%m-%dT%H:%M:%S")
                        f_handler.setFormatter(formatter)
                        _diagnostic_file_logger.addHandler(f_handler)
                        cls._initialized = True
                    except Exception as e:  # pylint: disable=broad-except
                        _logger.error("Failed to initialize Azure Monitor diagnostic logging: %s", e)
                        cls._initialized = False

    @classmethod
    def debug(cls, message: str, message_id: str):
        if not cls._initialized:
            cls._initialize()
        if cls._initialized:
            _diagnostic_file_logger.debug(message, extra={"msgId": message_id})

    @classmethod
    def info(cls, message: str, message_id: str):
        if not cls._initialized:
            cls._initialize()
        if cls._initialized:
            _diagnostic_file_logger.info(message, extra={"msgId": message_id})

    @classmethod
    def warning(cls, message: str, message_id: str):
        if not cls._initialized:
            cls._initialize()
        if cls._initialized:
            _diagnostic_file_logger.warning(message, extra={"msgId": message_id})

    @classmethod
    def error(cls, message: str, message_id: str):
        if not cls._initialized:
            cls._initialize()
        if cls._initialized:
            _diagnostic_file_logger.error(message, extra={"msgId": message_id})
