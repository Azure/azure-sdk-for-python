# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from __future__ import annotations

import asyncio
import logging
from time import perf_counter
from typing import TYPE_CHECKING, Optional

from ._version import VERSION

if TYPE_CHECKING:
    from opentelemetry.metrics import MeterProvider

_LOGGER = logging.getLogger(__name__)


class EventHubMetrics:
    """Application-owned instruments, shared by all partition links for one client."""

    def __init__(self, provider: MeterProvider, namespace: str, hub: str) -> None:
        meter = provider.get_meter("azure.eventhub", VERSION)
        self.attributes = {
            "messaging.system": "eventhubs",
            "messaging.destination.name": hub,
            "server.address": namespace,
        }
        self.operations = meter.create_counter("az.eventhubs.operations", unit="{operation}")
        self.events = meter.create_counter("az.eventhubs.events", unit="{event}")
        self.duration = meter.create_histogram(
            "az.eventhubs.operation.duration",
            unit="s",
            explicit_bucket_boundaries_advisory=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0),
        )
        self.lifecycle = meter.create_counter("az.eventhubs.amqp.lifecycle", unit="{transition}")


class Operation:
    """A logical send or receive. Finish before handing control to an application callback."""

    def __init__(self, metrics: Optional[EventHubMetrics], name: str) -> None:
        self._metrics = metrics
        self._name = name
        self._start = perf_counter() if metrics is not None else 0.0

    def finish(self, count: int = 0, error: Optional[BaseException] = None) -> None:
        metrics = self._metrics
        if metrics is None:
            return
        self._metrics = None
        outcome = "success"
        if error is not None:
            outcome = "cancelled" if isinstance(error, asyncio.CancelledError) else "error"
        attributes = {**metrics.attributes, "operation": self._name, "outcome": outcome}
        try:
            duration = perf_counter() - self._start
            metrics.operations.add(1, attributes)
            metrics.duration.record(duration, attributes)
            if count:
                metrics.events.add(count, attributes)
        except Exception:  # pylint: disable=broad-except
            _LOGGER.debug("Unable to record Event Hubs operation metrics", exc_info=True)

    def __enter__(self) -> Operation:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc is not None:
            self.finish(error=exc)


# No mutable state or clock reads on the uninstrumented path.
DISABLED_OPERATION = Operation(None, "")
