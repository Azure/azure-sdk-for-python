# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import logging
from typing import Sequence, Any

from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.sdk._logs import LogData
from opentelemetry.sdk._logs.severity import SeverityNumber
from opentelemetry.sdk._logs.export import LogExporter, LogExportResult

from azure.monitor.opentelemetry.exporter import _utils
from azure.monitor.opentelemetry.exporter._generated.models import (
    MessageData,
    MonitorBase,
    TelemetryExceptionData,
    TelemetryExceptionDetails,
    TelemetryItem,
)
from azure.monitor.opentelemetry.exporter.export._base import (
    BaseExporter,
    ExportResult,
)

_logger = logging.getLogger(__name__)

_DEFAULT_SPAN_ID = 0
_DEFAULT_TRACE_ID = 0

__all__ = ["AzureMonitorLogExporter"]


class AzureMonitorLogExporter(BaseExporter, LogExporter):
    """Azure Monitor Log exporter for OpenTelemetry."""

    def export(
        self, batch: Sequence[LogData], **kwargs: Any  # pylint: disable=unused-argument
    ) -> LogExportResult:
        """Export log data
        :param batch: Open Telemetry LogData(s) to export.
        :type batch: Sequence[~opentelemetry._logs.LogData]
        :rtype: ~opentelemetry.sdk._logs.export.LogData
        """
        envelopes = [self._log_to_envelope(log) for log in batch]
        try:
            result = self._transmit(envelopes)
            if result == ExportResult.FAILED_RETRYABLE:
                envelopes_to_store = [x.as_dict() for x in envelopes]
                self.storage.put(envelopes_to_store, 1)
            if result == ExportResult.SUCCESS:
                # Try to send any cached events
                self._transmit_from_storage()
            return _get_log_export_result(result)
        except Exception:  # pylint: disable=broad-except
            _logger.exception("Exception occurred while exporting the data.")
            return _get_log_export_result(ExportResult.FAILED_NOT_RETRYABLE)

    def shutdown(self) -> None:
        """Shuts down the exporter.

        Called when the SDK is shut down.
        """
        self.storage.close()

    def _log_to_envelope(self, log_data: LogData) -> TelemetryItem:
        if not log_data:
            return None
        envelope = _convert_log_to_envelope(log_data)
        envelope.instrumentation_key = self._instrumentation_key
        return envelope

    @classmethod
    def from_connection_string(
        cls, conn_str: str, **kwargs: Any
    ) -> "AzureMonitorLogExporter":
        """
        Create an AzureMonitorLogExporter from a connection string.

        This is the recommended way of instantation if a connection string is passed in explicitly.
        If a user wants to use a connection string provided by environment variable, the constructor
        of the exporter can be called directly.

        :param str conn_str: The connection string to be used for authentication.
        :keyword str api_version: The service API version used. Defaults to latest.
        :returns an instance of ~AzureMonitorLogExporter
        """
        return cls(connection_string=conn_str, **kwargs)


# pylint: disable=protected-access
def _convert_log_to_envelope(log_data: LogData) -> TelemetryItem:
    log_record = log_data.log_record
    envelope = _utils._create_telemetry_item(log_record.timestamp)
    envelope.tags.update(_utils._populate_part_a_fields(log_record.resource))
    envelope.tags["ai.operation.id"] = "{:032x}".format(
        log_record.trace_id or _DEFAULT_TRACE_ID
    )
    envelope.tags["ai.operation.parentId"] = "{:016x}".format(
        log_record.span_id or _DEFAULT_SPAN_ID
    )
    properties = {
        k: v
        for k, v in log_record.attributes.items()
        if k not in _EXCEPTION_ATTRS
    }
    exc_type = log_record.attributes.get(SpanAttributes.EXCEPTION_TYPE)
    exc_message = log_record.attributes.get(SpanAttributes.EXCEPTION_MESSAGE)
    # pylint: disable=line-too-long
    stack_trace = log_record.attributes.get(SpanAttributes.EXCEPTION_STACKTRACE)
    severity_level = _get_severity_level(log_record.severity_number)

    # Exception telemetry
    if exc_type is not None or exc_message is not None:
        envelope.name = "Microsoft.ApplicationInsights.Exception"
        has_full_stack = stack_trace is not None
        if not exc_message:
            exc_message = "Exception"
        exc_details = TelemetryExceptionDetails(
            type_name=exc_type,
            message=exc_message,
            has_full_stack=has_full_stack,
            stack=stack_trace,
        )
        data = TelemetryExceptionData(
            severity_level=severity_level,
            properties=properties,
            exceptions=[exc_details],
        )
        # pylint: disable=line-too-long
        envelope.data = MonitorBase(base_data=data, base_type="ExceptionData")
    else:  # Message telemetry
        envelope.name = "Microsoft.ApplicationInsights.Message"
        # pylint: disable=line-too-long
        # Severity number: https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/logs/data-model.md#field-severitynumber
        data = MessageData(
            message=log_record.body,
            severity_level=severity_level,
            properties=properties,
        )
        envelope.data = MonitorBase(base_data=data, base_type="MessageData")

    return envelope


def _get_log_export_result(result: ExportResult) -> LogExportResult:
    if result == ExportResult.SUCCESS:
        return LogExportResult.SUCCESS
    if result in (
        ExportResult.FAILED_RETRYABLE,
        ExportResult.FAILED_NOT_RETRYABLE,
    ):
        return LogExportResult.FAILURE
    return None


# pylint: disable=line-too-long
# Common schema: https://github.com/microsoft/common-schema/blob/main/Mappings/AzureMonitor-AI.md#messageseveritylevel
# SeverityNumber specs: https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/logs/data-model.md#field-severitynumber
def _get_severity_level(severity_number: SeverityNumber):
    if severity_number.value < 9:
        return 0
    return int((severity_number.value - 1) / 4 - 1)


_EXCEPTION_ATTRS = frozenset(
    (
        SpanAttributes.EXCEPTION_TYPE,
        SpanAttributes.EXCEPTION_MESSAGE,
        SpanAttributes.EXCEPTION_STACKTRACE,
        SpanAttributes.EXCEPTION_ESCAPED,
    )
)
