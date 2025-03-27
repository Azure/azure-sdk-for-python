"""
Logging utilities for Red Team Agent.

This module provides consistent logging configuration and helper functions
for logging throughout the Red Team Agent.
"""

import logging
import os
from datetime import datetime


def setup_logger(logger_name="RedTeamLogger", output_dir=None):
    """Configure and return a logger instance for the Red Team Agent.
    
    Creates two handlers:
    - File handler: Captures all logs at DEBUG level
    - Console handler: Shows WARNING and above for better visibility
    
    :param logger_name: Name to use for the logger
    :type logger_name: str
    :param output_dir: Directory to store log files in. If None, logs are stored in current directory.
    :type output_dir: Optional[str]
    :return: The configured logger instance
    :rtype: logging.Logger
    """
    # Format matches what's expected in test_setup_logger
    log_filename = "redteam.log"
    
    # If output directory is specified, create path with that directory
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        log_filepath = os.path.join(output_dir, log_filename)
    else:
        log_filepath = log_filename
    
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers (in case logger was already configured)
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)
            
    # File handler - captures all logs at DEBUG level with detailed formatting
    file_handler = logging.FileHandler(log_filepath)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler - shows only WARNING and above to reduce output but keep important messages
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Don't propagate to root logger to avoid duplicate logs
    logger.propagate = False
    
    return logger


def log_section_header(logger, section_title):
    """Log a section header to improve log readability.
    
    :param logger: The logger instance
    :type logger: logging.Logger
    :param section_title: The title of the section
    :type section_title: str
    """
    logger.debug("=" * 80)
    logger.debug(section_title.upper())
    logger.debug("=" * 80)


def log_subsection_header(logger, section_title):
    """Log a subsection header to improve log readability.
    
    :param logger: The logger instance
    :type logger: logging.Logger
    :param section_title: The title of the subsection
    :type section_title: str
    """
    logger.debug("-" * 60)
    logger.debug(section_title)
    logger.debug("-" * 60)


def log_strategy_start(logger, strategy_name, risk_category):
    """Log the start of a strategy processing.
    
    :param logger: The logger instance
    :type logger: logging.Logger
    :param strategy_name: The name of the strategy
    :type strategy_name: str
    :param risk_category: The risk category being processed
    :type risk_category: str
    """
    logger.info(f"Starting processing of {strategy_name} strategy for {risk_category} risk category")


def log_strategy_completion(logger, strategy_name, risk_category, elapsed_time=None):
    """Log the completion of a strategy processing.
    
    :param logger: The logger instance
    :type logger: logging.Logger
    :param strategy_name: The name of the strategy
    :type strategy_name: str
    :param risk_category: The risk category being processed
    :type risk_category: str
    :param elapsed_time: The time taken to process, if available
    :type elapsed_time: float
    """
    if elapsed_time:
        logger.info(f"Completed {strategy_name} strategy for {risk_category} risk category in {elapsed_time:.2f}s")
    else:
        logger.info(f"Completed {strategy_name} strategy for {risk_category} risk category")


def log_error(logger, message, exception=None, context=None):
    """Log an error with additional context if available.
    
    :param logger: The logger instance
    :type logger: logging.Logger
    :param message: The error message
    :type message: str
    :param exception: The exception that was raised, if any
    :type exception: Exception
    :param context: Additional context about where the error occurred
    :type context: str
    """
    error_msg = message
    if context:
        error_msg = f"[{context}] {error_msg}"
    if exception:
        error_msg = f"{error_msg}: {str(exception)}"
    logger.error(error_msg)