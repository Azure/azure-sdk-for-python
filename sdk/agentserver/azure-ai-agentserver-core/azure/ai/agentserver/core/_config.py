# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Configuration resolution helpers for AgentHost hosting.

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

from ._constants import Constants


def _parse_int_env(var_name: str) -> Optional[int]:
    """Parse an integer environment variable, raising on invalid values.

    :param var_name: Name of the environment variable.
    :type var_name: str
    :return: The parsed integer or None if the variable is not set.
    :rtype: Optional[int]
    :raises ValueError: If the variable is set but cannot be parsed as an integer.
    """
    raw = os.environ.get(var_name)
    if raw is None:
        return None
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(
            f"Invalid value for {var_name}: {raw!r} (expected an integer)"
        ) from exc


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
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(
            f"Invalid value for {name}: {value!r} (expected an integer)"
        )
    return value


def _validate_port(value: int, source: str) -> int:
    """Validate that a port number is within the valid range.

    :param value: The port number to validate.
    :type value: int
    :param source: Human-readable source name for the error message.
    :type source: str
    :return: The validated port number.
    :rtype: int
    :raises ValueError: If the port is outside 1-65535.
    """
    if not 1 <= value <= 65535:
        raise ValueError(
            f"Invalid value for {source}: {value} (expected 1-65535)"
        )
    return value


def resolve_port(port: Optional[int]) -> int:
    """Resolve the server port from argument, env var, or default.

    Resolution order: explicit *port* → ``PORT`` env var → ``8088``.

    :param port: Explicitly requested port or None.
    :type port: Optional[int]
    :return: The resolved port number.
    :rtype: int
    :raises ValueError: If the port value is not a valid integer or is outside 1-65535.
    """
    if port is not None:
        return _validate_port(_require_int("port", port), "port")
    env_port = _parse_int_env(Constants.PORT)
    if env_port is not None:
        return _validate_port(env_port, Constants.PORT)
    return Constants.DEFAULT_PORT


_DEFAULT_GRACEFUL_SHUTDOWN_TIMEOUT = 30


def resolve_graceful_shutdown_timeout(timeout: Optional[int]) -> int:
    """Resolve the graceful shutdown timeout from argument or default.

    :param timeout: Explicitly requested timeout or None.
    :type timeout: Optional[int]
    :return: The resolved timeout in seconds (default 30).
    :rtype: int
    """
    if timeout is not None:
        return max(0, _require_int("graceful_shutdown_timeout", timeout))
    return _DEFAULT_GRACEFUL_SHUTDOWN_TIMEOUT


_VALID_LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


def resolve_appinsights_connection_string(
    connection_string: Optional[str],
) -> Optional[str]:
    """Resolve the Application Insights connection string.

    Resolution order:

    1. Explicit *connection_string* argument (if not *None*).
    2. ``APPLICATIONINSIGHTS_CONNECTION_STRING`` env var (standard Azure
       Monitor convention).
    3. *None* — no connection string available.

    :param connection_string: Explicitly provided connection string or None.
    :type connection_string: Optional[str]
    :return: The resolved connection string, or None.
    :rtype: Optional[str]
    """
    if connection_string is not None:
        return connection_string
    return os.environ.get(
        Constants.APPLICATIONINSIGHTS_CONNECTION_STRING
    )


def resolve_log_level(level: Optional[str]) -> str:
    """Resolve the library log level from argument or default (``INFO``).

    :param level: Explicitly requested level (e.g. ``"DEBUG"``) or None.
    :type level: Optional[str]
    :return: Validated, upper-cased log level string.
    :rtype: str
    :raises ValueError: If the value is not one of DEBUG/INFO/WARNING/ERROR/CRITICAL.
    """
    if level is not None:
        normalized = level.upper()
    else:
        normalized = "INFO"
    if normalized not in _VALID_LOG_LEVELS:
        raise ValueError(
            f"Invalid log level: {normalized!r} "
            f"(expected one of {', '.join(_VALID_LOG_LEVELS)})"
        )
    return normalized


def resolve_agent_name() -> str:
    """Resolve the agent name from the ``FOUNDRY_AGENT_NAME`` environment variable.

    :return: The agent name, or an empty string if not set.
    :rtype: str
    """
    return os.environ.get(Constants.FOUNDRY_AGENT_NAME, "")


def resolve_agent_version() -> str:
    """Resolve the agent version from the ``FOUNDRY_AGENT_VERSION`` environment variable.

    :return: The agent version, or an empty string if not set.
    :rtype: str
    """
    return os.environ.get(Constants.FOUNDRY_AGENT_VERSION, "")


def resolve_project_id() -> str:
    """Resolve the Foundry project ARM resource ID from the ``FOUNDRY_PROJECT_ARM_ID`` environment variable.

    The UX queries spans using this ID, so it must be present in trace
    attributes for portal integration.

    :return: The project ARM resource ID, or an empty string if not set.
    :rtype: str
    """
    return os.environ.get(Constants.FOUNDRY_PROJECT_ARM_ID, "")


def resolve_otlp_endpoint() -> Optional[str]:
    """Resolve the OTLP exporter endpoint from the ``OTEL_EXPORTER_OTLP_ENDPOINT`` environment variable.

    :return: The OTLP endpoint URL, or None if not set or empty.
    :rtype: Optional[str]
    """
    value = os.environ.get(Constants.OTEL_EXPORTER_OTLP_ENDPOINT, "")
    return value if value else None
