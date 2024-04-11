# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
import os
from importlib import reload
from json import loads
from unittest.mock import patch

import azure.monitor.opentelemetry._diagnostics.diagnostic_logging as diagnostic_logger


TEST_SITE_NAME = "TEST_SITE_NAME"
TEST_CUSTOMER_IKEY = "TEST_CUSTOMER_IKEY"
TEST_EXTENSION_VERSION = "TEST_EXTENSION_VERSION"
TEST_VERSION = "TEST_VERSION"
TEST_SUBSCRIPTION_ID_PLUS = "TEST_SUBSCRIPTION_ID+TEST_SUBSCRIPTION_ID"
TEST_SUBSCRIPTION_ID = "TEST_SUBSCRIPTION_ID"
MESSAGE1 = "MESSAGE1"
MESSAGE2 = "MESSAGE2"
MESSAGE3 = "MESSAGE3"


def clear_file(file_path):
    with open(file_path, "w") as f:
        f.seek(0)
        f.truncate()


def check_file_for_messages(file_path, level, messages):
    with open(file_path, "r") as f:
        f.seek(0)
        for (message, message_id) in messages:
            json = loads(f.readline())
            assert json["time"]
            assert json["level"] == level
            assert json["logger"] == "azure.monitor.opentelemetry._diagnostics.diagnostic_logging"
            assert json["message"] == message
            properties = json["properties"]
            assert properties["operation"] == "Startup"
            assert properties["siteName"] == TEST_SITE_NAME
            assert properties["ikey"] == TEST_CUSTOMER_IKEY
            assert properties["extensionVersion"] == TEST_EXTENSION_VERSION
            assert properties["sdkVersion"] == TEST_VERSION
            assert properties["subscriptionId"] == TEST_SUBSCRIPTION_ID
            assert properties["msgId"] == message_id
        assert not f.read()


def check_file_is_empty(file_path):
    with open(file_path, "r") as f:
        f.seek(0)
        assert not f.read()


def set_up(
    file_path,
    is_diagnostics_enabled,
    subscription_id_env_var=TEST_SUBSCRIPTION_ID_PLUS,
) -> None:
    diagnostic_logger._logger.handlers.clear()
    patch.dict(
        "os.environ",
        {
            "WEBSITE_SITE_NAME": TEST_SITE_NAME,
            "WEBSITE_OWNER_NAME": subscription_id_env_var,
        },
    ).start()
    reload(diagnostic_logger)
    assert not diagnostic_logger.AzureDiagnosticLogging._initialized
    patch(
        "azure.monitor.opentelemetry._diagnostics.diagnostic_logging._DIAGNOSTIC_LOG_PATH",
        os.path.dirname(file_path),
    ).start()
    patch(
        "azure.monitor.opentelemetry._diagnostics.diagnostic_logging._DIAGNOSTIC_LOGGER_FILE_NAME",
        os.path.basename(file_path),
    ).start()
    patch(
        "azure.monitor.opentelemetry._diagnostics.diagnostic_logging._get_customer_ikey_from_env_var",
        return_value=TEST_CUSTOMER_IKEY,
    ).start()
    patch(
        "azure.monitor.opentelemetry._diagnostics.diagnostic_logging._EXTENSION_VERSION",
        TEST_EXTENSION_VERSION,
    ).start()
    patch(
        "azure.monitor.opentelemetry._diagnostics.diagnostic_logging.VERSION",
        TEST_VERSION,
    ).start()
    patch(
        "azure.monitor.opentelemetry._diagnostics.diagnostic_logging._IS_DIAGNOSTICS_ENABLED",
        is_diagnostics_enabled,
    ).start()


