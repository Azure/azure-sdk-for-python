# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Retry utilities for Red Team Agent.

This module provides centralized retry logic and decorators for handling
network errors and other transient failures consistently across the codebase.
"""

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional, TypeVar
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception,
    RetryError,
)

# Retry imports for exception handling
import httpx
import httpcore

# Import Azure exceptions if available
try:
    from azure.core.exceptions import ServiceRequestError, ServiceResponseError

    AZURE_EXCEPTIONS = (ServiceRequestError, ServiceResponseError)
except ImportError:
    AZURE_EXCEPTIONS = ()


# Type variable for generic retry decorators
T = TypeVar("T")


class RetryManager:
    """Centralized retry management for Red Team operations."""

    # Default retry configuration
    DEFAULT_MAX_ATTEMPTS = 5
    DEFAULT_MIN_WAIT = 2
    DEFAULT_MAX_WAIT = 30
    DEFAULT_MULTIPLIER = 1.5

    # Network-related exceptions that should trigger retries
    NETWORK_EXCEPTIONS = (
        httpx.ConnectTimeout,
        httpx.ReadTimeout,
        httpx.ConnectError,
        httpx.HTTPError,
        httpx.TimeoutException,
        httpx.HTTPStatusError,
        httpcore.ReadTimeout,
        ConnectionError,
        ConnectionRefusedError,
        ConnectionResetError,
        TimeoutError,
        OSError,
        IOError,
        asyncio.TimeoutError,
    ) + AZURE_EXCEPTIONS

    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
        min_wait: int = DEFAULT_MIN_WAIT,
        max_wait: int = DEFAULT_MAX_WAIT,
        multiplier: float = DEFAULT_MULTIPLIER,
    ):
        """Initialize retry manager.

        :param logger: Logger instance for retry messages
        :param max_attempts: Maximum number of retry attempts
        :param min_wait: Minimum wait time between retries (seconds)
        :param max_wait: Maximum wait time between retries (seconds)
        :param multiplier: Exponential backoff multiplier
        """
        self.logger = logger or logging.getLogger(__name__)
        self.max_attempts = max_attempts
        self.min_wait = min_wait
        self.max_wait = max_wait
        self.multiplier = multiplier

    def should_retry_exception(self, exception: Exception) -> bool:
        """Determine if an exception should trigger a retry.

        :param exception: The exception to check
        :return: True if the exception should trigger a retry
        """
        if isinstance(exception, self.NETWORK_EXCEPTIONS):
            return True

        # Special case for HTTP status errors
        if isinstance(exception, httpx.HTTPStatusError):
            return exception.response.status_code == 500 or "model_error" in str(
                exception
            )

        return False

    def log_retry_attempt(self, retry_state) -> None:
        """Log retry attempts for visibility.

        :param retry_state: The retry state object from tenacity
        """
        exception = retry_state.outcome.exception()
        if exception:
            self.logger.warning(
                f"Retry attempt {retry_state.attempt_number}/{self.max_attempts}: "
                f"{exception.__class__.__name__} - {str(exception)}. "
                f"Retrying in {retry_state.next_action.sleep} seconds..."
            )

    def log_retry_error(self, retry_state) -> Exception:
        """Log the final error after all retries failed.

        :param retry_state: The retry state object from tenacity
        :return: The final exception
        """
        exception = retry_state.outcome.exception()
        self.logger.error(
            f"All retries failed after {retry_state.attempt_number} attempts. "
            f"Final error: {exception.__class__.__name__}: {str(exception)}"
        )
        return exception

    def create_retry_decorator(self, context: str = "") -> Callable:
        """Create a retry decorator with the configured settings.

        :param context: Optional context string for logging
        :return: Configured retry decorator
        """
        context_prefix = f"[{context}] " if context else ""

        def log_attempt(retry_state):
            exception = retry_state.outcome.exception()
            if exception:
                self.logger.warning(
                    f"{context_prefix}Retry attempt {retry_state.attempt_number}/{self.max_attempts}: "
                    f"{exception.__class__.__name__} - {str(exception)}. "
                    f"Retrying in {retry_state.next_action.sleep} seconds..."
                )

        def log_final_error(retry_state):
            exception = retry_state.outcome.exception()
            self.logger.error(
                f"{context_prefix}All retries failed after {retry_state.attempt_number} attempts. "
                f"Final error: {exception.__class__.__name__}: {str(exception)}"
            )
            return exception

        return retry(
            retry=retry_if_exception(self.should_retry_exception),
            stop=stop_after_attempt(self.max_attempts),
            wait=wait_exponential(
                multiplier=self.multiplier,
                min=self.min_wait,
                max=self.max_wait,
            ),
            before_sleep=log_attempt,
            retry_error_callback=log_final_error,
        )

    def get_retry_config(self) -> Dict[str, Any]:
        """Get retry configuration dictionary for backward compatibility.

        :return: Dictionary containing retry configuration
        """
        return {
            "network_retry": {
                "retry": retry_if_exception(self.should_retry_exception),
                "stop": stop_after_attempt(self.max_attempts),
                "wait": wait_exponential(
                    multiplier=self.multiplier,
                    min=self.min_wait,
                    max=self.max_wait,
                ),
                "retry_error_callback": self.log_retry_error,
                "before_sleep": self.log_retry_attempt,
            }
        }


def create_standard_retry_manager(
    logger: Optional[logging.Logger] = None,
) -> RetryManager:
    """Create a standard retry manager with default settings.

    :param logger: Optional logger instance
    :return: Configured RetryManager instance
    """
    return RetryManager(logger=logger)


# Convenience function for creating retry decorators
def create_retry_decorator(
    logger: Optional[logging.Logger] = None,
    context: str = "",
    max_attempts: int = RetryManager.DEFAULT_MAX_ATTEMPTS,
    min_wait: int = RetryManager.DEFAULT_MIN_WAIT,
    max_wait: int = RetryManager.DEFAULT_MAX_WAIT,
) -> Callable:
    """Create a retry decorator with specified parameters.

    :param logger: Optional logger instance
    :param context: Optional context for logging
    :param max_attempts: Maximum retry attempts
    :param min_wait: Minimum wait time between retries
    :param max_wait: Maximum wait time between retries
    :return: Configured retry decorator
    """
    retry_manager = RetryManager(
        logger=logger,
        max_attempts=max_attempts,
        min_wait=min_wait,
        max_wait=max_wait,
    )
    return retry_manager.create_retry_decorator(context)
