# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Configuration resolution helpers for AgentServer.

Each ``resolve_*`` function follows the same hierarchy:
1. Explicit argument (if not *None*)
2. Environment variable
3. Built-in default

A value of ``0`` conventionally disables the corresponding feature.
"""
import logging
import os
from typing import Optional

from .._constants import Constants

logger = logging.getLogger("azure.ai.agentserver")


def resolve_port(port: Optional[int]) -> int:
    """Resolve the server port from argument, env var, or default.

    :param port: Explicitly requested port or None.
    :type port: Optional[int]
    :return: The resolved port number.
    :rtype: int
    """
    if port is not None:
        return port
    env_port = os.environ.get(Constants.AGENT_SERVER_PORT)
    if env_port:
        try:
            return int(env_port)
        except ValueError:
            logger.warning(
                "Invalid %s value '%s', falling back to default %s",
                Constants.AGENT_SERVER_PORT,
                env_port,
                Constants.DEFAULT_PORT,
            )
    return Constants.DEFAULT_PORT


def resolve_graceful_shutdown_timeout(timeout: Optional[int]) -> int:
    """Resolve the graceful shutdown timeout from argument, env var, or default.

    :param timeout: Explicitly requested timeout or None.
    :type timeout: Optional[int]
    :return: The resolved timeout in seconds.
    :rtype: int
    """
    if timeout is not None:
        return max(0, timeout)
    env_timeout = os.environ.get(Constants.AGENT_GRACEFUL_SHUTDOWN_TIMEOUT)
    if env_timeout:
        try:
            return max(0, int(env_timeout))
        except ValueError:
            logger.warning(
                "Invalid %s value '%s', falling back to default %s",
                Constants.AGENT_GRACEFUL_SHUTDOWN_TIMEOUT,
                env_timeout,
                Constants.DEFAULT_GRACEFUL_SHUTDOWN_TIMEOUT,
            )
    return Constants.DEFAULT_GRACEFUL_SHUTDOWN_TIMEOUT


def resolve_max_request_body_size(size: Optional[int]) -> int:
    """Resolve the max request body size from argument, env var, or default.

    :param size: Explicitly requested size in bytes or None.
    :type size: Optional[int]
    :return: The resolved max body size in bytes.
    :rtype: int
    """
    if size is not None:
        return max(0, size)
    env_size = os.environ.get(Constants.AGENT_MAX_REQUEST_BODY_SIZE)
    if env_size:
        try:
            return max(0, int(env_size))
        except ValueError:
            logger.warning(
                "Invalid %s value '%s', falling back to default %s",
                Constants.AGENT_MAX_REQUEST_BODY_SIZE,
                env_size,
                Constants.DEFAULT_MAX_REQUEST_BODY_SIZE,
            )
    return Constants.DEFAULT_MAX_REQUEST_BODY_SIZE


def resolve_request_timeout(timeout: Optional[int]) -> int:
    """Resolve the request timeout from argument, env var, or default.

    :param timeout: Explicitly requested timeout in seconds or None.
    :type timeout: Optional[int]
    :return: The resolved timeout in seconds.
    :rtype: int
    """
    if timeout is not None:
        return max(0, timeout)
    env_timeout = os.environ.get(Constants.AGENT_REQUEST_TIMEOUT)
    if env_timeout:
        try:
            return max(0, int(env_timeout))
        except ValueError:
            logger.warning(
                "Invalid %s value '%s', falling back to default %s",
                Constants.AGENT_REQUEST_TIMEOUT,
                env_timeout,
                Constants.DEFAULT_REQUEST_TIMEOUT,
            )
    return Constants.DEFAULT_REQUEST_TIMEOUT


def resolve_max_concurrent_requests(limit: Optional[int]) -> int:
    """Resolve the max concurrent requests from argument, env var, or default.

    :param limit: Explicitly requested concurrency limit or None.
    :type limit: Optional[int]
    :return: The resolved concurrency limit (0 = disabled).
    :rtype: int
    """
    if limit is not None:
        return max(0, limit)
    env_limit = os.environ.get(Constants.AGENT_MAX_CONCURRENT_REQUESTS)
    if env_limit:
        try:
            return max(0, int(env_limit))
        except ValueError:
            logger.warning(
                "Invalid %s value '%s', falling back to default %s",
                Constants.AGENT_MAX_CONCURRENT_REQUESTS,
                env_limit,
                Constants.DEFAULT_MAX_CONCURRENT_REQUESTS,
            )
    return Constants.DEFAULT_MAX_CONCURRENT_REQUESTS
