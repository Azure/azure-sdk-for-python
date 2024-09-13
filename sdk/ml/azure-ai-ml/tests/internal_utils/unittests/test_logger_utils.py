import logging

import pytest
from mock import patch

from azure.ai.ml._telemetry import AML_INTERNAL_LOGGER_NAMESPACE, set_appinsights_distro
from azure.ai.ml._user_agent import USER_AGENT
from azure.ai.ml._utils._logger_utils import OpsLogger, initialize_logger_info


@pytest.mark.unittest
class TestLoggerUtils:
    def test_initialize_logger_info(self) -> None:
        test_name = "test"
        test_terminator = "\n\n"
        module_logger = logging.getLogger(test_name)

        initialize_logger_info(module_logger, terminator=test_terminator)

        assert module_logger.level == logging.INFO
        assert not module_logger.propagate
        assert module_logger.hasHandlers()
        assert module_logger.handlers[0].terminator == test_terminator


@pytest.mark.unittest
class TestLoggingHandler:
    @patch("azure.ai.ml._telemetry.logging_handler.configure_azure_monitor")
    def test_logging_enabled(self, mock_configure_azure_monitor) -> None:
        with patch("azure.ai.ml._telemetry.logging_handler.in_jupyter_notebook", return_value=False):
            set_appinsights_distro(user_agent=USER_AGENT)
            mock_configure_azure_monitor.assert_not_called()

        with patch("azure.ai.ml._telemetry.logging_handler.in_jupyter_notebook", return_value=True):
            set_appinsights_distro(user_agent=USER_AGENT)
            mock_configure_azure_monitor.assert_called_once()


@pytest.mark.unittest
class TestOpsLogger:
    def test_init(self) -> None:
        test_name = "test"
        test_logger = OpsLogger(name=test_name)

        assert test_logger is not None
        assert test_logger.package_logger.name == AML_INTERNAL_LOGGER_NAMESPACE + "." + test_name
        assert test_logger.package_logger.propagate
        assert test_logger.package_tracer is not None
        assert test_logger.module_logger.name == test_name
        assert len(test_logger.custom_dimensions) == 0

    def test_update_filter(self) -> None:
        test_name = "test"

        test_logger = OpsLogger(name=test_name)
        assert len(test_logger.package_logger.filters) == 0

        test_logger.package_logger.parent = logging.getLogger("parent")
        test_logger.package_logger.parent.addFilter(logging.Filter)
        test_logger.update_filter()

        assert len(test_logger.package_logger.filters) == 1
