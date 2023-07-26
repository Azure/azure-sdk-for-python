# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

from json import loads
from os.path import join
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from azure.monitor.opentelemetry.diagnostics._status_logger import (
    AzureStatusLogger,
)

TEST_LOGGER_PATH = str(Path.home())
TEST_MACHINE_NAME = "TEST_MACHINE_NAME"
TEST_PID = 321
TEST_STATUS_LOGGER_LOCATION = join(
    TEST_LOGGER_PATH, f"status_{TEST_MACHINE_NAME}_{TEST_PID}.json"
)
TEST_OPERATION = "TEST_OPERATION"
TEST_OPERATION = "TEST_OPERATION"
TEST_SITE_NAME = "TEST_SITE_NAME"
TEST_CUSTOMER_IKEY = "TEST_CUSTOMER_IKEY"
TEST_EXTENSION_VERSION = "TEST_EXTENSION_VERSION"
TEST_VERSION = "TEST_VERSION"
TEST_SUBSCRIPTION_ID = "TEST_SUBSCRIPTION_ID"
MESSAGE1 = "MESSAGE1"
MESSAGE2 = "MESSAGE2"


def clear_file():
    with open(TEST_STATUS_LOGGER_LOCATION, "w") as f:
        f.seek(0)
        f.truncate()


def check_file_for_messages(agent_initialized_successfully, reason=None):
    with open(TEST_STATUS_LOGGER_LOCATION, "r") as f:
        f.seek(0)
        json = loads(f.readline())
        assert (
            json["AgentInitializedSuccessfully"]
            == agent_initialized_successfully
        )
        assert json["AppType"] == "python"
        assert json["MachineName"] == TEST_MACHINE_NAME
        assert json["PID"] == TEST_PID
        assert json["SdkVersion"] == TEST_VERSION
        assert json["Ikey"] == TEST_CUSTOMER_IKEY
        assert json["ExtensionVersion"] == TEST_EXTENSION_VERSION
        if reason:
            assert json["Reason"] == reason
        else:
            assert "Reason" not in json
        assert not f.read()


def check_file_is_empty():
    with open(TEST_STATUS_LOGGER_LOCATION, "r") as f:
        f.seek(0)
        assert not f.read()


class TestStatusLogger(TestCase):
    def setUp(self) -> None:
        clear_file()

    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger._STATUS_LOG_PATH",
        TEST_LOGGER_PATH,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger._get_customer_ikey_from_env_var",
        return_value=TEST_CUSTOMER_IKEY,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger._EXTENSION_VERSION",
        TEST_EXTENSION_VERSION,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger.VERSION",
        TEST_VERSION,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger._IS_DIAGNOSTICS_ENABLED",
        True,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger.getpid",
        return_value=TEST_PID,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger._MACHINE_NAME",
        TEST_MACHINE_NAME,
    )
    def test_log_status_success(self, mock_getpid, mock_get_ikey):
        AzureStatusLogger.log_status(False, MESSAGE1)
        AzureStatusLogger.log_status(True, MESSAGE2)
        check_file_for_messages(True, MESSAGE2)

    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger._STATUS_LOG_PATH",
        TEST_LOGGER_PATH,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger._get_customer_ikey_from_env_var",
        return_value=TEST_CUSTOMER_IKEY,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger._EXTENSION_VERSION",
        TEST_EXTENSION_VERSION,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger.VERSION",
        TEST_VERSION,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger._IS_DIAGNOSTICS_ENABLED",
        True,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger.getpid",
        return_value=TEST_PID,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger._MACHINE_NAME",
        TEST_MACHINE_NAME,
    )
    def test_log_status_failed_initialization(
        self, mock_getpid, mock_get_ikey
    ):
        AzureStatusLogger.log_status(True, MESSAGE1)
        AzureStatusLogger.log_status(False, MESSAGE2)
        check_file_for_messages(False, MESSAGE2)

    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger._STATUS_LOG_PATH",
        TEST_LOGGER_PATH,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger._get_customer_ikey_from_env_var",
        return_value=TEST_CUSTOMER_IKEY,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger._EXTENSION_VERSION",
        TEST_EXTENSION_VERSION,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger.VERSION",
        TEST_VERSION,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger._IS_DIAGNOSTICS_ENABLED",
        True,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger.getpid",
        return_value=TEST_PID,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger._MACHINE_NAME",
        TEST_MACHINE_NAME,
    )
    def test_log_status_no_reason(self, mock_getpid, mock_get_ikey):
        AzureStatusLogger.log_status(False, MESSAGE1)
        AzureStatusLogger.log_status(True)
        check_file_for_messages(True)

    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger._STATUS_LOG_PATH",
        TEST_LOGGER_PATH,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger._get_customer_ikey_from_env_var",
        return_value=TEST_CUSTOMER_IKEY,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger._EXTENSION_VERSION",
        TEST_EXTENSION_VERSION,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger.VERSION",
        TEST_VERSION,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger._IS_DIAGNOSTICS_ENABLED",
        False,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger.getpid",
        return_value=TEST_PID,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger._MACHINE_NAME",
        TEST_MACHINE_NAME,
    )
    def test_disabled_log_status_success(self, mock_getpid, mock_get_ikey):
        AzureStatusLogger.log_status(False, MESSAGE1)
        AzureStatusLogger.log_status(True, MESSAGE2)
        check_file_is_empty()

    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger._STATUS_LOG_PATH",
        TEST_LOGGER_PATH,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger._get_customer_ikey_from_env_var",
        return_value=TEST_CUSTOMER_IKEY,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger._EXTENSION_VERSION",
        TEST_EXTENSION_VERSION,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger.VERSION",
        TEST_VERSION,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger._IS_DIAGNOSTICS_ENABLED",
        False,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger.getpid",
        return_value=TEST_PID,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger._MACHINE_NAME",
        TEST_MACHINE_NAME,
    )
    def test_disabled_log_status_failed_initialization(
        self, mock_getpid, mock_get_ikey
    ):
        AzureStatusLogger.log_status(True, MESSAGE1)
        AzureStatusLogger.log_status(False, MESSAGE2)
        check_file_is_empty()

    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger._STATUS_LOG_PATH",
        TEST_LOGGER_PATH,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger._get_customer_ikey_from_env_var",
        return_value=TEST_CUSTOMER_IKEY,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger._EXTENSION_VERSION",
        TEST_EXTENSION_VERSION,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger.VERSION",
        TEST_VERSION,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger._IS_DIAGNOSTICS_ENABLED",
        False,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger.getpid",
        return_value=TEST_PID,
    )
    @patch(
        "azure.monitor.opentelemetry.diagnostics._status_logger._MACHINE_NAME",
        TEST_MACHINE_NAME,
    )
    def test_disabled_log_status_no_reason(self, mock_getpid, mock_get_ikey):
        AzureStatusLogger.log_status(False, MESSAGE1)
        AzureStatusLogger.log_status(True)
        check_file_is_empty()
