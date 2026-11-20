# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from copy import copy
from typing import Optional, Dict, Any

from opentelemetry._logs import LogRecord
from opentelemetry.sdk._logs import ReadWriteLogRecord
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, LogRecordExporter
from opentelemetry.trace import TraceFlags, get_current_span

from azure.monitor.opentelemetry.exporter._constants import _LOG_SAMPLE_RATE_ATTR, _SAMPLE_RATE_KEY


def _get_span_sample_rate(record: LogRecord) -> Optional[float]:
    if record.context is None:
        return None
    span = get_current_span(record.context)
    span_context = span.get_span_context()
    if span_context.trace_id != record.trace_id or span_context.span_id != record.span_id:
        return None
    attributes = getattr(span, "attributes", None)
    rate = attributes.get(_SAMPLE_RATE_KEY) if attributes else None
    if isinstance(rate, str):
        try:
            rate = float(rate)
        except ValueError:
            return None
    if isinstance(rate, (int, float)) and not isinstance(rate, bool) and 0 < rate < 100:
        return rate
    return None


class _AzureBatchLogRecordProcessor(BatchLogRecordProcessor):
    """Azure Monitor Log Record Processor with support for trace-based sampling."""

    def __init__(
        self,
        log_record_exporter: LogRecordExporter,
        options: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the Azure Monitor Log Record Processor.

        :param log_record_exporter: The LogRecordExporter to use for exporting logs.
        :param options: Optional configuration dictionary. Supported options:
                        - enable_trace_based_sampling_for_logs(bool): Enable trace-based sampling for logs.
        """
        super().__init__(log_record_exporter)
        self._options = options or {}
        self._enable_trace_based_sampling_for_logs = self._options.get("enable_trace_based_sampling_for_logs")

    def on_emit(self, log_record: ReadWriteLogRecord) -> None:  # pylint: disable=arguments-renamed
        # cspell: disable
        """Determines whether the logger should drop log records associated with unsampled traces.
        If `enable_trace_based_sampling_for_logs` is `true`, log records associated with unsampled traces are
        dropped by the `Logger`.
        A log record is considered associated with an unsampled trace if it has a valid `SpanId` and its
        `TraceFlags` indicate that the trace is unsampled. A log record that isn't associated with a trace
        context is not affected by this parameter and therefore bypasses trace based sampling filtering.

        :param log_record: Contains the log record to be exported
        :type log_record: ReadWriteLogRecord
        """

        # cspell: enable
        record = log_record.log_record
        if (
            self._enable_trace_based_sampling_for_logs
            and 0 < (record.trace_id or 0) < 1 << 128
            and 0 < (record.span_id or 0) < 1 << 64
        ):
            if (record.trace_flags or 0) & TraceFlags.SAMPLED == 0:
                return
            sample_rate = _get_span_sample_rate(record)
            if sample_rate is not None:
                # The SDK clears context when batching. Keep the rate on our copy, not
                # on the record shared with other processors or in a user attribute slot.
                log_record = copy(log_record)
                log_record.log_record = copy(record)
                setattr(log_record.log_record, _LOG_SAMPLE_RATE_ATTR, sample_rate)
        super().on_emit(log_record)
