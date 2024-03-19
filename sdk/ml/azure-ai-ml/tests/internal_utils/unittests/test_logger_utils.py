import logging

import pytest
from mock import patch
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.trace.tracer import Tracer

from azure.ai.ml._telemetry import AML_INTERNAL_LOGGER_NAMESPACE, get_appinsights_log_handler
from azure.ai.ml._telemetry.logging_handler import AzureMLSDKLogHandler
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
    def test_logging_enabled(self) -> None:
        with patch("azure.ai.ml._telemetry.logging_handler.in_jupyter_notebook", return_value=False):
            handler, tracer = get_appinsights_log_handler(user_agent=USER_AGENT)
            assert isinstance(handler, logging.NullHandler)
            assert tracer is None

        with patch("azure.ai.ml._telemetry.logging_handler.in_jupyter_notebook", return_value=True):
            handler, tracer = get_appinsights_log_handler(user_agent=USER_AGENT)
            assert isinstance(handler, AzureLogHandler)
            assert isinstance(handler, AzureMLSDKLogHandler)
            assert isinstance(tracer, Tracer)


@pytest.mark.unittest
class TestOpsLogger:
    def test_init(self) -> None:
        test_name = "test"
        test_logger = OpsLogger(name=test_name)

        assert test_logger is not None
        assert test_logger.package_logger.name == AML_INTERNAL_LOGGER_NAMESPACE + test_name
        assert not test_logger.package_logger.propagate
        assert test_logger.module_logger.name == test_name
        assert len(test_logger.custom_dimensions) == 0

    def test_update_info(self) -> None:
        test_name = "test"
        test_handler = (logging.NullHandler(), None)
        test_data = {"app_insights_handler": test_handler}

        test_logger = OpsLogger(name=test_name)
        test_logger.update_info(test_data)

        assert len(test_data) == 0
        assert test_logger.package_logger.hasHandlers()
        assert test_logger.package_logger.handlers[0] == test_handler[0]
