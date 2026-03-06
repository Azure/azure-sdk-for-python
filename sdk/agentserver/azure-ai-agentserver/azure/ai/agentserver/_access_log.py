# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Structured access logging for AgentServer.

Access logging is **disabled by default**. Enable it in one of two ways:

1. Set the environment variable ``AGENT_ENABLE_ACCESS_LOG=true``.
2. Pass ``enable_access_log=True`` to the :class:`AgentServer` constructor
   (constructor argument takes precedence over the env var).

When enabled, one structured log entry is emitted per HTTP request to the
``azure.ai.agentserver.access`` logger.  Each entry is formatted as a JSON
object using only the Python standard library.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Optional

from ._constants import Constants

#: Dedicated logger name for access logs — separate from the library logger
#: so that operators can route, filter, or silence it independently.
_ACCESS_LOGGER_NAME = "azure.ai.agentserver.access"

_STRUCTURED_FIELDS = (
    "method",
    "path",
    "status",
    "protocol",
    "duration_ms",
    "request_size",
    "response_size",
    "invocation_id",
    "client_ip",
    "user_agent",
)


class _JsonFormatter(logging.Formatter):
    """Emit each log record as a single-line JSON object.

    Uses only the Python standard library — no external dependencies.
    """

    def format(self, record: logging.LogRecord) -> str:  # noqa: A003
        entry: dict[str, object] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        for field in _STRUCTURED_FIELDS:
            value = getattr(record, field, None)
            if value is not None:
                entry[field] = value
        return json.dumps(entry, default=str)


class AccessLogHelper:
    """Structured access-log emitter.

    Only instantiate when access logging is enabled.
    """

    def __init__(self) -> None:
        self._logger = logging.getLogger(_ACCESS_LOGGER_NAME)
        self._logger.setLevel(logging.INFO)
        # Only add a handler if one hasn't been configured by the caller
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(_JsonFormatter())
            self._logger.addHandler(handler)

    def log_request(
        self,
        method: str,
        path: str,
        status: int,
        duration_ms: float,
        request_size: int,
        response_size: int,
        invocation_id: str,
        client_ip: str,
        user_agent: str,
        protocol: str = "HTTP/1.1",
    ) -> None:
        """Emit a structured log entry for one completed HTTP request.

        :param method: HTTP method (e.g. ``"POST"``).
        :type method: str
        :param path: Request path (e.g. ``"/invocations"``).
        :type path: str
        :param status: HTTP status code.
        :type status: int
        :param duration_ms: Request duration in milliseconds.
        :type duration_ms: float
        :param request_size: Request body size in bytes.
        :type request_size: int
        :param response_size: Response body size in bytes.
        :type response_size: int
        :param invocation_id: The ``x-agent-invocation-id`` value.
        :type invocation_id: str
        :param client_ip: Client IP address.
        :type client_ip: str
        :param user_agent: Client User-Agent header.
        :type user_agent: str
        :param protocol: HTTP protocol version (e.g. ``"HTTP/1.1"``, ``"HTTP/2"``).
        :type protocol: str
        """
        self._logger.info(
            "%s %s %s %d %.1fms",
            method,
            path,
            protocol,
            status,
            duration_ms,
            extra={
                "method": method,
                "path": path,
                "status": status,
                "protocol": protocol,
                "duration_ms": round(duration_ms, 2),
                "request_size": request_size,
                "response_size": response_size,
                "invocation_id": invocation_id,
                "client_ip": client_ip,
                "user_agent": user_agent,
            },
        )
