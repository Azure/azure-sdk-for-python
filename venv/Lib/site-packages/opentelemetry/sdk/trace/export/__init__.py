# Copyright The OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import collections
import logging
import os
import sys
import threading
import typing
from enum import Enum

from opentelemetry.context import attach, detach, get_current, set_value
from opentelemetry.trace import DefaultSpan
from opentelemetry.util import time_ns

from .. import Span, SpanProcessor

logger = logging.getLogger(__name__)


class SpanExportResult(Enum):
    SUCCESS = 0
    FAILED_RETRYABLE = 1
    FAILED_NOT_RETRYABLE = 2


class SpanExporter:
    """Interface for exporting spans.

    Interface to be implemented by services that want to export recorded in
    its own format.

    To export data this MUST be registered to the :class`opentelemetry.sdk.trace.Tracer` using a
    `SimpleExportSpanProcessor` or a `BatchExportSpanProcessor`.
    """

    def export(self, spans: typing.Sequence[Span]) -> "SpanExportResult":
        """Exports a batch of telemetry data.

        Args:
            spans: The list of `opentelemetry.trace.Span` objects to be exported

        Returns:
            The result of the export
        """

    def shutdown(self) -> None:
        """Shuts down the exporter.

        Called when the SDK is shut down.
        """


class SimpleExportSpanProcessor(SpanProcessor):
    """Simple SpanProcessor implementation.

    SimpleExportSpanProcessor is an implementation of `SpanProcessor` that
    passes ended spans directly to the configured `SpanExporter`.
    """

    def __init__(self, span_exporter: SpanExporter):
        self.span_exporter = span_exporter

    def on_start(self, span: Span) -> None:
        pass

    def on_end(self, span: Span) -> None:
        token = attach(set_value("suppress_instrumentation", True))
        try:
            self.span_exporter.export((span,))
        # pylint: disable=broad-except
        except Exception:
            logger.exception("Exception while exporting Span.")
        detach(token)

    def shutdown(self) -> None:
        self.span_exporter.shutdown()

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        # pylint: disable=unused-argument
        return True


class BatchExportSpanProcessor(SpanProcessor):
    """Batch span processor implementation.

    BatchExportSpanProcessor is an implementation of `SpanProcessor` that
    batches ended spans and pushes them to the configured `SpanExporter`.
    """

    _FLUSH_TOKEN_SPAN = DefaultSpan(context=None)

    def __init__(
        self,
        span_exporter: SpanExporter,
        max_queue_size: int = 2048,
        schedule_delay_millis: float = 5000,
        max_export_batch_size: int = 512,
    ):
        if max_queue_size <= 0:
            raise ValueError("max_queue_size must be a positive integer.")

        if schedule_delay_millis <= 0:
            raise ValueError("schedule_delay_millis must be positive.")

        if max_export_batch_size <= 0:
            raise ValueError(
                "max_export_batch_size must be a positive integer."
            )

        if max_export_batch_size > max_queue_size:
            raise ValueError(
                "max_export_batch_size must be less than and equal to max_export_batch_size."
            )

        self.span_exporter = span_exporter
        self.queue = collections.deque(
            [], max_queue_size
        )  # type: typing.Deque[Span]
        self.worker_thread = threading.Thread(target=self.worker, daemon=True)
        self.condition = threading.Condition(threading.Lock())
        self.flush_condition = threading.Condition(threading.Lock())
        # flag to indicate that there is a flush operation on progress
        self._flushing = False
        self.schedule_delay_millis = schedule_delay_millis
        self.max_export_batch_size = max_export_batch_size
        self.max_queue_size = max_queue_size
        self.done = False
        # flag that indicates that spans are being dropped
        self._spans_dropped = False
        # precallocated list to send spans to exporter
        self.spans_list = [
            None
        ] * self.max_export_batch_size  # type: typing.List[typing.Optional[Span]]
        self.worker_thread.start()

    def on_start(self, span: Span) -> None:
        pass

    def on_end(self, span: Span) -> None:
        if self.done:
            logger.warning("Already shutdown, dropping span.")
            return
        if len(self.queue) == self.max_queue_size:
            if not self._spans_dropped:
                logger.warning("Queue is full, likely spans will be dropped.")
                self._spans_dropped = True

        self.queue.appendleft(span)

        if len(self.queue) >= self.max_queue_size // 2:
            with self.condition:
                self.condition.notify()

    def worker(self):
        timeout = self.schedule_delay_millis / 1e3
        while not self.done:
            if (
                len(self.queue) < self.max_export_batch_size
                and not self._flushing
            ):
                with self.condition:
                    self.condition.wait(timeout)
                    if not self.queue:
                        # spurious notification, let's wait again
                        continue
                    if self.done:
                        # missing spans will be sent when calling flush
                        break

            # substract the duration of this export call to the next timeout
            start = time_ns()
            self.export()
            end = time_ns()
            duration = (end - start) / 1e9
            timeout = self.schedule_delay_millis / 1e3 - duration

        # be sure that all spans are sent
        self._drain_queue()

    def export(self) -> None:
        """Exports at most max_export_batch_size spans."""
        idx = 0
        notify_flush = False
        # currently only a single thread acts as consumer, so queue.pop() will
        # not raise an exception
        while idx < self.max_export_batch_size and self.queue:
            span = self.queue.pop()
            if span is self._FLUSH_TOKEN_SPAN:
                notify_flush = True
            else:
                self.spans_list[idx] = span
                idx += 1
        token = attach(set_value("suppress_instrumentation", True))
        try:
            # Ignore type b/c the Optional[None]+slicing is too "clever"
            # for mypy
            self.span_exporter.export(self.spans_list[:idx])  # type: ignore
        # pylint: disable=broad-except
        except Exception:
            logger.exception("Exception while exporting Span batch.")
        detach(token)

        if notify_flush:
            with self.flush_condition:
                self.flush_condition.notify()

        # clean up list
        for index in range(idx):
            self.spans_list[index] = None

    def _drain_queue(self):
        """"Export all elements until queue is empty.

        Can only be called from the worker thread context because it invokes
        `export` that is not thread safe.
        """
        while self.queue:
            self.export()

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        if self.done:
            logger.warning("Already shutdown, ignoring call to force_flush().")
            return True

        self._flushing = True
        self.queue.appendleft(self._FLUSH_TOKEN_SPAN)

        # wake up worker thread
        with self.condition:
            self.condition.notify_all()

        # wait for token to be processed
        with self.flush_condition:
            ret = self.flush_condition.wait(timeout_millis / 1e3)

        self._flushing = False

        if not ret:
            logger.warning("Timeout was exceeded in force_flush().")
        return ret

    def shutdown(self) -> None:
        # signal the worker thread to finish and then wait for it
        self.done = True
        with self.condition:
            self.condition.notify_all()
        self.worker_thread.join()
        self.span_exporter.shutdown()


class ConsoleSpanExporter(SpanExporter):
    """Implementation of :class:`SpanExporter` that prints spans to the
    console.

    This class can be used for diagnostic purposes. It prints the exported
    spans to the console STDOUT.
    """

    def __init__(
        self,
        out: typing.IO = sys.stdout,
        formatter: typing.Callable[[Span], str] = lambda span: str(span)
        + os.linesep,
    ):
        self.out = out
        self.formatter = formatter

    def export(self, spans: typing.Sequence[Span]) -> SpanExportResult:
        for span in spans:
            self.out.write(self.formatter(span))
        self.out.flush()
        return SpanExportResult.SUCCESS
