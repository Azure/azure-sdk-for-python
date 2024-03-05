# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from opentelemetry.sdk._logs import LogData, LogRecordProcessor

from azure.monitor.opentelemetry.exporter._quickpulse._live_metrics import record_log_record


class _QuickpulseLogRecordProcessor(LogRecordProcessor):

    def emit(self, log_data: LogData) -> None:
        record_log_record(log_data)
        super().emit(log_data)
    
    def shutdown(self):
        super().shutdown()

    def force_flush(self, timeout_millis: int = 30000):
        super().force_flush(timeout_millis=timeout_millis)