class TestDiagnosticLogger:

    def test_initialized(self, temp_file_path):
        set_up(temp_file_path, is_diagnostics_enabled=True)
        diagnostic_logger.AzureDiagnosticLogging.info(MESSAGE1, "4200")
        assert diagnostic_logger.AzureDiagnosticLogging._initialized is True

    def test_uninitialized(self, temp_file_path):
        set_up(temp_file_path, is_diagnostics_enabled=False)
        assert diagnostic_logger.AzureDiagnosticLogging._initialized is False

    def test_info(self, temp_file_path):
        set_up(temp_file_path, is_diagnostics_enabled=True)
        diagnostic_logger.AzureDiagnosticLogging.info(MESSAGE1, "4200")
        diagnostic_logger.AzureDiagnosticLogging.info(MESSAGE2, "4301")
        check_file_for_messages(temp_file_path, "INFO", ((MESSAGE1, "4200"), (MESSAGE2, "4301")))

    def test_warning(self, temp_file_path):
        set_up(temp_file_path, is_diagnostics_enabled=True)
        diagnostic_logger.AzureDiagnosticLogging.warning(MESSAGE1, "4200")
        diagnostic_logger.AzureDiagnosticLogging.warning(MESSAGE2, "4301")
        check_file_for_messages(temp_file_path, "WARNING", ((MESSAGE1, "4200"), (MESSAGE2, "4301")))

    def test_error(self, temp_file_path):
        set_up(temp_file_path, is_diagnostics_enabled=True)
        diagnostic_logger.AzureDiagnosticLogging.error(MESSAGE1, "4200")
        diagnostic_logger.AzureDiagnosticLogging.error(MESSAGE2, "4301")
        check_file_for_messages(temp_file_path, "ERROR", ((MESSAGE1, "4200"), (MESSAGE2, "4301")))

    def test_off_app_service_info(self, temp_file_path):
        set_up(temp_file_path, is_diagnostics_enabled=False)
        diagnostic_logger.AzureDiagnosticLogging.info(MESSAGE1, "4200")
        diagnostic_logger.AzureDiagnosticLogging.info(MESSAGE2, "4301")
        check_file_is_empty(temp_file_path)

    def test_off_app_service_warning(self, temp_file_path):
        set_up(temp_file_path, is_diagnostics_enabled=False)
        diagnostic_logger.AzureDiagnosticLogging.warning(MESSAGE1, "4200")
        diagnostic_logger.AzureDiagnosticLogging.warning(MESSAGE2, "4301")
        check_file_is_empty(temp_file_path)

    def test_off_app_service_error(self, temp_file_path):
        set_up(temp_file_path, is_diagnostics_enabled=False)
        diagnostic_logger.AzureDiagnosticLogging.error(MESSAGE1, "4200")
        diagnostic_logger.AzureDiagnosticLogging.error(MESSAGE2, "4301")
        check_file_is_empty(temp_file_path)

    def test_subscription_id_plus(self, temp_file_path):
        set_up(
            temp_file_path,
            is_diagnostics_enabled=True,
            subscription_id_env_var=TEST_SUBSCRIPTION_ID_PLUS,
        )
        assert diagnostic_logger._SUBSCRIPTION_ID == TEST_SUBSCRIPTION_ID
        diagnostic_logger.AzureDiagnosticLogging.info(MESSAGE1, "4200")
        diagnostic_logger.AzureDiagnosticLogging.info(MESSAGE2, "4301")
        check_file_for_messages(temp_file_path, "INFO", ((MESSAGE1, "4200"), (MESSAGE2, "4301")))

    def test_subscription_id_no_plus(self, temp_file_path):
        set_up(
            temp_file_path,
            is_diagnostics_enabled=True,
            subscription_id_env_var=TEST_SUBSCRIPTION_ID,
        )
        assert diagnostic_logger._SUBSCRIPTION_ID == TEST_SUBSCRIPTION_ID
        diagnostic_logger.AzureDiagnosticLogging.info(MESSAGE1, "4200")
        diagnostic_logger.AzureDiagnosticLogging.info(MESSAGE2, "4301")
        check_file_for_messages(temp_file_path, "INFO", ((MESSAGE1, "4200"), (MESSAGE2, "4301")))
