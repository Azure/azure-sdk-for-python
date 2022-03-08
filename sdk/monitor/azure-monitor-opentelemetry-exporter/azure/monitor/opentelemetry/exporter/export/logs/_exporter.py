# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import logging
from typing import Sequence, Any

from opentelemetry.sdk._logs import LogData
from opentelemetry.sdk._logs.export import LogExporter, LogExportResult
from opentelemetry.sdk.util import ns_to_iso_str
from opentelemetry.trace import Span, SpanKind

from azure.monitor.opentelemetry.exporter import _utils
from azure.monitor.opentelemetry.exporter._generated.models import (
    MessageData,
    MonitorBase,
    TelemetryItem
)
from azure.monitor.opentelemetry.exporter.export._base import (
    BaseExporter,
    ExportResult,
)

_logger = logging.getLogger(__name__)

_DEFAULT_SPAN_ID = "0x0000000000000000"
_DEFAULT_TRACE_ID = "0x00000000000000000000000000000000"

__all__ = ["AzureMonitorLogExporter"]


class AzureMonitorLogExporter(BaseExporter, LogExporter):
    """Azure Monitor Log exporter for OpenTelemetry."""

    def export(self, batch: Sequence[LogData], **kwargs: Any) -> LogExportResult: # pylint: disable=unused-argument
        """Export log data
        :param logs: Open Telemetry LogData to export.
        :type logs: Sequence[~opentelemetry._logs.LogData]
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

    def _log_to_envelope(self, log: LogData) -> TelemetryItem:
        if not log:
            return None
        envelope = _convert_log_to_envelope(log)
        envelope.instrumentation_key = self._instrumentation_key
        return envelope

    @classmethod
    def from_connection_string(cls, conn_str: str, **kwargs: Any) -> "AzureMonitorLogExporter":
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

def _convert_log_to_envelope(log: LogData) -> TelemetryItem:
    envelope = TelemetryItem(
        name="",
        instrumentation_key="",
        tags=dict(_utils.azure_monitor_context),
        time=ns_to_iso_str(log.timestamp),
    )
    # pylint: disable=protected-access
    envelope.tags.update(_utils._populate_part_a_fields(log.resource))

    envelope.tags['ai.operation.id'] = log.trace_id or _DEFAULT_TRACE_ID
    envelope.tags['ai.operation.parentId'] = log.span_id or _DEFAULT_SPAN_ID

    # TODO: Properties
    properties = {}
    # properties = {
    #     'process': record.processName,
    #     'module': record.module,
    #     'fileName': record.pathname,
    #     'lineNumber': record.lineno,
    #     'level': record.levelname,
    # }
    # TODO: Custom dimensions
    # TODO: Exceptions

    envelope.name = 'Microsoft.ApplicationInsights.Message'
    # Severity number: https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/logs/data-model.md#field-severitynumber
    data = MessageData(
        message=log.body,
        severityLevel= _get_severity_level(log.severity_number),
        properties=properties,
    )
    envelope.data = MonitorBase(baseData=data, baseType='MessageData')

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

def _get_severity_level(severity_number):
    if severity_number < 9:
        return 0
    return (severity_number-1)/4 - 1
