# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
from importlib import reload
from json import loads
from os.path import join
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

import azure.monitor.opentelemetry._diagnostics.diagnostic_logging as diagnostic_logger

TEST_LOGGER_PATH = str(Path.home())
TEST_DIAGNOSTIC_LOGGER_FILE_NAME_TEMPLATE = "test-applicationinsights-extension-%s.log"
TEST_SITE_NAME = "TEST_SITE_NAME"
TEST_CUSTOMER_IKEY = "TEST_CUSTOMER_IKEY"
TEST_EXTENSION_VERSION = "TEST_EXTENSION_VERSION"
TEST_VERSION = "TEST_VERSION"
TEST_SUBSCRIPTION_ID_ENV_VAR = "TEST_SUBSCRIPTION_ID+TEST_SUBSCRIPTION_ID"
TEST_SUBSCRIPTION_ID = "TEST_SUBSCRIPTION_ID"
MESSAGE1 = "MESSAGE1"
MESSAGE2 = "MESSAGE2"
MESSAGE3 = "MESSAGE3"
TEST_LOGGER_NAME = "test.logger.name"
TEST_LOGGER = logging.getLogger(TEST_LOGGER_NAME)
TEST_LOGGER_NAME_SUB_MODULE = TEST_LOGGER_NAME + ".sub.module"
TEST_LOGGER_SUB_MODULE = logging.getLogger(TEST_LOGGER_NAME_SUB_MODULE)


def get_test_file_name(test_id):
    return TEST_DIAGNOSTIC_LOGGER_FILE_NAME_TEMPLATE % test_id

def get_test_file_location(test_id):
    return join(
        TEST_LOGGER_PATH, get_test_file_name(test_id) 
    )

def clear_file(test_id):
    with open(get_test_file_location(test_id), "w") as f:
        f.seek(0)
        f.truncate()


def check_file_for_messages(
    level, messages, test_id, logger_name=TEST_LOGGER_NAME_SUB_MODULE
):
    with open(get_test_file_location(test_id), "r") as f:
        f.seek(0)
        for message in messages:
            json = loads(f.readline())
            assert json["time"]
            assert json["level"] == level
            assert json["logger"] == logger_name
            assert json["message"] == message
            properties = json["properties"]
            assert properties["operation"] == "Startup"
            assert properties["sitename"] == TEST_SITE_NAME
            assert properties["ikey"] == TEST_CUSTOMER_IKEY
            assert properties["extensionVersion"] == TEST_EXTENSION_VERSION
            assert properties["sdkVersion"] == TEST_VERSION
            assert properties["subscriptionId"] == TEST_SUBSCRIPTION_ID
        assert not f.read()


def check_file_is_empty(test_id):
    with open(get_test_file_location(test_id), "r") as f:
        f.seek(0)
        assert not f.read()


