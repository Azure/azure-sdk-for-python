# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import logging
import os
import tempfile
from enum import Enum
from typing import List, Any

from opentelemetry.sdk.trace.export import SpanExportResult

from azure.core.exceptions import HttpResponseError, ServiceRequestError
from azure.core.pipeline.policies import ContentDecodePolicy, HttpLoggingPolicy, RequestIdPolicy
from azure.monitor.opentelemetry.exporter._generated import AzureMonitorClient
from azure.monitor.opentelemetry.exporter._generated._configuration import AzureMonitorClientConfiguration
from azure.monitor.opentelemetry.exporter._generated.models import TelemetryItem
from azure.monitor.opentelemetry.exporter._connection_string_parser import ConnectionStringParser
from azure.monitor.opentelemetry.exporter._storage import LocalFileStorage


logger = logging.getLogger(__name__)

_TEMPDIR_PREFIX = "opentelemetry-python-"
_SERVICE_API_LATEST = "2020-09-15_Preview"

class ExportResult(Enum):
    SUCCESS = 0
    FAILED_RETRYABLE = 1
    FAILED_NOT_RETRYABLE = 2


# pylint: disable=broad-except
class BaseExporter:
    """Azure Monitor base exporter for OpenTelemetry."""

    def __init__(self, **kwargs: Any) -> None:
        """Azure Monitor base exporter for OpenTelemetry.

        :keyword str api_version: The service API version used. Defaults to latest.
        :rtype: None
        """
        parsed_connection_string = ConnectionStringParser(kwargs.get('connection_string'))

        self._instrumentation_key = parsed_connection_string.instrumentation_key
        self._timeout = 10.0  # networking timeout in seconds
        self._api_version = kwargs.get('api_version') or _SERVICE_API_LATEST

        temp_suffix = self._instrumentation_key or ""
        default_storage_path = os.path.join(
            tempfile.gettempdir(), _TEMPDIR_PREFIX + temp_suffix
        )
        config = AzureMonitorClientConfiguration(
            parsed_connection_string.endpoint, **kwargs)
        policies = [
            RequestIdPolicy(**kwargs),
            config.headers_policy,
            config.user_agent_policy,
            config.proxy_policy,
            ContentDecodePolicy(**kwargs),
            config.redirect_policy,
            config.retry_policy,
            config.authentication_policy,
            config.custom_hook_policy,
            config.logging_policy,
            # Explicitly disabling to avoid infinite loop of Span creation when data is exported
            # DistributedTracingPolicy(**kwargs),
            config.http_logging_policy or HttpLoggingPolicy(**kwargs)
        ]
        self.client = AzureMonitorClient(
            host=parsed_connection_string.endpoint, connection_timeout=self._timeout, policies=policies, **kwargs)
        self.storage = LocalFileStorage(
            path=default_storage_path,
            max_size=50 * 1024 * 1024,  # Maximum size in bytes.
            maintenance_period=60,  # Maintenance interval in seconds.
            retention_period=7 * 24 * 60 * 60,  # Retention period in seconds
        )

    def _transmit_from_storage(self) -> None:
        for blob in self.storage.gets():
            # give a few more seconds for blob lease operation
            # to reduce the chance of race (for perf consideration)
            if blob.lease(self._timeout + 5):
                envelopes = [TelemetryItem(**x) for x in blob.get()]
                result = self._transmit(list(envelopes))
                if result == ExportResult.FAILED_RETRYABLE:
                    blob.lease(1)
                else:
                    blob.delete()

    # pylint: disable=too-many-branches
    # pylint: disable=too-many-nested-blocks
    # pylint: disable=too-many-return-statements
    def _transmit(self, envelopes: List[TelemetryItem]) -> ExportResult:
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
                    if _is_retryable_code(error.status_code):
                        resend_envelopes.append(
                            envelopes[error.index]
                        )
                    else:
                        logger.error(
                            "Data drop %s: %s %s.",
                            error.status_code,
                            error.message,
                            envelopes[error.index] if error.index is not None else "",
                        )
                if resend_envelopes:
                    envelopes_to_store = [x.as_dict()
                                          for x in resend_envelopes]
                    self.storage.put(envelopes_to_store)
                    return ExportResult.FAILED_RETRYABLE

            except HttpResponseError as response_error:
                if _is_retryable_code(response_error.status_code):
                    return ExportResult.FAILED_RETRYABLE
                return ExportResult.FAILED_NOT_RETRYABLE
            except ServiceRequestError as request_error:
                # Errors when we're fairly sure that the server did not receive the
                # request, so it should be safe to retry.
                logger.warning(
                    "Retrying due to server request error: %s.", request_error
                )
                return ExportResult.FAILED_RETRYABLE
            except Exception as ex:
                logger.error(
                    "Envelopes could not be exported and are not retryable: %s.", ex
                )
                return ExportResult.FAILED_NOT_RETRYABLE
            return ExportResult.FAILED_NOT_RETRYABLE
        # No spans to export
        return ExportResult.SUCCESS


def _is_retryable_code(response_code: int) -> bool:
    """
    Determine if response is retryable
    """
    return bool(response_code in (
        206,  # Partial success
        408,  # Timeout
        429,  # Throttle, too Many Requests
        439,  # Quota, too Many Requests over extended time
        500,  # Internal Server Error
        502,  # BadGateway
        503,  # Service Unavailable
        504,  # Gateway timeout
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
