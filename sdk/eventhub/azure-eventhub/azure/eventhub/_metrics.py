# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from __future__ import annotations

from contextvars import copy_context
import logging
from time import perf_counter
from typing import TYPE_CHECKING, Optional

from azure.core.settings import settings

from ._tracing import DiagnosticSpan, operation_outcome
from ._version import VERSION

if TYPE_CHECKING:
    from opentelemetry.metrics import MeterProvider

_LOGGER = logging.getLogger(__name__)


class EventHubMetrics:
    """Application-owned instruments, shared by all partition links for one client."""

    def __init__(self, provider: MeterProvider) -> None:
        meter = provider.get_meter("azure.eventhub", VERSION)
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

    def __init__(
        self, metrics: Optional[EventHubMetrics], name: str, namespace: str = "", hub: str = "", *, paused: bool = False
    ) -> None:
        self._metrics = metrics
        self._name = name
        self._elapsed = 0.0
        self._start: Optional[float] = None
        self._finished = not name
        self.span: Optional[DiagnosticSpan] = None
        self._attributes = {
            "messaging.system": "eventhubs",
            "messaging.destination.name": hub,
            "server.address": namespace,
        }
        if not paused:
            self.resume()

    def resume(self) -> None:
        if self._finished:
            return
        if self._metrics is not None and self._start is None:
            self._start = perf_counter()
        self._start_trace()

    def _start_trace(self) -> None:
        span_impl = settings.tracing_implementation()
        if self.span is None and span_impl is not None:
            # Receive polls and callbacks may be interleaved or run on different tasks.
            self.span = DiagnosticSpan(
                span_impl,
                "EventHubs." + self._name + ".operation",
                self._attributes,
                copy_context() if self._name == "receive" else None,
            )

    def pause(self) -> None:
        if self._start is not None:
            self._elapsed += perf_counter() - self._start
            self._start = None

    def finish(self, count: int = 0, error: Optional[BaseException] = None) -> None:
        if self._finished:
            return
        self._finished = True
        self.pause()
        outcome = operation_outcome(error)
        if error is not None and self.span is None:
            self._start_trace()
        if self.span is not None:
            self.span.finish(outcome)
        metrics = self._metrics
        if metrics is not None:
            attributes = {**self._attributes, "operation": self._name, "outcome": outcome}
            try:
                metrics.operations.add(1, attributes)
                metrics.duration.record(self._elapsed, attributes)
                if count:
                    metrics.events.add(count, attributes)
            except Exception:  # pylint: disable=broad-except
                _LOGGER.debug("Unable to record Event Hubs operation metrics", exc_info=True)

    def discard(self) -> None:
        # An empty send or a receive loop that completed without another delivery.
        if not self._finished and self.span is not None:
            self.span.finish("success")
        self._finished = True

    def __enter__(self) -> Operation:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc is not None:
            self.finish(error=exc)
        else:
            self.discard()


DISABLED_OPERATION = Operation(None, "")
