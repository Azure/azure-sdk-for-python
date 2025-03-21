"""
Unit tests for red_team_agent.utils.logging_utils module.
"""

import pytest
import logging
import os
from unittest.mock import patch, MagicMock, call
from datetime import datetime
from azure.ai.evaluation.red_team_agent.utils.logging_utils import (
    setup_logger, log_section_header, log_subsection_header,
    log_strategy_start, log_strategy_completion, log_error
)


@pytest.fixture
def mock_logger():
    """Fixture that provides a mock logger object."""
    return MagicMock(spec=logging.Logger)


@patch('logging.getLogger')
@patch('logging.FileHandler')
@patch('logging.StreamHandler')
@patch('datetime.datetime')
def test_setup_logger(mock_datetime, mock_stream_handler, mock_file_handler, mock_get_logger):
    """Test logger setup with correct handlers and configuration."""
    # Setup datetime mock
    mock_now = MagicMock()
    mock_now.strftime.return_value = "redteam_agent_test_timestamp.log"
    mock_datetime.now.return_value = mock_now
    
    # Setup mock handlers
    mock_file_handler_instance = MagicMock()
    mock_file_handler.return_value = mock_file_handler_instance
    
    mock_stream_handler_instance = MagicMock()
    mock_stream_handler.return_value = mock_stream_handler_instance
    
    # Setup mock logger
    mock_logger_instance = MagicMock()
    mock_get_logger.return_value = mock_logger_instance
    
    # Call the function under test
    result = setup_logger("TestLogger")
    
    # Verify logger was created correctly
    mock_get_logger.assert_called_once_with("TestLogger")
    mock_logger_instance.setLevel.assert_called_once_with(logging.DEBUG)
    
    # Verify file handler was created correctly
    mock_file_handler.assert_called_once_with("redteam_agent_test_timestamp.log")
    mock_file_handler_instance.setLevel.assert_called_once_with(logging.DEBUG)
    mock_logger_instance.addHandler.assert_any_call(mock_file_handler_instance)
    
    # Verify stream handler was created correctly
    mock_stream_handler_instance.setLevel.assert_called_once_with(logging.WARNING)
    mock_logger_instance.addHandler.assert_any_call(mock_stream_handler_instance)
    
    # Verify propagate was set to False
    assert mock_logger_instance.propagate is False
    
    # Verify the function returns the logger
    assert result == mock_logger_instance


def test_log_section_header(mock_logger):
    """Test section header logging."""
    log_section_header(mock_logger, "TEST SECTION")
    
    assert mock_logger.debug.call_count == 3
    mock_logger.debug.assert_any_call("=" * 80)
    mock_logger.debug.assert_any_call("TEST SECTION")
    mock_logger.debug.assert_any_call("=" * 80)


def test_log_subsection_header(mock_logger):
    """Test subsection header logging."""
    log_subsection_header(mock_logger, "Test Subsection")
    
    assert mock_logger.debug.call_count == 3
    mock_logger.debug.assert_any_call("-" * 60)
    mock_logger.debug.assert_any_call("Test Subsection")
    mock_logger.debug.assert_any_call("-" * 60)


def test_log_strategy_start(mock_logger):
    """Test strategy start logging."""
    log_strategy_start(mock_logger, "TestStrategy", "test_risk")
    
    mock_logger.info.assert_called_once_with(
        "Starting processing of TestStrategy strategy for test_risk risk category"
    )


def test_log_strategy_completion_with_elapsed_time(mock_logger):
    """Test strategy completion logging with elapsed time."""
    log_strategy_completion(mock_logger, "TestStrategy", "test_risk", 10.5)
    
    mock_logger.info.assert_called_once_with(
        "Completed TestStrategy strategy for test_risk risk category in 10.50s"
    )


def test_log_strategy_completion_without_elapsed_time(mock_logger):
    """Test strategy completion logging without elapsed time."""
    log_strategy_completion(mock_logger, "TestStrategy", "test_risk")
    
    mock_logger.info.assert_called_once_with(
        "Completed TestStrategy strategy for test_risk risk category"
    )


def test_log_error_basic(mock_logger):
    """Test basic error logging with just a message."""
    log_error(mock_logger, "Test error message")
    
    mock_logger.error.assert_called_once_with("Test error message")


def test_log_error_with_exception(mock_logger):
    """Test error logging with an exception."""
    exception = Exception("Test exception")
    log_error(mock_logger, "Test error message", exception)
    
    mock_logger.error.assert_called_once_with("Test error message: Test exception")


def test_log_error_with_context(mock_logger):
    """Test error logging with context."""
    log_error(mock_logger, "Test error message", context="TestContext")
    
    mock_logger.error.assert_called_once_with("[TestContext] Test error message")


def test_log_error_with_exception_and_context(mock_logger):
    """Test error logging with both exception and context."""
    exception = Exception("Test exception")
    log_error(mock_logger, "Test error message", exception, "TestContext")
    
    mock_logger.error.assert_called_once_with("[TestContext] Test error message: Test exception")


@patch('os.path.exists')
def test_setup_logger_with_existing_handlers(mock_exists, mock_logger):
    """Test logger setup when handlers already exist."""
    mock_exists.return_value = True
    
    with patch('logging.getLogger') as mock_get_logger:
        # Setup a logger that already has handlers
        mock_handler1 = MagicMock()
        mock_handler2 = MagicMock()
        mock_logger_instance = MagicMock(spec=logging.Logger)
        mock_logger_instance.handlers = [mock_handler1, mock_handler2]
        mock_get_logger.return_value = mock_logger_instance
        
        # Call the function under test
        with patch('datetime.datetime'):
            with patch('logging.FileHandler'):
                with patch('logging.StreamHandler'):
                    setup_logger("TestLogger")
        
        # Verify existing handlers were removed
        assert mock_logger_instance.removeHandler.call_count == 2
        mock_logger_instance.removeHandler.assert_any_call(mock_handler1)
        mock_logger_instance.removeHandler.assert_any_call(mock_handler2)