def set_up(
    is_diagnostics_enabled,
    test_id,
    logger=TEST_LOGGER,
    subscription_id_env_var=TEST_SUBSCRIPTION_ID_ENV_VAR,
) -> None:
    clear_file(test_id)
    check_file_is_empty(test_id)
    diagnostic_logger._logger.handlers.clear()
    logger.handlers.clear()
    TEST_LOGGER.handlers.clear()
    TEST_LOGGER_SUB_MODULE.handlers.clear()
    TEST_LOGGER_SUB_MODULE.setLevel(logging.WARN)
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
        TEST_LOGGER_PATH,
    ).start()
    patch(
        "azure.monitor.opentelemetry._diagnostics.diagnostic_logging._DIAGNOSTIC_LOGGER_FILE_NAME",
        get_test_file_name(test_id),
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
    diagnostic_logger.AzureDiagnosticLogging.enable(logger)


class TestDiagnosticLogger(TestCase):
    def test_initialized(self):
        set_up(test_id=self.id(), is_diagnostics_enabled=True)
        self.assertTrue(diagnostic_logger.AzureDiagnosticLogging._initialized)

    def test_uninitialized(self):
        set_up(test_id=self.id(), is_diagnostics_enabled=False)
        self.assertFalse(diagnostic_logger.AzureDiagnosticLogging._initialized)

    def test_info(self):
        set_up(test_id=self.id(), is_diagnostics_enabled=True)
        TEST_LOGGER_SUB_MODULE.info(MESSAGE1)
        TEST_LOGGER_SUB_MODULE.info(MESSAGE2)
        check_file_is_empty(test_id=self.id())

    def test_info_with_info_log_level(self):
        set_up(test_id=self.id(), is_diagnostics_enabled=True)
        TEST_LOGGER_SUB_MODULE.setLevel(logging.INFO)
        TEST_LOGGER_SUB_MODULE.info(MESSAGE1)
        TEST_LOGGER_SUB_MODULE.info(MESSAGE2)
        TEST_LOGGER_SUB_MODULE.setLevel(logging.NOTSET)
        check_file_for_messages("INFO", (MESSAGE1, MESSAGE2), test_id=self.id())

    def test_info_with_sub_module_info_log_level(self):
        set_up(test_id=self.id(), is_diagnostics_enabled=True)
        TEST_LOGGER_SUB_MODULE.setLevel(logging.INFO)
        TEST_LOGGER_SUB_MODULE.info(MESSAGE1)
        TEST_LOGGER_SUB_MODULE.info(MESSAGE2)
        TEST_LOGGER_SUB_MODULE.setLevel(logging.NOTSET)
        check_file_for_messages("INFO", (MESSAGE1, MESSAGE2), test_id=self.id())

    def test_warning(self):
        set_up(test_id=self.id(), is_diagnostics_enabled=True)
        TEST_LOGGER_SUB_MODULE.warning(MESSAGE1)
        TEST_LOGGER_SUB_MODULE.warning(MESSAGE2)
        check_file_for_messages("WARNING", (MESSAGE1, MESSAGE2), test_id=self.id())

    def test_warning_multiple_enable(self):
        set_up(test_id=self.id(), is_diagnostics_enabled=True)
        diagnostic_logger.AzureDiagnosticLogging.enable(TEST_LOGGER)
        diagnostic_logger.AzureDiagnosticLogging.enable(TEST_LOGGER)
        TEST_LOGGER_SUB_MODULE.warning(MESSAGE1)
        TEST_LOGGER_SUB_MODULE.warning(MESSAGE2)
        check_file_for_messages("WARNING", (MESSAGE1, MESSAGE2), test_id=self.id())

    def test_error(self):
        set_up(test_id=self.id(), is_diagnostics_enabled=True)
        TEST_LOGGER_SUB_MODULE.error(MESSAGE1)
        TEST_LOGGER_SUB_MODULE.error(MESSAGE2)
        check_file_for_messages("ERROR", (MESSAGE1, MESSAGE2), test_id=self.id())

    def test_off_app_service_info(self):
        set_up(test_id=self.id(), is_diagnostics_enabled=False)
        TEST_LOGGER.info(MESSAGE1)
        TEST_LOGGER.info(MESSAGE2)
        TEST_LOGGER_SUB_MODULE.info(MESSAGE1)
        TEST_LOGGER_SUB_MODULE.info(MESSAGE2)
        check_file_is_empty(test_id=self.id())

    def test_off_app_service_warning(self):
        set_up(test_id=self.id(), is_diagnostics_enabled=False)
        TEST_LOGGER.warning(MESSAGE1)
        TEST_LOGGER.warning(MESSAGE2)
        TEST_LOGGER_SUB_MODULE.warning(MESSAGE1)
        TEST_LOGGER_SUB_MODULE.warning(MESSAGE2)
        check_file_is_empty(test_id=self.id())

    def test_off_app_service_error(self):
        set_up(test_id=self.id(), is_diagnostics_enabled=False)
        TEST_LOGGER.error(MESSAGE1)
        TEST_LOGGER.error(MESSAGE2)
        TEST_LOGGER_SUB_MODULE.error(MESSAGE1)
        TEST_LOGGER_SUB_MODULE.error(MESSAGE2)
        check_file_is_empty(test_id=self.id())

    def test_subscription_id_plus(self):
        set_up(
            test_id=self.id(),
            is_diagnostics_enabled=True,
            subscription_id_env_var=TEST_SUBSCRIPTION_ID_ENV_VAR,
        )
        self.assertEqual(diagnostic_logger._SUBSCRIPTION_ID, TEST_SUBSCRIPTION_ID)
        TEST_LOGGER_SUB_MODULE.warning(MESSAGE1)
        TEST_LOGGER_SUB_MODULE.warning(MESSAGE2)
        check_file_for_messages("WARNING", (MESSAGE1, MESSAGE2), test_id=self.id())

    def test_subscription_id_no_plus(self):
        set_up(
            test_id=self.id(),
            is_diagnostics_enabled=True,
            subscription_id_env_var=TEST_SUBSCRIPTION_ID,
        )
        self.assertEqual(diagnostic_logger._SUBSCRIPTION_ID, TEST_SUBSCRIPTION_ID)
        TEST_LOGGER_SUB_MODULE.warning(MESSAGE1)
        TEST_LOGGER_SUB_MODULE.warning(MESSAGE2)
        check_file_for_messages("WARNING", (MESSAGE1, MESSAGE2), test_id=self.id())
