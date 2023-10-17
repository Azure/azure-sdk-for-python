# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import logging
from typing import Sequence, Any

from opentelemetry._logs.severity import SeverityNumber
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.sdk._logs import LogData
from opentelemetry.sdk._logs.export import LogExporter, LogExportResult

from azure.monitor.opentelemetry.exporter import _utils
from azure.monitor.opentelemetry.exporter._constants import (
    _EXCEPTION_ENVELOPE_NAME,
    _MESSAGE_ENVELOPE_NAME,
)
from azure.monitor.opentelemetry.exporter._generated.models import (
    MessageData,
    MonitorBase,
    TelemetryEventData,
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

_APPLICATION_INSIGHTS_EVENT_MARKER_ATTRIBUTE = "APPLICATION_INSIGHTS_EVENT_MARKER_ATTRIBUTE"

class AzureMonitorLogExporter(BaseExporter, LogExporter):
    """Azure Monitor Log exporter for OpenTelemetry."""

    def export(
        self, batch: Sequence[LogData], **kwargs: Any  # pylint: disable=unused-argument
    ) -> LogExportResult:
        """Export log data.

        :param batch: OpenTelemetry LogData(s) to export.
        :type batch: ~typing.Sequence[~opentelemetry._logs.LogData]
        :return: The result of the export.
        :rtype: ~opentelemetry.sdk._logs.export.LogData
        """
        envelopes = [self._log_to_envelope(log) for log in batch]
        try:
            result = self._transmit(envelopes)
            self._handle_transmit_from_storage(envelopes, result)
            return _get_log_export_result(result)
        except Exception:  # pylint: disable=broad-except
            _logger.exception("Exception occurred while exporting the data.")
            return _get_log_export_result(ExportResult.FAILED_NOT_RETRYABLE)

    def shutdown(self) -> None:
        """Shuts down the exporter.

        Called when the SDK is shut down.
        """
        if self.storage:
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
        :rtype ~azure.monitor.opentelemetry.exporter.AzureMonitorLogExporter
        """
        return cls(connection_string=conn_str, **kwargs)


def _log_data_is_event(log_data: LogData):
    log_record = log_data.log_record
    is_event = log_record.attributes.get(_APPLICATION_INSIGHTS_EVENT_MARKER_ATTRIBUTE)
    return is_event is True

# pylint: disable=protected-access
def _convert_log_to_envelope(log_data: LogData) -> TelemetryItem:
    log_record = log_data.log_record
    time_stamp = log_record.timestamp if log_record.timestamp is not None else log_record.observed_timestamp
    envelope = _utils._create_telemetry_item(time_stamp)
    envelope.tags.update(_utils._populate_part_a_fields(log_record.resource))
    envelope.tags["ai.operation.id"] = "{:032x}".format(
        log_record.trace_id or _DEFAULT_TRACE_ID
    )
    envelope.tags["ai.operation.parentId"] = "{:016x}".format(
        log_record.span_id or _DEFAULT_SPAN_ID
    )
    properties = _utils._filter_custom_properties(
        log_record.attributes,
        lambda key, val: not _is_ignored_attribute(key)
    )
    exc_type = log_record.attributes.get(SpanAttributes.EXCEPTION_TYPE)
    exc_message = log_record.attributes.get(SpanAttributes.EXCEPTION_MESSAGE)
    # pylint: disable=line-too-long
    stack_trace = log_record.attributes.get(SpanAttributes.EXCEPTION_STACKTRACE)
    severity_level = _get_severity_level(log_record.severity_number)

    if not log_record.body:
        log_record.body = "n/a"

    # Event telemetry
    if _log_data_is_event(log_data):
        envelope.name = 'Microsoft.ApplicationInsights.Event'
        data = TelemetryEventData(
            name=str(log_record.body)[:32768],
            properties=properties,
        )
        envelope.data = MonitorBase(base_data=data, base_type="EventData")
    # Exception telemetry
    elif exc_type is not None or exc_message is not None:
        envelope.name = _EXCEPTION_ENVELOPE_NAME
        has_full_stack = stack_trace is not None
        if not exc_type:
            exc_type = "Exception"
        if not exc_message:
            exc_message = "Exception"
        exc_details = TelemetryExceptionDetails(
            type_name=str(exc_type)[:1024],
            message=str(exc_message)[:32768],
            has_full_stack=has_full_stack,
            stack=str(stack_trace)[:32768],
        )
        data = TelemetryExceptionData(
            severity_level=severity_level,
            properties=properties,
            exceptions=[exc_details],
        )
        # pylint: disable=line-too-long
        envelope.data = MonitorBase(base_data=data, base_type="ExceptionData")
    else:  # Message telemetry
        envelope.name = _MESSAGE_ENVELOPE_NAME
        # pylint: disable=line-too-long
        # Severity number: https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/logs/data-model.md#field-severitynumber
        data = MessageData(
            message=str(log_record.body)[:32768],
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


def _is_ignored_attribute(key: str) -> bool:
    return key in _IGNORED_ATTRS


_IGNORED_ATTRS = frozenset(
    (
        SpanAttributes.EXCEPTION_TYPE,
        SpanAttributes.EXCEPTION_MESSAGE,
        SpanAttributes.EXCEPTION_STACKTRACE,
        SpanAttributes.EXCEPTION_ESCAPED,
        _APPLICATION_INSIGHTS_EVENT_MARKER_ATTRIBUTE,
    )
)
