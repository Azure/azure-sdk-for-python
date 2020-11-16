# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import logging
import os
import tempfile
import typing
from enum import Enum

from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.policies import ProxyPolicy, RetryPolicy

from opentelemetry.sdk.trace.export import SpanExportResult
from microsoft.opentelemetry.exporter.azuremonitor._generated import AzureMonitorClient
from microsoft.opentelemetry.exporter.azuremonitor._generated.models import TelemetryItem
from microsoft.opentelemetry.exporter.azuremonitor.connection_string_parser import ConnectionStringParser
from microsoft.opentelemetry.exporter.azuremonitor.options import ExporterOptions
from microsoft.opentelemetry.exporter.azuremonitor.storage import LocalFileStorage


logger = logging.getLogger(__name__)

TEMPDIR_PREFIX = "opentelemetry-python-"

class ExportResult(Enum):
    SUCCESS = 0
    FAILED_RETRYABLE = 1
    FAILED_NOT_RETRYABLE = 2


# pylint: disable=broad-except
class BaseExporter:
    """Azure Monitor base exporter for OpenTelemetry.

    Args:
        options: :doc:`export.options` to allow configuration for the exporter
    """

    def __init__(self, **options):
        options = ExporterOptions(**options)
        parsed_connection_string = ConnectionStringParser(options.connection_string)
        self._instrumentation_key = parsed_connection_string.instrumentation_key
        self._timeout = 10.0 # networking timeout in seconds

        temp_suffix = self._instrumentation_key or ""
        default_storage_path = os.path.join(
            tempfile.gettempdir(), TEMPDIR_PREFIX + temp_suffix
        )
        retry_policy = RetryPolicy(timeout=self._timeout)
        proxy_policy = ProxyPolicy()
        self.client = AzureMonitorClient(
            parsed_connection_string.endpoint, proxy_policy=proxy_policy, retry_policy=retry_policy)
        self.storage = LocalFileStorage(
            path=default_storage_path,
            max_size=50 * 1024 * 1024,
            maintenance_period=60,
            retention_period=7 * 24 * 60 * 60,
        )

    def _transmit_from_storage(self) -> None:
        for blob in self.storage.gets():
            # give a few more seconds for blob lease operation
            # to reduce the chance of race (for perf consideration)
            if blob.lease(self._timeout + 5):
                envelopes = blob.get()
                result = self._transmit(envelopes)
                if result == ExportResult.FAILED_RETRYABLE:
                    blob.lease(1)
                else:
                    blob.delete()

    # pylint: disable=too-many-branches
    # pylint: disable=too-many-nested-blocks
    # pylint: disable=too-many-return-statements
    def _transmit(self, envelopes: typing.List[TelemetryItem]) -> ExportResult:
        """
        Transmit the data envelopes to the ingestion service.

        Returns an ExportResult, this function should never
        throw an exception.
        """
        if len(envelopes) > 0:
            try:
                track_response = self.client.track(envelopes)
                if not track_response.errors:
                    logger.info("Transmission succeeded: Item received: %s. Items accepted: %s",
                                track_response.items_received, track_response.items_accepted)
                    return ExportResult.SUCCESS
                resend_envelopes = []
                for error in track_response.errors:
                    if is_retryable_code(error.statusCode):
                        resend_envelopes.append(
                            envelopes[error.index]
                        )
                    else:
                        logger.error(
                            "Data drop %s: %s %s.",
                            error.statusCode,
                            error.message,
                            envelopes[error.index],
                        )
                if resend_envelopes:
                    self.storage.put(resend_envelopes)

            except HttpResponseError as response_error:
                if is_retryable_code(response_error.status_code):
                    return ExportResult.FAILED_RETRYABLE
                return ExportResult.FAILED_NOT_RETRYABLE
            except Exception as ex:
                logger.warning(
                    "Retrying due to transient client side error %s.", ex
                )
                # client side error (retryable)
                return ExportResult.FAILED_RETRYABLE
            return ExportResult.FAILED_NOT_RETRYABLE
        # No spans to export
        return ExportResult.SUCCESS


def is_retryable_code(response_code: int) -> bool:
    """
    Determine if response is retryable
    """
    return bool(response_code in (
        206,  # Retriable
        408,  # Timeout
        429,  # Throttle, too Many Requests
        439,  # Quota, too Many Requests over extended time
        500,  # Internal Server Error
        503,  # Service Unavailable
    ))


def get_trace_export_result(result: ExportResult) -> SpanExportResult:
    if result == ExportResult.SUCCESS:
        return SpanExportResult.SUCCESS
    if result in (
        ExportResult.FAILED_RETRYABLE,
        ExportResult.FAILED_NOT_RETRYABLE,
    ):
        return SpanExportResult.FAILURE
    return None
