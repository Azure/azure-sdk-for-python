"""
Retry configuration and utilities for Red Team Agent.

This module provides standardized retry configurations and logging functions
for handling connection and network-related errors.
"""

import asyncio
import httpx
import httpcore
from tenacity import retry_if_exception, stop_after_attempt, wait_exponential
from azure.core.exceptions import ServiceRequestError, ServiceResponseError


# Default retry configuration constants
MAX_RETRY_ATTEMPTS = 3
MIN_RETRY_WAIT_SECONDS = 2
MAX_RETRY_WAIT_SECONDS = 60


def create_retry_config(
    max_retry_attempts: int = MAX_RETRY_ATTEMPTS,
    min_retry_wait_seconds: int = MIN_RETRY_WAIT_SECONDS, 
    max_retry_wait_seconds: int = MAX_RETRY_WAIT_SECONDS,
    log_retry_attempt_func=None,
    log_retry_error_func=None,
):
    """Create a standard retry configuration for connection-related issues.

    Creates a dictionary with retry configurations for various network and connection-related
    exceptions. The configuration includes retry predicates, stop conditions, wait strategies,
    and callback functions for logging retry attempts.

    :param max_retry_attempts: Maximum number of retry attempts
    :type max_retry_attempts: int
    :param min_retry_wait_seconds: Minimum wait time between retries
    :type min_retry_wait_seconds: int
    :param max_retry_wait_seconds: Maximum wait time between retries
    :type max_retry_wait_seconds: int
    :param log_retry_attempt_func: Function to call when logging retry attempts
    :type log_retry_attempt_func: callable
    :param log_retry_error_func: Function to call when logging retry errors
    :type log_retry_error_func: callable
    :return: Dictionary with retry configuration for different exception types
    :rtype: dict
    """
    return {  # For connection timeouts and network-related errors
        "network_retry": {
            "retry": retry_if_exception(
                lambda e: isinstance(
                    e,
                    (
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
                        ServiceRequestError,
                        ServiceResponseError,
                    ),
                )
                or (
                    isinstance(e, httpx.HTTPStatusError)
                    and (e.response.status_code == 500 or "model_error" in str(e))
                )
            ),
            "stop": stop_after_attempt(max_retry_attempts),
            "wait": wait_exponential(
                multiplier=1.5, min=min_retry_wait_seconds, max=max_retry_wait_seconds
            ),
            "retry_error_callback": log_retry_error_func,
            "before_sleep": log_retry_attempt_func,
        }
    }


def log_retry_attempt(logger, max_retry_attempts: int = MAX_RETRY_ATTEMPTS):
    """Create a retry attempt logging function.

    Returns a function that logs retry attempts for better visibility.
    Logs information about connection issues that trigger retry attempts, including the
    exception type, retry count, and wait time before the next attempt.

    :param logger: Logger instance to use for logging
    :type logger: logging.Logger
    :param max_retry_attempts: Maximum number of retry attempts
    :type max_retry_attempts: int
    :return: Function that can be used as a retry callback
    :rtype: callable
    """
    def _log_retry_attempt(retry_state):
        exception = retry_state.outcome.exception()
        if exception:
            logger.warning(
                f"Connection issue: {exception.__class__.__name__}. "
                f"Retrying in {retry_state.next_action.sleep} seconds... "
                f"(Attempt {retry_state.attempt_number}/{max_retry_attempts})"
            )
    return _log_retry_attempt


def log_retry_error(logger):
    """Create a retry error logging function.

    Returns a function that logs the final error after all retries have been exhausted.
    Logs detailed information about the error that persisted after all retry attempts have been exhausted.
    This provides visibility into what ultimately failed and why.

    :param logger: Logger instance to use for logging
    :type logger: logging.Logger
    :return: Function that can be used as a retry error callback
    :rtype: callable
    """
    def _log_retry_error(retry_state):
        exception = retry_state.outcome.exception()
        logger.error(
            f"All retries failed after {retry_state.attempt_number} attempts. "
            f"Last error: {exception.__class__.__name__}: {str(exception)}"
        )
        return exception
    return _log_retry_error