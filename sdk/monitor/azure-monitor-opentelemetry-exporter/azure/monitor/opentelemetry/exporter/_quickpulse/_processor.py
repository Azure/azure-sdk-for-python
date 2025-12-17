# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from opentelemetry.sdk._logs import LogData, LogRecordProcessor
from opentelemetry.sdk.trace import ReadableSpan, SpanProcessor

from azure.monitor.opentelemetry.exporter._quickpulse._live_metrics import _QuickpulseManager


# pylint: disable=protected-access
class _QuickpulseLogRecordProcessor(LogRecordProcessor):
    def __init__(self):
        super().__init__()
        self.call_on_emit = hasattr(super(), "on_emit")

    def on_emit(self, log_data: LogData) -> None:  # type: ignore
        qpm = _QuickpulseManager._instance
        if qpm:
            qpm._record_log_record(log_data)
        if self.call_on_emit:
            super().on_emit(log_data)  # type: ignore[safe-super]
        else:
            # this method was removed in opentelemetry-sdk and replaced with on_emit
            super().emit(log_data)  # type: ignore[safe-super,misc] # pylint: disable=no-member

    def emit(self, log_data: LogData) -> None:
        self.on_emit(log_data)

    def shutdown(self):
        pass

    def force_flush(self, timeout_millis: int = 30000):
        super().force_flush(timeout_millis=timeout_millis)  # type: ignore[safe-super]


# pylint: disable=protected-access
class _QuickpulseSpanProcessor(SpanProcessor):
    def on_end(self, span: ReadableSpan) -> None:
        qpm = _QuickpulseManager._instance
        if qpm:
            qpm._record_span(span)
        return super().on_end(span)
