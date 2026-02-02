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
        for message, message_id in messages:
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
    diagnostic_logger._diagnostic_file_logger.handlers.clear()
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
        "azure.monitor.opentelemetry._diagnostics.diagnostic_logging._is_diagnostics_enabled",
        return_value=is_diagnostics_enabled,
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

    def test_initialize_file_handler_exception(self, temp_file_path):
        """Test that initialization fails gracefully when FileHandler creation raises an exception."""
        set_up(temp_file_path, is_diagnostics_enabled=True)
        # Mock FileHandler to raise an exception
        with patch(
            "azure.monitor.opentelemetry._diagnostics.diagnostic_logging.logging.FileHandler"
        ) as mock_file_handler, patch(
            "azure.monitor.opentelemetry._diagnostics.diagnostic_logging._logger"
        ) as mock_logger:
            mock_file_handler.side_effect = OSError("Permission denied")
            # Attempt to log, which will trigger initialization
            diagnostic_logger.AzureDiagnosticLogging.info(MESSAGE1, "4200")
            # Verify that initialization failed
            assert diagnostic_logger.AzureDiagnosticLogging._initialized is False
            check_file_is_empty(temp_file_path)
            # Verify that the error was logged
            mock_logger.error.assert_called_once()

    def test_initialize_makedirs_exception_not_file_exists(self, temp_file_path):
        """Test that initialization fails gracefully when makedirs raises a non-FileExistsError exception."""
        set_up(temp_file_path, is_diagnostics_enabled=True)
        # Mock makedirs to raise a PermissionError
        with patch("azure.monitor.opentelemetry._diagnostics.diagnostic_logging.makedirs") as mock_makedirs, patch(
            "azure.monitor.opentelemetry._diagnostics.diagnostic_logging.exists", return_value=False
        ), patch("azure.monitor.opentelemetry._diagnostics.diagnostic_logging._logger") as mock_logger:
            mock_makedirs.side_effect = PermissionError("Permission denied")
            # Attempt to log, which will trigger initialization
            diagnostic_logger.AzureDiagnosticLogging.info(MESSAGE1, "4200")
            # Verify that initialization failed
            assert diagnostic_logger.AzureDiagnosticLogging._initialized is False
            check_file_is_empty(temp_file_path)
            # Verify that the error was logged
            mock_logger.error.assert_called_once()

    def test_initialize_makedirs_file_exists_error_handled(self, temp_file_path):
        """Test that FileExistsError from makedirs is handled gracefully and initialization continues."""
        set_up(temp_file_path, is_diagnostics_enabled=True)
        # Mock makedirs to raise FileExistsError (this should be handled gracefully)
        with patch("azure.monitor.opentelemetry._diagnostics.diagnostic_logging.makedirs") as mock_makedirs, patch(
            "azure.monitor.opentelemetry._diagnostics.diagnostic_logging.exists", return_value=False
        ), patch("azure.monitor.opentelemetry._diagnostics.diagnostic_logging._logger") as mock_logger:
            mock_makedirs.side_effect = FileExistsError("Directory already exists")
            # Attempt to log, which will trigger initialization
            diagnostic_logger.AzureDiagnosticLogging.info(MESSAGE1, "4200")
            # Verify that initialization succeeded despite FileExistsError
            assert diagnostic_logger.AzureDiagnosticLogging._initialized is True
            check_file_for_messages(temp_file_path, "INFO", ((MESSAGE1, "4200"),))

    def test_initialize_formatter_exception(self, temp_file_path):
        """Test that initialization fails gracefully when Formatter creation raises an exception."""
        set_up(temp_file_path, is_diagnostics_enabled=True)
        # Mock Formatter to raise an exception
        with patch(
            "azure.monitor.opentelemetry._diagnostics.diagnostic_logging.logging.Formatter"
        ) as mock_formatter, patch(
            "azure.monitor.opentelemetry._diagnostics.diagnostic_logging._logger"
        ) as mock_logger:
            mock_formatter.side_effect = ValueError("Invalid format string")
            # Attempt to log, which will trigger initialization
            diagnostic_logger.AzureDiagnosticLogging.info(MESSAGE1, "4200")
            # Verify that initialization failed
            assert diagnostic_logger.AzureDiagnosticLogging._initialized is False
            # Verify that the error was logged
            mock_logger.error.assert_called_once()

    def test_singleton_pattern(self, temp_file_path):
        """Test that AzureDiagnosticLogging follows the singleton pattern."""
        set_up(temp_file_path, is_diagnostics_enabled=True)

        # Create multiple instances
        instance1 = diagnostic_logger.AzureDiagnosticLogging()
        instance2 = diagnostic_logger.AzureDiagnosticLogging()
        instance3 = diagnostic_logger.AzureDiagnosticLogging()

        # Verify all instances are the same object
        assert instance1 is instance2
        assert instance2 is instance3
        assert instance1 is instance3

        # Verify they all have the same id (memory address)
        assert id(instance1) == id(instance2) == id(instance3)

        # Verify class-level access still works
        diagnostic_logger.AzureDiagnosticLogging.info(MESSAGE1, "4200")
        assert diagnostic_logger.AzureDiagnosticLogging._initialized is True

        # Verify instance methods work (if they exist)
        # Since this is primarily a class-based API, we just verify the singleton behavior
