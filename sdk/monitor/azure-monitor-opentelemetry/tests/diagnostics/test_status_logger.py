# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

import os
from json import loads
from unittest.mock import patch

from azure.monitor.opentelemetry._diagnostics.status_logger import (
    AzureStatusLogger,
    _get_status_logger_file_name
)

TEST_MACHINE_NAME = "TEST_MACHINE_NAME"
TEST_PID = 321
TEST_OPERATION = "TEST_OPERATION"
TEST_OPERATION = "TEST_OPERATION"
TEST_SITE_NAME = "TEST_SITE_NAME"
TEST_CUSTOMER_IKEY = "TEST_CUSTOMER_IKEY"
TEST_EXTENSION_VERSION = "TEST_EXTENSION_VERSION"
TEST_VERSION = "TEST_VERSION"
TEST_SUBSCRIPTION_ID = "TEST_SUBSCRIPTION_ID"
MESSAGE1 = "MESSAGE1"
MESSAGE2 = "MESSAGE2"


def set_up(file_path, is_diagnostics_enabled=True):

    patch(
        "azure.monitor.opentelemetry._diagnostics.status_logger._STATUS_LOG_PATH",
        file_path,
    ).start()
    patch(
        "azure.monitor.opentelemetry._diagnostics.status_logger._STATUS_LOG_PATH",
        os.path.dirname(file_path),
    ).start()
    patch(
        "azure.monitor.opentelemetry._diagnostics.status_logger._get_status_logger_file_name",
        return_value=os.path.basename(file_path),
    ).start()
    patch(
        "azure.monitor.opentelemetry._diagnostics.status_logger._get_customer_ikey_from_env_var",
        return_value=TEST_CUSTOMER_IKEY,
    ).start()
    patch(
        "azure.monitor.opentelemetry._diagnostics.status_logger._EXTENSION_VERSION",
        TEST_EXTENSION_VERSION,
    ).start()
    patch(
        "azure.monitor.opentelemetry._diagnostics.status_logger.VERSION",
        TEST_VERSION,
    ).start()
    patch(
        "azure.monitor.opentelemetry._diagnostics.status_logger._IS_DIAGNOSTICS_ENABLED",
        is_diagnostics_enabled,
    ).start()
    patch(
        "azure.monitor.opentelemetry._diagnostics.status_logger.getpid",
        return_value=TEST_PID,
    ).start()
    patch(
        "azure.monitor.opentelemetry._diagnostics.status_logger._MACHINE_NAME",
        TEST_MACHINE_NAME,
    ).start()


def check_file_for_messages(agent_initialized_successfully, file_path, reason=None, sdk_present=None):
    with open(file_path, "r") as f:
        f.seek(0)
        json = loads(f.readline())
        assert json["AgentInitializedSuccessfully"] == agent_initialized_successfully
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
        if sdk_present:
            assert json["SDKPresent"] == sdk_present
        else:
            assert "SDKPresent" not in json
        assert not f.read()


def check_file_is_empty(file_path):
    with open(file_path, "r") as f:
        f.seek(0)
        assert not f.read()


class TestStatusLogger:

    def test_log_status_success(self, temp_file_path):
        set_up(temp_file_path, is_diagnostics_enabled=True)
        AzureStatusLogger.log_status(False, MESSAGE1)
        AzureStatusLogger.log_status(True, MESSAGE2)
        check_file_for_messages(True, temp_file_path, MESSAGE2)

    def test_log_status_failed_initialization(self, temp_file_path):
        set_up(temp_file_path, is_diagnostics_enabled=True)
        AzureStatusLogger.log_status(True, MESSAGE1)
        AzureStatusLogger.log_status(False, MESSAGE2)
        check_file_for_messages(False, temp_file_path, MESSAGE2)

    def test_log_status_no_reason(self, temp_file_path):
        set_up(temp_file_path, is_diagnostics_enabled=True)
        AzureStatusLogger.log_status(False, MESSAGE1)
        AzureStatusLogger.log_status(True)
        check_file_for_messages(True, temp_file_path)

    def test_log_status_sdk_present(self, temp_file_path):
        set_up(temp_file_path, is_diagnostics_enabled=True)
        AzureStatusLogger.log_status(True, reason=MESSAGE1)
        AzureStatusLogger.log_status(False, reason=MESSAGE2, sdk_present=True)
        check_file_for_messages(agent_initialized_successfully=False, file_path=temp_file_path, reason=MESSAGE2, sdk_present=True)

    def test_disabled_log_status_success(self, temp_file_path):
        set_up(temp_file_path, is_diagnostics_enabled=False)
        AzureStatusLogger.log_status(False, MESSAGE1)
        AzureStatusLogger.log_status(True, MESSAGE2)
        check_file_is_empty(temp_file_path)

    def test_disabled_log_status_failed_initialization(self, temp_file_path):
        set_up(temp_file_path, is_diagnostics_enabled=False)
        AzureStatusLogger.log_status(True, MESSAGE1)
        AzureStatusLogger.log_status(False, MESSAGE2)
        check_file_is_empty(temp_file_path)

    def test_disabled_log_status_no_reason(self, temp_file_path):
        set_up(temp_file_path, is_diagnostics_enabled=False)
        AzureStatusLogger.log_status(False, MESSAGE1)
        AzureStatusLogger.log_status(True)
        check_file_is_empty(temp_file_path)

    def test_disabled_log_status_sdk_present(self, temp_file_path):
        set_up(temp_file_path, is_diagnostics_enabled=False)
        AzureStatusLogger.log_status(True, reason=MESSAGE1)
        AzureStatusLogger.log_status(False, reason=MESSAGE2, sdk_present=True)
        check_file_is_empty(temp_file_path)

    @patch(
        "azure.monitor.opentelemetry._diagnostics.status_logger._MACHINE_NAME",
        TEST_MACHINE_NAME,
    )
    def test_get_status_logger_file_name(self):
        assert _get_status_logger_file_name(TEST_PID) == f"status_{TEST_MACHINE_NAME}_{TEST_PID}.json"
