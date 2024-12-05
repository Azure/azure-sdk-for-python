import logging

import pytest
from mock import MagicMock, patch

from azure.ai.ml._telemetry import AML_INTERNAL_LOGGER_NAMESPACE, configure_appinsights_logging
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
    # @patch("azure.monitor.opentelemetry.configure_azure_monitor")
    @patch("azure.ai.ml._telemetry.logging_handler.setup_azure_monitor")
    @patch("azure.ai.ml._telemetry.logging_handler.logging.getLogger")
    def test_logging_enabled(self, mock_get_logger, mock_configure_azure_monitor) -> None:
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        with patch("azure.ai.ml._telemetry.logging_handler.in_jupyter_notebook", return_value=False):
            configure_appinsights_logging(user_agent=USER_AGENT)
            assert len(mock_logger.addHandler.call_args_list) == 1
            assert isinstance(mock_logger.addHandler.call_args[0][0], logging.NullHandler)
            mock_configure_azure_monitor.assert_not_called()
            mock_logger.reset_mock()

        with patch("azure.ai.ml._telemetry.logging_handler.in_jupyter_notebook", return_value=True):
            configure_appinsights_logging(user_agent=USER_AGENT)
            mock_logger.addHandler.assert_not_called()
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
