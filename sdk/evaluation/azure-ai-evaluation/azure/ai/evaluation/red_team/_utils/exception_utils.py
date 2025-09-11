# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Exception handling utilities for Red Team Agent.

This module provides centralized exception handling, error categorization,
and error reporting utilities for red team operations.
"""

import logging
import traceback
import asyncio
from typing import Optional, Any, Dict, Union
from enum import Enum


class ErrorCategory(Enum):
    """Categories of errors that can occur during red team operations."""

    NETWORK = "network"
    AUTHENTICATION = "authentication"
    CONFIGURATION = "configuration"
    DATA_PROCESSING = "data_processing"
    ORCHESTRATOR = "orchestrator"
    EVALUATION = "evaluation"
    FILE_IO = "file_io"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


class ErrorSeverity(Enum):
    """Severity levels for errors."""

    LOW = "low"  # Warning level, operation can continue
    MEDIUM = "medium"  # Error level, task failed but scan can continue
    HIGH = "high"  # Critical error, scan should be aborted
    FATAL = "fatal"  # Unrecoverable error


class RedTeamError(Exception):
    """Base exception for Red Team operations."""

    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.context = context or {}
        self.original_exception = original_exception


class NonRetryableError(RedTeamError):
    """Exception for errors that should not be retried and should fail the operation immediately."""

    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        context: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None,
    ):
        super().__init__(
            message=message,
            category=category,
            severity=ErrorSeverity.HIGH,  # Non-retryable errors are high severity
            context=context,
            original_exception=original_exception,
        )


class ExceptionHandler:
    """Centralized exception handling for Red Team operations."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize exception handler.

        :param logger: Logger instance for error reporting
        """
        self.logger = logger or logging.getLogger(__name__)
        self.error_counts: Dict[ErrorCategory, int] = {category: 0 for category in ErrorCategory}

    def is_non_retryable_error(self, exception: Exception) -> bool:
        """Determine if an exception represents a non-retryable error.

        Non-retryable errors are those that won't be resolved by retrying,
        such as authentication failures, bad requests, configuration errors, etc.

        :param exception: The exception to check
        :return: True if the error should not be retried
        """
        import httpx

        # HTTP status code specific non-retryable errors
        if hasattr(exception, "response") and hasattr(exception.response, "status_code"):
            status_code = exception.response.status_code
            # 4xx errors (except 429 rate limiting, 400 content filter triggered) are generally non-retryable
            if 400 < status_code < 500 and status_code != 429:
                return True

        # Specific HTTP status errors that are non-retryable
        if isinstance(exception, httpx.HTTPStatusError):
            status_code = exception.response.status_code
            if 400 < status_code < 500 and status_code != 429:
                return True

        # Authentication and permission errors
        auth_error_messages = ["authentication", "unauthorized", "forbidden", "access denied"]
        message = str(exception).lower()
        if any(keyword in message for keyword in auth_error_messages):
            return True

        # Configuration and validation errors
        config_error_messages = ["configuration", "invalid", "malformed", "bad request"]
        if any(keyword in message for keyword in config_error_messages):
            return True

        # File not found and similar errors
        if isinstance(exception, (FileNotFoundError, PermissionError)):
            return True

        return False

    def categorize_exception(self, exception: Exception) -> ErrorCategory:
        """Categorize an exception based on its type and message.

        :param exception: The exception to categorize
        :return: The appropriate error category
        """
        import httpx
        import httpcore

        # Network-related errors
        network_exceptions = (
            httpx.ConnectTimeout,
            httpx.ReadTimeout,
            httpx.ConnectError,
            httpx.HTTPError,
            httpx.TimeoutException,
            httpcore.ReadTimeout,
            ConnectionError,
            ConnectionRefusedError,
            ConnectionResetError,
        )

        if isinstance(exception, network_exceptions):
            return ErrorCategory.NETWORK

        # Timeout errors (separate from network to handle asyncio.TimeoutError)
        if isinstance(exception, (TimeoutError, asyncio.TimeoutError)):
            return ErrorCategory.TIMEOUT

        # File I/O errors
        if isinstance(exception, (IOError, OSError, FileNotFoundError, PermissionError)):
            return ErrorCategory.FILE_IO

        # HTTP status code specific errors
        if hasattr(exception, "response") and hasattr(exception.response, "status_code"):
            status_code = exception.response.status_code
            if 500 <= status_code < 600:
                return ErrorCategory.NETWORK
            elif status_code == 401:
                return ErrorCategory.AUTHENTICATION
            elif status_code == 403:
                return ErrorCategory.CONFIGURATION

        # String-based categorization
        message = str(exception).lower()

        # Define keyword mappings for cleaner logic
        keyword_mappings = {
            ErrorCategory.AUTHENTICATION: ["authentication", "unauthorized"],
            ErrorCategory.CONFIGURATION: ["configuration", "config"],
            ErrorCategory.ORCHESTRATOR: ["orchestrator"],
            ErrorCategory.EVALUATION: ["evaluation", "evaluate", "model_error"],
            ErrorCategory.DATA_PROCESSING: ["data", "json"],
        }

        for category, keywords in keyword_mappings.items():
            if any(keyword in message for keyword in keywords):
                return category

        return ErrorCategory.UNKNOWN

    def determine_severity(
        self, exception: Exception, category: ErrorCategory, context: Optional[Dict[str, Any]] = None
    ) -> ErrorSeverity:
        """Determine the severity of an exception.

        :param exception: The exception to evaluate
        :param category: The error category
        :param context: Additional context for severity determination
        :return: The appropriate error severity
        """
        context = context or {}

        # Critical system errors
        if isinstance(exception, (MemoryError, SystemExit, KeyboardInterrupt)):
            return ErrorSeverity.FATAL

        # Authentication and configuration are typically high severity
        if category in (ErrorCategory.AUTHENTICATION, ErrorCategory.CONFIGURATION):
            return ErrorSeverity.HIGH

        # File I/O errors can be high severity if they involve critical files
        if category == ErrorCategory.FILE_IO:
            if context.get("critical_file", False):
                return ErrorSeverity.HIGH
            return ErrorSeverity.MEDIUM

        # Network and timeout errors are usually medium severity (retryable)
        if category in (ErrorCategory.NETWORK, ErrorCategory.TIMEOUT):
            return ErrorSeverity.MEDIUM

        # Task-specific errors are medium severity
        if category in (ErrorCategory.ORCHESTRATOR, ErrorCategory.EVALUATION, ErrorCategory.DATA_PROCESSING):
            return ErrorSeverity.MEDIUM

        return ErrorSeverity.LOW

    def handle_exception(
        self,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None,
        task_name: Optional[str] = None,
        reraise: bool = False,
    ) -> RedTeamError:
        """Handle an exception with proper categorization and logging.

        :param exception: The exception to handle
        :param context: Additional context information
        :param task_name: Name of the task where the exception occurred
        :param reraise: Whether to reraise the exception after handling
        :return: A RedTeamError with categorized information
        """
        context = context or {}

        # If it's already a RedTeamError, just log and return/reraise
        if isinstance(exception, RedTeamError):
            self._log_error(exception, task_name)
            if reraise:
                raise exception
            return exception

        # Check if this is a non-retryable error that should fail immediately
        if self.is_non_retryable_error(exception):
            category = self.categorize_exception(exception)

            # Create a NonRetryableError to signal immediate failure
            message = f"Non-retryable {category.value} error"
            if task_name:
                message += f" in {task_name}"
            message += f": {str(exception)}"

            non_retryable_error = NonRetryableError(
                message=message, category=category, context=context, original_exception=exception
            )

            # Update error counts
            self.error_counts[category] += 1

            # Log the error
            self._log_error(non_retryable_error, task_name)

            if reraise:
                raise non_retryable_error
            return non_retryable_error

        # Categorize the exception
        category = self.categorize_exception(exception)
        severity = self.determine_severity(exception, category, context)

        # Update error counts
        self.error_counts[category] += 1

        # Create RedTeamError
        message = f"{category.value.title()} error"
        if task_name:
            message += f" in {task_name}"
        message += f": {str(exception)}"

        red_team_error = RedTeamError(
            message=message, category=category, severity=severity, context=context, original_exception=exception
        )

        # Log the error
        self._log_error(red_team_error, task_name)

        if reraise:
            raise red_team_error

        return red_team_error

    def _log_error(self, error: RedTeamError, task_name: Optional[str] = None) -> None:
        """Log an error with appropriate level based on severity.

        :param error: The RedTeamError to log
        :param task_name: Optional task name for context
        """
        # Determine log level based on severity
        if error.severity == ErrorSeverity.FATAL:
            log_level = logging.CRITICAL
        elif error.severity == ErrorSeverity.HIGH:
            log_level = logging.ERROR
        elif error.severity == ErrorSeverity.MEDIUM:
            log_level = logging.WARNING
        else:
            log_level = logging.INFO

        # Create log message
        message_parts = []
        if task_name:
            message_parts.append(f"[{task_name}]")
        message_parts.append(f"[{error.category.value}]")
        message_parts.append(f"[{error.severity.value}]")
        message_parts.append(error.message)

        log_message = " ".join(message_parts)

        # Log with appropriate level
        self.logger.log(log_level, log_message)

        # Log additional context if available
        if error.context:
            self.logger.debug(f"Error context: {error.context}")

        # Log original exception traceback for debugging
        if error.original_exception and self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(f"Original exception traceback:\n{traceback.format_exc()}")

    def should_abort_scan(self) -> bool:
        """Determine if the scan should be aborted based on error patterns.

        :return: True if the scan should be aborted
        """
        # Abort if we have too many high-severity errors
        high_severity_categories = [ErrorCategory.AUTHENTICATION, ErrorCategory.CONFIGURATION]
        high_severity_count = sum(self.error_counts[cat] for cat in high_severity_categories)

        if high_severity_count > 2:
            return True

        # Abort if we have too many network errors (indicates systemic issue)
        if self.error_counts[ErrorCategory.NETWORK] > 10:
            return True

        return False

    def get_error_summary(self) -> Dict[str, Any]:
        """Get a summary of all errors encountered.

        :return: Dictionary containing error statistics
        """
        total_errors = sum(self.error_counts.values())

        return {
            "total_errors": total_errors,
            "error_counts_by_category": dict(self.error_counts),
            "most_common_category": max(self.error_counts, key=self.error_counts.get) if total_errors > 0 else None,
            "should_abort": self.should_abort_scan(),
        }

    def log_error_summary(self) -> None:
        """Log a summary of all errors encountered."""
        summary = self.get_error_summary()

        if summary["total_errors"] == 0:
            self.logger.info("No errors encountered during operation")
            return

        self.logger.info(f"Error Summary: {summary['total_errors']} total errors")

        for category, count in summary["error_counts_by_category"].items():
            if count > 0:
                self.logger.info(f"  {category}: {count}")

        if summary["most_common_category"]:
            self.logger.info(f"Most common error type: {summary['most_common_category']}")


def create_exception_handler(logger: Optional[logging.Logger] = None) -> ExceptionHandler:
    """Create an ExceptionHandler instance.

    :param logger: Logger instance for error reporting
    :return: Configured ExceptionHandler
    """
    return ExceptionHandler(logger=logger)


# Convenience context manager for handling exceptions
class exception_context:
    """Context manager for handling exceptions in Red Team operations."""

    def __init__(
        self,
        handler: ExceptionHandler,
        task_name: str,
        context: Optional[Dict[str, Any]] = None,
        reraise_fatal: bool = True,
    ):
        self.handler = handler
        self.task_name = task_name
        self.context = context or {}
        self.reraise_fatal = reraise_fatal
        self.error: Optional[RedTeamError] = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            self.error = self.handler.handle_exception(
                exception=exc_val, context=self.context, task_name=self.task_name, reraise=False
            )

            # Reraise fatal errors unless specifically disabled
            if self.reraise_fatal and self.error.severity == ErrorSeverity.FATAL:
                raise self.error

            # Suppress the original exception (we've handled it)
            return True
        return False
