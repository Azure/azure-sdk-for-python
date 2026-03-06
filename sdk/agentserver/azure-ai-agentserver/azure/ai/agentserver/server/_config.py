# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Configuration resolution helpers for AgentServer.

Each ``resolve_*`` function follows the same hierarchy:
1. Explicit argument (if not *None*)
2. Environment variable
3. Built-in default

A value of ``0`` conventionally disables the corresponding feature.

Invalid environment variable values raise ``ValueError`` immediately so
misconfiguration is surfaced at startup rather than silently masked.
"""
import os
from typing import Optional

from .._constants import Constants


def _parse_int_env(var_name: str) -> Optional[int]:
    """Parse an integer environment variable, raising on invalid values.

    :param var_name: Name of the environment variable.
    :type var_name: str
    :return: The parsed integer or None if the variable is not set.
    :rtype: Optional[int]
    :raises ValueError: If the variable is set but cannot be parsed as an integer.
    """
    raw = os.environ.get(var_name)
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        raise ValueError(
            f"Invalid value for {var_name}: {raw!r} (expected an integer)"
        ) from None


def _require_int(name: str, value: object) -> int:
    """Validate that *value* is an integer.

    :param name: Human-readable parameter/env-var name for the error message.
    :type name: str
    :param value: The value to validate.
    :type value: object
    :return: The value cast to int.
    :rtype: int
    :raises ValueError: If *value* is not an integer.
    """
    if not isinstance(value, int):
        raise ValueError(
            f"Invalid value for {name}: {value!r} (expected an integer)"
        )
    return value


def resolve_port(port: Optional[int]) -> int:
    """Resolve the server port from argument, env var, or default.

    :param port: Explicitly requested port or None.
    :type port: Optional[int]
    :return: The resolved port number.
    :rtype: int
    :raises ValueError: If the port value is not a valid integer or is outside 1-65535.
    """
    if port is not None:
        result = _require_int("port", port)
        if not 1 <= result <= 65535:
            raise ValueError(
                f"Invalid value for port: {result} (expected 1-65535)"
            )
        return result
    env_port = _parse_int_env(Constants.AGENT_SERVER_PORT)
    if env_port is not None:
        if not 1 <= env_port <= 65535:
            raise ValueError(
                f"Invalid value for {Constants.AGENT_SERVER_PORT}: {env_port} (expected 1-65535)"
            )
        return env_port
    return Constants.DEFAULT_PORT


def resolve_graceful_shutdown_timeout(timeout: Optional[int]) -> int:
    """Resolve the graceful shutdown timeout from argument, env var, or default.

    :param timeout: Explicitly requested timeout or None.
    :type timeout: Optional[int]
    :return: The resolved timeout in seconds.
    :rtype: int
    :raises ValueError: If the env var is not a valid integer.
    """
    if timeout is not None:
        return max(0, _require_int("timeout_graceful_shutdown", timeout))
    env_timeout = _parse_int_env(Constants.AGENT_GRACEFUL_SHUTDOWN_TIMEOUT)
    if env_timeout is not None:
        return max(0, env_timeout)
    return Constants.DEFAULT_GRACEFUL_SHUTDOWN_TIMEOUT


def resolve_max_request_body_size(size: Optional[int]) -> int:
    """Resolve the max request body size from argument, env var, or default.

    :param size: Explicitly requested size in bytes or None.
    :type size: Optional[int]
    :return: The resolved max body size in bytes.
    :rtype: int
    :raises ValueError: If the env var is not a valid integer.
    """
    if size is not None:
        return max(0, _require_int("max_request_body_size", size))
    env_size = _parse_int_env(Constants.AGENT_MAX_REQUEST_BODY_SIZE)
    if env_size is not None:
        return max(0, env_size)
    return Constants.DEFAULT_MAX_REQUEST_BODY_SIZE


def resolve_request_timeout(timeout: Optional[int]) -> int:
    """Resolve the request timeout from argument, env var, or default.

    :param timeout: Explicitly requested timeout in seconds or None.
    :type timeout: Optional[int]
    :return: The resolved timeout in seconds.
    :rtype: int
    :raises ValueError: If the env var is not a valid integer.
    """
    if timeout is not None:
        return max(0, _require_int("request_timeout", timeout))
    env_timeout = _parse_int_env(Constants.AGENT_REQUEST_TIMEOUT)
    if env_timeout is not None:
        return max(0, env_timeout)
    return Constants.DEFAULT_REQUEST_TIMEOUT


def resolve_max_concurrent_requests(limit: Optional[int]) -> int:
    """Resolve the max concurrent requests from argument, env var, or default.

    :param limit: Explicitly requested concurrency limit or None.
    :type limit: Optional[int]
    :return: The resolved concurrency limit (0 = disabled).
    :rtype: int
    :raises ValueError: If the env var is not a valid integer.
    """
    if limit is not None:
        return max(0, _require_int("max_concurrent_requests", limit))
    env_limit = _parse_int_env(Constants.AGENT_MAX_CONCURRENT_REQUESTS)
    if env_limit is not None:
        return max(0, env_limit)
    return Constants.DEFAULT_MAX_CONCURRENT_REQUESTS


def resolve_bool_feature(value: Optional[bool], env_var: str) -> bool:
    """Resolve an opt-in boolean feature from argument, env var, or default (False).

    :param value: Explicitly requested value or None.
    :type value: Optional[bool]
    :param env_var: Name of the environment variable to consult.
    :type env_var: str
    :return: Whether the feature is enabled.
    :rtype: bool
    """
    if value is not None:
        return bool(value)
    return os.environ.get(env_var, "").lower() == "true"


_VALID_LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


def resolve_log_level(level: Optional[str]) -> str:
    """Resolve the library log level from argument, env var, or default (``WARNING``).

    :param level: Explicitly requested level (e.g. ``"DEBUG"``) or None.
    :type level: Optional[str]
    :return: Validated, upper-cased log level string.
    :rtype: str
    :raises ValueError: If the value is not one of DEBUG/INFO/WARNING/ERROR/CRITICAL.
    """
    if level is not None:
        normalized = level.upper()
    else:
        normalized = os.environ.get(Constants.AGENT_LOG_LEVEL, "WARNING").upper()
    if normalized not in _VALID_LOG_LEVELS:
        raise ValueError(
            f"Invalid log level: {normalized!r} "
            f"(expected one of {', '.join(_VALID_LOG_LEVELS)})"
        )
    return normalized
