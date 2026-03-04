# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Structured access logging for AgentServer.

Access logging is **disabled by default**. Enable it in one of two ways:

1. Set the environment variable ``AGENT_ENABLE_ACCESS_LOG=true``.
2. Pass ``enable_access_log=True`` to the :class:`AgentServer` constructor
   (constructor argument takes precedence over the env var).

When enabled, one structured log entry is emitted per HTTP request to the
``azure.ai.agentserver.access`` logger.

If ``python-json-logger`` is installed, log entries are formatted as JSON.
Otherwise, a ``key=value`` fallback format is used.  Install the optional
dependency::

    pip install azure-ai-agentserver[logging]
"""
from __future__ import annotations

import logging
import os
from typing import Optional

from ._constants import Constants

_HAS_JSON_LOGGER = False
_JsonFormatterClass: type | None = None
try:
    from pythonjsonlogger.json import JsonFormatter as _JsonFormatterImport

    _HAS_JSON_LOGGER = True
    _JsonFormatterClass = _JsonFormatterImport
except ImportError:
    pass

#: Dedicated logger name for access logs — separate from the library logger
#: so that operators can route, filter, or silence it independently.
_ACCESS_LOGGER_NAME = "azure.ai.agentserver.access"


class _KeyValueFormatter(logging.Formatter):
    """Simple structured formatter that emits ``key=value`` pairs.

    Used as a fallback when ``python-json-logger`` is not installed.
    """

    _FIELDS = (
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

    def format(self, record: logging.LogRecord) -> str:  # noqa: A003
        parts = [self.formatTime(record)]
        for field in self._FIELDS:
            value = getattr(record, field, None)
            if value is not None:
                parts.append(f"{field}={value}")
        return " ".join(parts)


class AccessLogHelper:
    """Structured access-log emitter.

    :param enabled: Explicit enable flag, or *None* to read from
        ``AGENT_ENABLE_ACCESS_LOG`` env var (default ``false``).
    :type enabled: Optional[bool]
    """

    def __init__(self, enabled: Optional[bool] = None) -> None:
        if enabled is None:
            enabled = os.getenv(Constants.AGENT_ENABLE_ACCESS_LOG, "false").lower() == "true"
        self._enabled = bool(enabled)
        self._logger: Optional[logging.Logger] = None

        if self._enabled:
            self._logger = logging.getLogger(_ACCESS_LOGGER_NAME)
            self._logger.setLevel(logging.INFO)
            # Only add a handler if one hasn't been configured by the caller
            if not self._logger.handlers:
                handler = logging.StreamHandler()
                if _HAS_JSON_LOGGER and _JsonFormatterClass is not None:
                    handler.setFormatter(
                        _JsonFormatterClass(
                            fmt="%(asctime)s %(levelname)s %(message)s",
                            rename_fields={"asctime": "timestamp", "levelname": "level"},
                        )
                    )
                else:
                    handler.setFormatter(_KeyValueFormatter())
                self._logger.addHandler(handler)

    @property
    def enabled(self) -> bool:
        """Whether access logging is active.

        :rtype: bool
        """
        return self._enabled

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
        if not self._enabled or self._logger is None:
            return
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
