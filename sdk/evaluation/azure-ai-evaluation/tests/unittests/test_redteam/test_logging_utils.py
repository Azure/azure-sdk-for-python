"""
Unit tests for red_team._utils.logging_utils module.
"""

import logging
import os
import pytest
from unittest.mock import patch, MagicMock, call
from azure.ai.evaluation.red_team._utils.logging_utils import (
    setup_logger,
    log_section_header,
    log_subsection_header,
    log_strategy_start,
    log_strategy_completion,
    log_error,
)


@pytest.mark.unittest
class TestSetupLogger:
    """Test setup_logger function."""

    @patch("azure.ai.evaluation.red_team._utils.logging_utils.logging.FileHandler")
    @patch("azure.ai.evaluation.red_team._utils.logging_utils.logging.StreamHandler")
    @patch("azure.ai.evaluation.red_team._utils.logging_utils.logging.getLogger")
    def test_setup_logger_default(self, mock_get_logger, mock_stream_handler, mock_file_handler):
        """Test setup_logger with default arguments."""
        mock_logger = MagicMock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger

        result = setup_logger()

        mock_get_logger.assert_called_once_with("RedTeamLogger")
        mock_logger.setLevel.assert_called_once_with(logging.DEBUG)
        mock_file_handler.assert_called_once_with("redteam.log")
        mock_file_handler.return_value.setLevel.assert_called_once_with(logging.DEBUG)
        mock_stream_handler.return_value.setLevel.assert_called_once_with(logging.WARNING)
        assert mock_logger.addHandler.call_count == 2
        assert mock_logger.propagate is False
        assert result is mock_logger

    @patch("azure.ai.evaluation.red_team._utils.logging_utils.logging.FileHandler")
    @patch("azure.ai.evaluation.red_team._utils.logging_utils.logging.StreamHandler")
    @patch("azure.ai.evaluation.red_team._utils.logging_utils.logging.getLogger")
    def test_setup_logger_custom_name(self, mock_get_logger, mock_stream_handler, mock_file_handler):
        """Test setup_logger with a custom logger name."""
        mock_logger = MagicMock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger

        setup_logger(logger_name="CustomLogger")

        mock_get_logger.assert_called_once_with("CustomLogger")

    @patch("azure.ai.evaluation.red_team._utils.logging_utils.os.makedirs")
    @patch("azure.ai.evaluation.red_team._utils.logging_utils.logging.FileHandler")
    @patch("azure.ai.evaluation.red_team._utils.logging_utils.logging.StreamHandler")
    @patch("azure.ai.evaluation.red_team._utils.logging_utils.logging.getLogger")
    def test_setup_logger_with_output_dir(self, mock_get_logger, mock_stream_handler, mock_file_handler, mock_makedirs):
        """Test setup_logger creates output directory and uses correct log path."""
        mock_logger = MagicMock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger

        setup_logger(output_dir="/some/output/dir")

        mock_makedirs.assert_called_once_with("/some/output/dir", exist_ok=True)
        expected_path = os.path.join("/some/output/dir", "redteam.log")
        mock_file_handler.assert_called_once_with(expected_path)

    @patch("azure.ai.evaluation.red_team._utils.logging_utils.logging.FileHandler")
    @patch("azure.ai.evaluation.red_team._utils.logging_utils.logging.StreamHandler")
    @patch("azure.ai.evaluation.red_team._utils.logging_utils.logging.getLogger")
    def test_setup_logger_without_output_dir(self, mock_get_logger, mock_stream_handler, mock_file_handler):
        """Test setup_logger without output_dir uses filename only."""
        mock_logger = MagicMock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger

        setup_logger(output_dir=None)

        mock_file_handler.assert_called_once_with("redteam.log")

    @patch("azure.ai.evaluation.red_team._utils.logging_utils.logging.FileHandler")
    @patch("azure.ai.evaluation.red_team._utils.logging_utils.logging.StreamHandler")
    @patch("azure.ai.evaluation.red_team._utils.logging_utils.logging.getLogger")
    def test_setup_logger_clears_existing_handlers(self, mock_get_logger, mock_stream_handler, mock_file_handler):
        """Test setup_logger removes pre-existing handlers before adding new ones."""
        old_handler_1 = MagicMock()
        old_handler_2 = MagicMock()
        mock_logger = MagicMock()
        mock_logger.handlers = [old_handler_1, old_handler_2]
        mock_get_logger.return_value = mock_logger

        setup_logger()

        mock_logger.removeHandler.assert_any_call(old_handler_1)
        mock_logger.removeHandler.assert_any_call(old_handler_2)
        assert mock_logger.removeHandler.call_count == 2

    @patch("azure.ai.evaluation.red_team._utils.logging_utils.logging.FileHandler")
    @patch("azure.ai.evaluation.red_team._utils.logging_utils.logging.StreamHandler")
    @patch("azure.ai.evaluation.red_team._utils.logging_utils.logging.getLogger")
    def test_setup_logger_no_existing_handlers(self, mock_get_logger, mock_stream_handler, mock_file_handler):
        """Test setup_logger skips removal when there are no existing handlers."""
        mock_logger = MagicMock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger

        setup_logger()

        mock_logger.removeHandler.assert_not_called()

    @patch("azure.ai.evaluation.red_team._utils.logging_utils.logging.FileHandler")
    @patch("azure.ai.evaluation.red_team._utils.logging_utils.logging.StreamHandler")
    @patch("azure.ai.evaluation.red_team._utils.logging_utils.logging.getLogger")
    def test_setup_logger_handler_formatters(self, mock_get_logger, mock_stream_handler, mock_file_handler):
        """Test that file and console handlers get their expected formatters."""
        mock_logger = MagicMock()
        mock_logger.handlers = []
        mock_get_logger.return_value = mock_logger

        setup_logger()

        # File handler formatter
        file_fmt_call = mock_file_handler.return_value.setFormatter.call_args
        formatter = file_fmt_call[0][0]
        assert isinstance(formatter, logging.Formatter)
        assert "%(asctime)s" in formatter._fmt
        assert "%(levelname)s" in formatter._fmt
        assert "%(name)s" in formatter._fmt
        assert "%(message)s" in formatter._fmt

        # Console handler formatter
        console_fmt_call = mock_stream_handler.return_value.setFormatter.call_args
        console_formatter = console_fmt_call[0][0]
        assert isinstance(console_formatter, logging.Formatter)
        assert "%(levelname)s" in console_formatter._fmt
        assert "%(message)s" in console_formatter._fmt


