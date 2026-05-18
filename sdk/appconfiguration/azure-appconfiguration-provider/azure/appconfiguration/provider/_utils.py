# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import time
import datetime
import random
from typing import (
    Any,
    Dict,
    Mapping,
    Optional,
    Tuple,
)
from ._constants import (
    DEFAULT_STARTUP_TIMEOUT,
    MAX_STARTUP_BACKOFF_DURATION,
    MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION,
    JITTER_RATIO,
    STARTUP_BACKOFF_INTERVALS,
)


JSON = Mapping[str, Any]

min_uptime = 5


def delay_failure(start_time: datetime.datetime) -> None:
    """
    We want to make sure we are up a minimum amount of time before we kill the process.
    Otherwise, we could get stuck in a quick restart loop.

    :param start_time: The time when the process started.
    :type start_time: datetime.datetime
    """
    min_time = datetime.timedelta(seconds=min_uptime)
    current_time = datetime.datetime.now()
    if current_time - start_time < min_time:
        time.sleep((min_time - (current_time - start_time)).total_seconds())


def get_startup_backoff(elapsed_seconds: float, attempts: int) -> Tuple[float, bool]:
    """
    Get a backoff duration based on elapsed startup time.

    :param elapsed_seconds: The time elapsed since startup began, in seconds.
    :type elapsed_seconds: float
    :param attempts: The number of retry attempts made (1-based).
    :type attempts: int
    :return: A tuple where the first element is the backoff duration in seconds,
             and the second element indicates if the fixed backoff window has been exceeded.
    :rtype: Tuple[float, bool]
    """
    for threshold, backoff in STARTUP_BACKOFF_INTERVALS:
        if elapsed_seconds < threshold:
            return backoff, False
    return _calculate_backoff_duration(attempts), True


def process_load_parameters(*args, **kwargs: Any) -> Dict[str, Any]:
    """
    Process and validate all load function parameters in one place.
    This consolidates the most obviously duplicated logic from both sync and async load functions.

    :param args: Positional arguments, either endpoint and credential, or connection string.
    :type args: Any
    :return: Dictionary containing processed parameters
    :rtype: Dict[str, Any]
    """
    endpoint: Optional[str] = kwargs.pop("endpoint", None)
    credential = kwargs.pop("credential", None)
    connection_string: Optional[str] = kwargs.pop("connection_string", None)
    start_time = datetime.datetime.now()

    # Handle positional arguments
    if len(args) > 2:
        raise TypeError(
            "Unexpected positional parameters. Please pass either endpoint and credential, or a connection string."
        )
    if len(args) == 1:
        if endpoint is not None:
            raise TypeError("Received multiple values for parameter 'endpoint'.")
        endpoint = args[0]
    elif len(args) == 2:
        if credential is not None:
            raise TypeError("Received multiple values for parameter 'credential'.")
        endpoint, credential = args

    # Validate endpoint/credential vs connection_string
    if (endpoint or credential) and connection_string:
        raise ValueError("Please pass either endpoint and credential, or a connection string.")

    # Process Key Vault options in one place
    key_vault_options = kwargs.pop("key_vault_options", None)
    if key_vault_options:
        if "keyvault_credential" in kwargs or "secret_resolver" in kwargs or "keyvault_client_configs" in kwargs:
            raise ValueError(
                "Key Vault configurations should only be set by either the key_vault_options or kwargs not both."
            )
        kwargs["keyvault_credential"] = key_vault_options.credential
        kwargs["secret_resolver"] = key_vault_options.secret_resolver
        kwargs["keyvault_client_configs"] = key_vault_options.client_configs

    if kwargs.get("keyvault_credential") is not None and kwargs.get("secret_resolver") is not None:
        raise ValueError("A keyvault credential and secret resolver can't both be configured.")

    # Determine Key Vault usage
    uses_key_vault = (
        "keyvault_credential" in kwargs
        or "keyvault_client_configs" in kwargs
        or "secret_resolver" in kwargs
        or kwargs.get("uses_key_vault", False)
    )

    # Get startup timeout
    startup_timeout = kwargs.pop("startup_timeout", DEFAULT_STARTUP_TIMEOUT)
    if startup_timeout < 0:
        raise ValueError("Startup timeout must be greater than or equal to 0 seconds.")

    return {
        "endpoint": endpoint,
        "credential": credential,
        "connection_string": connection_string,
        "uses_key_vault": uses_key_vault,
        "start_time": start_time,
        "startup_timeout": startup_timeout,
        "kwargs": kwargs,
    }


def sdk_allowed_kwargs(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    allowed_kwargs = [
        "audience",
        "headers",
        "request_id",
        "user_agent",
        "logging_enable",
        "logger",
        "response_encoding",
        "raw_request_hook",
        "raw_response_hook",
        "network_span_namer",
        "tracing_attributes",
        "permit_redirects",
        "redirect_max",
        "retry_total",
        "retry_connect",
        "retry_read",
        "retry_status",
        "retry_backoff_factor",
        "retry_backoff_max",
        "retry_mode",
        "timeout",
        "connection_timeout",
        "read_timeout",
        "connection_verify",
        "connection_cert",
        "proxies",
        "cookies",
        "connection_data_block_size",
    ]
    return {k: v for k, v in kwargs.items() if k in allowed_kwargs}


def _jitter(duration: float, ratio: float = JITTER_RATIO) -> float:
    """
    Apply jitter to a duration value.

    :param duration: The base duration in seconds.
    :type duration: float
    :param ratio: The jitter ratio (0 to 1). Default is 0.25 (25% jitter means +/- 25% variation).
    :type ratio: float
    :return: The jittered duration in seconds.
    :rtype: float
    """
    if ratio < 0 or ratio > 1:
        raise ValueError("Jitter ratio must be between 0 and 1.")
    if ratio == 0:
        return duration
    jitter = ratio * (random.random() * 2 - 1)
    return duration * (1 + jitter)


def _calculate_backoff_duration(attempts: int) -> float:
    """
    Calculate the jittered exponential backoff duration.

    :param attempts: The number of retry attempts made, using a 0-based counter.
    :type attempts: int
    :return: The calculated backoff duration with jitter applied.
    :rtype: float
    """
    attempts += 1
    if attempts < 1:
        raise ValueError("Number of attempts must be at least 1.")

    if attempts == 1:
        return MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION

    # Calculate exponential backoff: min * 2^(attempts-1)
    # Cap the shift amount to prevent overflow
    safe_shift = min(attempts - 1, 63)
    calculated = MIN_STARTUP_EXPONENTIAL_BACKOFF_DURATION * (1 << safe_shift)

    # Cap at max duration
    if calculated > MAX_STARTUP_BACKOFF_DURATION or calculated <= 0:  # Check for overflow
        calculated = MAX_STARTUP_BACKOFF_DURATION

    return _jitter(calculated, JITTER_RATIO)
