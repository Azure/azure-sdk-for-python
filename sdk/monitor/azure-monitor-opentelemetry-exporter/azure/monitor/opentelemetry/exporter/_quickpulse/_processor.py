# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from opentelemetry.sdk._logs import ReadableLogRecord, LogRecordProcessor
from opentelemetry.sdk.trace import ReadableSpan, SpanProcessor

from azure.monitor.opentelemetry.exporter._quickpulse._state import get_quickpulse_manager


# pylint: disable=protected-access
class _QuickpulseLogRecordProcessor(LogRecordProcessor):
    def __init__(self):
        super().__init__()
        self.call_on_emit = hasattr(super(), 'on_emit')

    def on_emit(self, readable_log_record: ReadableLogRecord) -> None:  # type: ignore # pylint: disable=arguments-renamed
        qpm = get_quickpulse_manager()
        if qpm:
            qpm._record_log_record(readable_log_record)
        if self.call_on_emit:
            super().on_emit(readable_log_record)  # type: ignore[safe-super]
        else:
            # this method was removed in opentelemetry-sdk and replaced with on_emit
            super().emit(readable_log_record)  # type: ignore[safe-super,misc] # pylint: disable=no-member

    def emit(self, readable_log_record: ReadableLogRecord) -> None: # pylint: disable=arguments-renamed
        self.on_emit(readable_log_record)

    def shutdown(self):
        pass

    def force_flush(self, timeout_millis: int = 30000):
        super().force_flush(timeout_millis=timeout_millis)  # type: ignore[safe-super]


# pylint: disable=protected-access
class _QuickpulseSpanProcessor(SpanProcessor):

    def on_end(self, span: ReadableSpan) -> None:
        qpm = get_quickpulse_manager()
        if qpm:
            qpm._record_span(span)
        return super().on_end(span)  # type: ignore
