# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import Optional, Dict, Any

from opentelemetry.sdk._logs import LogRecordProcessor, LogData
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, LogExporter
from opentelemetry.trace import get_current_span


class _AzureBatchLogRecordProcessor(BatchLogRecordProcessor):
    """Azure Monitor Log Record Processor with support for trace-based sampling."""

    def __init__(
        self,
        log_exporter: LogExporter,
        options: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the Azure Monitor Log Record Processor.

        :param exporter: The LogRecordExporter to use for exporting logs.
        :param options: Optional configuration dictionary. Supported options:
                        - enable_trace_based_sampling_for_logs(bool): Enable trace-based sampling for logs.
        """
        super().__init__(log_exporter)
        self._options = options or {}
        self._enable_trace_based_sampling_for_logs = self._options.get("enable_trace_based_sampling_for_logs")

    def on_emit(self, log_data: LogData) -> None:
        # cspell: disable
        """ Determines whether the logger should drop log records associated with unsampled traces.
        If `trace_based_sampling` is `true`, log records associated with unsampled traces are dropped by the `Logger`.
        A log record is considered associated with an unsampled trace if it has a valid `SpanId` and its
        `TraceFlags` indicate that the trace is unsampled. A log record that isn't associated with a trace
        context is not affected by this parameter and therefore bypasses trace based sampling filtering.

        :param log_data: Contains the log record to be exported
        :type log_data: LogData
        """

        # cspell: enable
        if self._enable_trace_based_sampling_for_logs:
            if hasattr(log_data, "log_record") and log_data.log_record is not None:
                if hasattr(log_data.log_record, "context") and log_data.log_record.context is not None:
                    span = get_current_span(log_data.log_record.context)
                    span_context = span.get_span_context()
                    if span_context.is_valid and not span_context.trace_flags.sampled:
                        return
        super().on_emit(log_data)