@pytest.mark.unittest
class TestLogSectionHeader:
    """Test log_section_header function."""

    def test_log_section_header(self):
        """Test section header logs separator lines and uppercased title."""
        mock_logger = MagicMock()

        log_section_header(mock_logger, "test section")

        assert mock_logger.debug.call_count == 3
        mock_logger.debug.assert_any_call("=" * 80)
        mock_logger.debug.assert_any_call("TEST SECTION")

    def test_log_section_header_call_order(self):
        """Test section header logs in correct order: separator, title, separator."""
        mock_logger = MagicMock()

        log_section_header(mock_logger, "my section")

        calls = mock_logger.debug.call_args_list
        assert calls[0] == call("=" * 80)
        assert calls[1] == call("MY SECTION")
        assert calls[2] == call("=" * 80)


@pytest.mark.unittest
class TestLogSubsectionHeader:
    """Test log_subsection_header function."""

    def test_log_subsection_header(self):
        """Test subsection header logs separator lines and title (not uppercased)."""
        mock_logger = MagicMock()

        log_subsection_header(mock_logger, "subsection title")

        assert mock_logger.debug.call_count == 3
        mock_logger.debug.assert_any_call("-" * 60)
        mock_logger.debug.assert_any_call("subsection title")

    def test_log_subsection_header_call_order(self):
        """Test subsection header logs in correct order: separator, title, separator."""
        mock_logger = MagicMock()

        log_subsection_header(mock_logger, "Sub Title")

        calls = mock_logger.debug.call_args_list
        assert calls[0] == call("-" * 60)
        assert calls[1] == call("Sub Title")
        assert calls[2] == call("-" * 60)


