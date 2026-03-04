# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Optional Prometheus metrics for AgentServer.

Metrics collection is **disabled by default**. Enable it in one of two ways:

1. Set the environment variable ``AGENT_ENABLE_METRICS=true``.
2. Pass ``enable_metrics=True`` to the :class:`AgentServer` constructor
   (constructor argument takes precedence over the env var).

When enabled, the module requires ``prometheus_client`` to be installed::

    pip install azure-ai-agentserver[metrics]

If the package is not installed, metrics silently becomes a no-op.
A ``/metrics`` endpoint is added to the server that returns Prometheus
text exposition format.
"""
from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Any, Optional

from ._constants import Constants

logger = logging.getLogger("azure.ai.agentserver")

_HAS_PROMETHEUS = False
try:
    from prometheus_client import (
        CollectorRegistry,
        Counter,
        Gauge,
        Histogram,
        generate_latest,
    )

    _HAS_PROMETHEUS = True
except ImportError:
    if TYPE_CHECKING:
        from prometheus_client import (  # type: ignore[assignment]
            CollectorRegistry,
            Counter,
            Gauge,
            Histogram,
            generate_latest,
        )

#: Default histogram buckets (seconds) — tuned for HTTP/LLM workloads
#: that commonly range from 10 ms to several minutes.
_DURATION_BUCKETS = (
    0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75,
    1.0, 2.5, 5.0, 7.5, 10.0, 30.0, 60.0, 120.0, 300.0,
)

#: Body-size histogram buckets (bytes) — from 100 B to 100 MB.
_SIZE_BUCKETS = (
    100, 1_000, 10_000, 100_000, 500_000,
    1_000_000, 5_000_000, 10_000_000, 50_000_000, 100_000_000,
)


class MetricsHelper:
    """Lightweight wrapper around ``prometheus_client`` that can be a complete no-op.

    :param enabled: Explicit enable flag, or *None* to read from
        ``AGENT_ENABLE_METRICS`` env var (default ``false``).
    :type enabled: Optional[bool]
    """

    def __init__(self, enabled: Optional[bool] = None) -> None:
        if enabled is None:
            enabled = os.getenv(Constants.AGENT_ENABLE_METRICS, "false").lower() == "true"
        self._enabled = enabled and _HAS_PROMETHEUS
        self._registry: Any = None
        self._request_total: Any = None
        self._request_duration: Any = None
        self._request_in_flight: Any = None
        self._request_body_bytes: Any = None
        self._response_body_bytes: Any = None

        if self._enabled:
            self._registry = CollectorRegistry()
            self._request_total = Counter(
                "agent_request_total",
                "Total HTTP requests processed",
                labelnames=["method", "path", "status"],
                registry=self._registry,
            )
            self._request_duration = Histogram(
                "agent_request_duration_seconds",
                "Request duration in seconds",
                labelnames=["method", "path", "status"],
                buckets=_DURATION_BUCKETS,
                registry=self._registry,
            )
            self._request_in_flight = Gauge(
                "agent_request_in_flight",
                "Number of requests currently being processed",
                registry=self._registry,
            )
            self._request_body_bytes = Histogram(
                "agent_request_body_bytes",
                "Request body size in bytes",
                labelnames=["path"],
                buckets=_SIZE_BUCKETS,
                registry=self._registry,
            )
            self._response_body_bytes = Histogram(
                "agent_response_body_bytes",
                "Response body size in bytes",
                labelnames=["path"],
                buckets=_SIZE_BUCKETS,
                registry=self._registry,
            )
        elif enabled and not _HAS_PROMETHEUS:
            logger.warning(
                "Metrics were enabled but prometheus_client is not installed. "
                "Install it with: pip install azure-ai-agentserver[metrics]"
            )

    @property
    def enabled(self) -> bool:
        """Whether metrics collection is active."""
        return self._enabled

    def inc_in_flight(self) -> None:
        """Increment the in-flight request gauge."""
        if self._request_in_flight is not None:
            self._request_in_flight.inc()

    def dec_in_flight(self) -> None:
        """Decrement the in-flight request gauge."""
        if self._request_in_flight is not None:
            self._request_in_flight.dec()

    def record_request(
        self,
        method: str,
        path: str,
        status: int,
        duration: float,
        request_size: int,
        response_size: int,
    ) -> None:
        """Record metrics for a completed request.

        :param method: HTTP method (e.g. ``"POST"``).
        :type method: str
        :param path: Request path (e.g. ``"/invocations"``).
        :type path: str
        :param status: HTTP status code.
        :type status: int
        :param duration: Request duration in seconds.
        :type duration: float
        :param request_size: Request body size in bytes.
        :type request_size: int
        :param response_size: Response body size in bytes.
        :type response_size: int
        """
        if not self._enabled:
            return
        status_str = str(status)
        self._request_total.labels(method=method, path=path, status=status_str).inc()
        self._request_duration.labels(method=method, path=path, status=status_str).observe(duration)
        if request_size >= 0:
            self._request_body_bytes.labels(path=path).observe(request_size)
        if response_size >= 0:
            self._response_body_bytes.labels(path=path).observe(response_size)

    def render(self) -> bytes:
        """Render all metrics in Prometheus text exposition format.

        :return: Prometheus-formatted metrics text.
        :rtype: bytes
        """
        if not self._enabled or self._registry is None:
            return b""
        return generate_latest(self._registry)
