# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from opentelemetry.sdk._logs import LogData
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, LogExporter


# pylint: disable=protected-access
class _AzureMonitorLogRecordProcessor(BatchLogRecordProcessor):

    def __init__(self, exporter: LogExporter, disable_trace_based_sampling=False) -> None:
        self._disable_trace_based_sampling = disable_trace_based_sampling
        super().__init__(exporter)

    def emit(self, log_data: LogData) -> None:
        # Trace based sampling for logs
        if not self._disable_trace_based_sampling:
            if log_data.log_record.span_id and log_data.log_record.trace_flags is not None and \
                not log_data.log_record.trace_flags.sampled:
                # Do not export log for spans that were sampled out
                return
        super().emit(log_data)