@pytest.mark.unittest
class TestLogStrategyStart:
    """Test log_strategy_start function."""

    def test_log_strategy_start(self):
        """Test strategy start logs the correct info message."""
        mock_logger = MagicMock()

        log_strategy_start(mock_logger, "Base64", "Violence")

        mock_logger.info.assert_called_once_with("Starting processing of Base64 strategy for Violence risk category")


@pytest.mark.unittest
class TestLogStrategyCompletion:
    """Test log_strategy_completion function."""

    def test_log_strategy_completion_with_elapsed_time(self):
        """Test strategy completion logs message including formatted elapsed time."""
        mock_logger = MagicMock()

        log_strategy_completion(mock_logger, "Flip", "Hate", elapsed_time=12.3456)

        mock_logger.info.assert_called_once_with("Completed Flip strategy for Hate risk category in 12.35s")

    def test_log_strategy_completion_without_elapsed_time(self):
        """Test strategy completion logs message without timing when not provided."""
        mock_logger = MagicMock()

        log_strategy_completion(mock_logger, "Morse", "SelfHarm")

        mock_logger.info.assert_called_once_with("Completed Morse strategy for SelfHarm risk category")

    def test_log_strategy_completion_elapsed_time_none(self):
        """Test strategy completion with explicitly passed None elapsed_time."""
        mock_logger = MagicMock()

        log_strategy_completion(mock_logger, "Tense", "Sexual", elapsed_time=None)

        mock_logger.info.assert_called_once_with("Completed Tense strategy for Sexual risk category")

    def test_log_strategy_completion_elapsed_time_zero(self):
        """Test strategy completion with zero elapsed_time uses no-time branch."""
        mock_logger = MagicMock()

        log_strategy_completion(mock_logger, "Base64", "Violence", elapsed_time=0)

        # 0 is falsy, so the no-time branch is taken
        mock_logger.info.assert_called_once_with("Completed Base64 strategy for Violence risk category")


@pytest.mark.unittest
class TestLogError:
    """Test log_error function."""

    def test_log_error_message_only(self):
        """Test logging an error with just a message."""
        mock_logger = MagicMock()

        log_error(mock_logger, "Something went wrong")

        mock_logger.error.assert_called_once_with("Something went wrong", exc_info=True)

    def test_log_error_with_context(self):
        """Test logging an error with context prepended."""
        mock_logger = MagicMock()

        log_error(mock_logger, "Connection failed", context="DatabaseModule")

        mock_logger.error.assert_called_once_with("[DatabaseModule] Connection failed", exc_info=True)

    def test_log_error_with_exception(self):
        """Test logging an error with exception appended."""
        mock_logger = MagicMock()
        exc = ValueError("invalid value")

        log_error(mock_logger, "Processing error", exception=exc)

        mock_logger.error.assert_called_once_with("Processing error: invalid value", exc_info=True)

    def test_log_error_with_context_and_exception(self):
        """Test logging an error with both context and exception."""
        mock_logger = MagicMock()
        exc = RuntimeError("timeout reached")

        log_error(mock_logger, "Request failed", exception=exc, context="APIClient")

        mock_logger.error.assert_called_once_with("[APIClient] Request failed: timeout reached", exc_info=True)

    def test_log_error_no_context_no_exception(self):
        """Test logging an error with neither context nor exception."""
        mock_logger = MagicMock()

        log_error(mock_logger, "Generic error", exception=None, context=None)

        mock_logger.error.assert_called_once_with("Generic error", exc_info=True)
