# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from copy import copy
from typing import Optional, Dict, Any

from opentelemetry.sdk._logs import ReadWriteLogRecord
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, LogRecordExporter
from opentelemetry.trace import Span, get_current_span

from azure.monitor.opentelemetry.exporter._constants import _LOG_SAMPLE_RATE_ATTR, _SAMPLE_RATE_KEY


def _get_span_sample_rate(span: Span) -> Optional[float]:
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
        Sampling drops a log only when the span in the log's context is valid and unsampled.
        Trace IDs and flags on the log record itself do not determine whether it is dropped.

        :param log_record: Contains the log record to be exported
        :type log_record: ReadWriteLogRecord
        """

        # cspell: enable
        record = getattr(log_record, "log_record", None)
        if (
            self._enable_trace_based_sampling_for_logs
            and record is not None
            and getattr(record, "context", None) is not None
        ):
            span = get_current_span(record.context)
            span_context = span.get_span_context()
            if span_context.is_valid:
                if not span_context.trace_flags.sampled:
                    return
                if (
                    span_context.trace_id == record.trace_id
                    and span_context.span_id == record.span_id
                    and (sample_rate := _get_span_sample_rate(span)) is not None
                ):
                    # The SDK clears context when batching. Keep the rate on our copy, not
                    # on the record shared with other processors or in a user attribute slot.
                    log_record = copy(log_record)
                    log_record.log_record = copy(record)
                    setattr(log_record.log_record, _LOG_SAMPLE_RATE_ATTR, sample_rate)
        super().on_emit(log_record)
