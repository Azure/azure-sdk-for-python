# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import logging
import os
import tempfile
import time
from enum import Enum
from typing import List, Any
from urllib.parse import urlparse

from azure.core.exceptions import HttpResponseError, ServiceRequestError
from azure.core.pipeline.policies import ContentDecodePolicy, HttpLoggingPolicy, RedirectPolicy, RequestIdPolicy
from azure.monitor.opentelemetry.exporter._generated import AzureMonitorClient
from azure.monitor.opentelemetry.exporter._generated._configuration import AzureMonitorClientConfiguration
from azure.monitor.opentelemetry.exporter._generated.models import TelemetryItem
from azure.monitor.opentelemetry.exporter._constants import (
    _REACHED_INGESTION_STATUS_CODES,
    _REDIRECT_STATUS_CODES,
    _REQ_DURATION_NAME,
    _REQ_EXCEPTION_NAME,
    _REQ_FAILURE_NAME,
    _REQ_RETRY_NAME,
    _REQ_SUCCESS_NAME,
    _REQ_THROTTLE_NAME,
    _RETRYABLE_STATUS_CODES,
    _THROTTLE_STATUS_CODES,
)
from azure.monitor.opentelemetry.exporter._connection_string_parser import ConnectionStringParser
from azure.monitor.opentelemetry.exporter._storage import LocalFileStorage
from azure.monitor.opentelemetry.exporter.statsbeat._state import (
    _REQUESTS_MAP_LOCK,
    _REQUESTS_MAP,
    get_statsbeat_initial_success,
    get_statsbeat_shutdown,
    increment_and_check_statsbeat_failure_count,
    is_statsbeat_enabled,
    set_statsbeat_initial_success,
)

logger = logging.getLogger(__name__)

_AZURE_TEMPDIR_PREFIX = "Microsoft/AzureMonitor"
_TEMPDIR_PREFIX = "opentelemetry-python-"
_SERVICE_API_LATEST = "2020-09-15_Preview"

class ExportResult(Enum):
    SUCCESS = 0
    FAILED_RETRYABLE = 1
    FAILED_NOT_RETRYABLE = 2


# pylint: disable=broad-except
# pylint: disable=too-many-instance-attributes
# pylint: disable=C0301
class BaseExporter:
    """Azure Monitor base exporter for OpenTelemetry."""

    def __init__(self, **kwargs: Any) -> None:
        """Azure Monitor base exporter for OpenTelemetry.

        :keyword str api_version: The service API version used. Defaults to latest.
        :keyword str connection_string: The connection string used for your Application Insights resource.
        :keyword bool disable_offline_storage: Determines whether to disable storing failed telemetry records for retry. Defaults to `False`.
        :keyword str storage_directory: Storage path in which to store retry files. Defaults to `<tempfile.gettempdir()>/opentelemetry-python-<your-instrumentation-key>`.
        :rtype: None
        """
        parsed_connection_string = ConnectionStringParser(kwargs.get('connection_string'))

        self._api_version = kwargs.get('api_version') or _SERVICE_API_LATEST
        self._consecutive_redirects = 0  # To prevent circular redirects
        self._disable_offline_storage = kwargs.get('disable_offline_storage', False)
        self._endpoint = parsed_connection_string.endpoint
        self._instrumentation_key = parsed_connection_string.instrumentation_key
        self._storage_maintenance_period = kwargs.get('storage_maintenance_period', 60)  # Maintenance interval in seconds.
        self._storage_max_size = kwargs.get('storage_max_size', 50 * 1024 * 1024)  # Maximum size in bytes (default 50MiB)
        self._storage_min_retry_interval = kwargs.get('storage_min_retry_interval', 60)  # minimum retry interval in seconds
        temp_suffix = self._instrumentation_key or ""
        default_storage_directory = os.path.join(
            tempfile.gettempdir(), _AZURE_TEMPDIR_PREFIX, _TEMPDIR_PREFIX + temp_suffix
        )
        self._storage_directory = kwargs.get('storage_directory', default_storage_directory)  # Storage path in which to store retry files.
        self._storage_retention_period = kwargs.get('storage_retention_period', 48 * 60 * 60)  # Retention period in seconds (default 48 hrs)
        self._timeout = kwargs.get('timeout', 10.0)  # networking timeout in seconds

        config = AzureMonitorClientConfiguration(self._endpoint, **kwargs)
        policies = [
            RequestIdPolicy(**kwargs),
            config.headers_policy,
            config.user_agent_policy,
            config.proxy_policy,
            ContentDecodePolicy(**kwargs),
            # Handle redirects in exporter, set new endpoint if redirected
            RedirectPolicy(permit_redirects=False),
            config.retry_policy,
            config.authentication_policy,
            config.custom_hook_policy,
            config.logging_policy,
            # Explicitly disabling to avoid infinite loop of Span creation when data is exported
            # DistributedTracingPolicy(**kwargs),
            config.http_logging_policy or HttpLoggingPolicy(**kwargs)
        ]
        self.client = AzureMonitorClient(
            host=self._endpoint, connection_timeout=self._timeout, policies=policies, **kwargs)
        self.storage = None
        if not self._disable_offline_storage:
            self.storage = LocalFileStorage(
                path=self._storage_directory,
                max_size=self._storage_max_size,
                maintenance_period=self._storage_maintenance_period,
                retention_period=self._storage_retention_period,
                name="{} Storage".format(self.__class__.__name__),
                lease_period=self._storage_min_retry_interval,
            )
        # statsbeat initialization
        if self._should_collect_stats():
            # Import here to avoid circular dependencies
            from azure.monitor.opentelemetry.exporter.statsbeat._statsbeat import collect_statsbeat_metrics
            collect_statsbeat_metrics(self)

    def _transmit_from_storage(self) -> None:
        for blob in self.storage.gets():
            # give a few more seconds for blob lease operation
            # to reduce the chance of race (for perf consideration)
            if blob.lease(self._timeout + 5):
                envelopes = [TelemetryItem.from_dict(x) for x in blob.get()]
                result = self._transmit(list(envelopes))
                if result == ExportResult.FAILED_RETRYABLE:
                    blob.lease(1)
                else:
                    blob.delete()

    def _handle_transmit_from_storage(self, envelopes: List[TelemetryItem], result: ExportResult) -> None:
        if self.storage:
            if result == ExportResult.FAILED_RETRYABLE:
                envelopes_to_store = [x.as_dict() for x in envelopes]
                self.storage.put(envelopes_to_store)
            elif result == ExportResult.SUCCESS:
                # Try to send any cached events
                self._transmit_from_storage()

    # pylint: disable=too-many-branches
    # pylint: disable=too-many-nested-blocks
    # pylint: disable=too-many-return-statements
    # pylint: disable=too-many-statements
    def _transmit(self, envelopes: List[TelemetryItem]) -> ExportResult:
        """
        Transmit the data envelopes to the ingestion service.

        Returns an ExportResult, this function should never
        throw an exception.
        """
        if len(envelopes) > 0:
            result = ExportResult.SUCCESS
            reach_ingestion = False
            try:
                start_time = time.time()
                track_response = self.client.track(envelopes)
                if not track_response.errors:  # 200
                    self._consecutive_redirects = 0
                    if not self._is_stats_exporter():
                        logger.info("Transmission succeeded: Item received: %s. Items accepted: %s",
                                    track_response.items_received, track_response.items_accepted)
                    if self._should_collect_stats():
                        _update_requests_map(_REQ_SUCCESS_NAME[1])
                    reach_ingestion = True
                    result = ExportResult.SUCCESS
                else:  # 206
                    reach_ingestion = True
                    resend_envelopes = []
                    for error in track_response.errors:
                        if _is_retryable_code(error.status_code):
                            resend_envelopes.append(
                                envelopes[error.index]
                            )
                            if self._should_collect_stats():
                                _update_requests_map(_REQ_RETRY_NAME[1], value=error.status_code)
                        else:
                            if not self._is_stats_exporter():
                                logger.error(
                                    "Data drop %s: %s %s.",
                                    error.status_code,
                                    error.message,
                                    envelopes[error.index] if error.index is not None else "",
                                )
                    if self.storage and resend_envelopes:
                        envelopes_to_store = [x.as_dict()
                                            for x in resend_envelopes]
                        self.storage.put(envelopes_to_store, 0)
                        self._consecutive_redirects = 0
                        result = ExportResult.FAILED_RETRYABLE
                    else:
                        result = ExportResult.FAILED_NOT_RETRYABLE
            except HttpResponseError as response_error:
                # HttpResponseError is raised when a response is received
                if _reached_ingestion_code(response_error.status_code):
                    reach_ingestion = True
                if _is_retryable_code(response_error.status_code):
                    if self._should_collect_stats():
                        _update_requests_map(_REQ_RETRY_NAME[1], value=response_error.status_code)
                    result = ExportResult.FAILED_RETRYABLE
                elif _is_throttle_code(response_error.status_code):
                    if self._should_collect_stats():
                        _update_requests_map(_REQ_THROTTLE_NAME[1], value=response_error.status_code)
                    result = ExportResult.FAILED_NOT_RETRYABLE
                elif _is_redirect_code(response_error.status_code):
                    self._consecutive_redirects = self._consecutive_redirects + 1
                    if self._consecutive_redirects < self.client._config.redirect_policy.max_redirects:  # pylint: disable=W0212
                        if response_error.response and response_error.response.headers:
                            redirect_has_headers = True
                            location = response_error.response.headers.get("location")
                            url = urlparse(location)
                        else:
                            redirect_has_headers = False
                        if redirect_has_headers and url.scheme and url.netloc:
                            # Change the host to the new redirected host
                            self.client._config.host = "{}://{}".format(url.scheme, url.netloc)  # pylint: disable=W0212
                            # Attempt to export again
                            result = self._transmit(envelopes)
                        else:
                            if not self._is_stats_exporter():
                                logger.error(
                                    "Error parsing redirect information.",
                                )
                            result = ExportResult.FAILED_NOT_RETRYABLE
                    else:
                        if not self._is_stats_exporter():
                            logger.error(
                                "Error sending telemetry because of circular redirects. " \
                                "Please check the integrity of your connection string."
                            )
                        # If redirect but did not return, exception occurred
                        if self._should_collect_stats():
                            _update_requests_map(_REQ_EXCEPTION_NAME[1], value="Circular Redirect")
                        result = ExportResult.FAILED_NOT_RETRYABLE
                else:
                    # Any other status code counts as failure (non-retryable)
                    # 400 - Invalid - The server cannot or will not process the request due to the invalid telemetry (invalid data, iKey, etc.)
                    # 404 - Ingestion is allowed only from stamp specific endpoint - must update connection string
                    if self._should_collect_stats():
                        _update_requests_map(_REQ_FAILURE_NAME[1], value=response_error.status_code)
                    if not self._is_stats_exporter():
                        logger.error(
                            'Non-retryable server side error: %s.',
                            response_error.message,
                        )
                    result = ExportResult.FAILED_NOT_RETRYABLE
            except ServiceRequestError as request_error:
                # Errors when we're fairly sure that the server did not receive the
                # request, so it should be safe to retry.
                # ServiceRequestError is raised by azure.core for these cases
                logger.warning(
                    "Retrying due to server request error: %s.", request_error.message
                )
                if self._should_collect_stats():
                    exc_type = request_error.exc_type
                    if exc_type is None or exc_type is type(None):
                        exc_type = request_error.__class__.__name__
                    _update_requests_map(_REQ_EXCEPTION_NAME[1], value=exc_type)
                result = ExportResult.FAILED_RETRYABLE
            except Exception as ex:
                logger.error(
                    "Envelopes could not be exported and are not retryable: %s.", ex
                )
                if self._should_collect_stats():
                    _update_requests_map(_REQ_EXCEPTION_NAME[1], value=ex.__class__.__name__)
                result = ExportResult.FAILED_NOT_RETRYABLE
            finally:
                if self._should_collect_stats():
                    end_time = time.time()
                    _update_requests_map('count')
                    _update_requests_map(_REQ_DURATION_NAME[1], value=end_time-start_time)
                if self._is_statsbeat_initializing_state():
                    # Update statsbeat initial success state if reached ingestion
                    if reach_ingestion:
                        set_statsbeat_initial_success(True)
                    else:
                        # if didn't reach ingestion, increment and check if failure threshold
                        # has been reached during attempting statsbeat initialization
                        if increment_and_check_statsbeat_failure_count():
                            # Import here to avoid circular dependencies
                            from azure.monitor.opentelemetry.exporter.statsbeat._statsbeat import shutdown_statsbeat_metrics
                            shutdown_statsbeat_metrics()
                            # pylint: disable=lost-exception
                            return ExportResult.FAILED_NOT_RETRYABLE
                # pylint: disable=lost-exception
                return result

        # No spans to export
        self._consecutive_redirects = 0
        return ExportResult.SUCCESS

    # check to see whether its the case of stats collection
    def _should_collect_stats(self):
        return is_statsbeat_enabled() and \
            not get_statsbeat_shutdown() and \
            not self._is_stats_exporter()

    # check to see if statsbeat is in "attempting to be initialized" state
    def _is_statsbeat_initializing_state(self):
        return self._is_stats_exporter() and \
            not get_statsbeat_shutdown() and \
            not get_statsbeat_initial_success()

    def _is_stats_exporter(self):
        return self.__class__.__name__ == "_StatsBeatExporter"


def _is_redirect_code(response_code: int) -> bool:
    """
    Determine if response is a redirect response.
    """
    return response_code in _REDIRECT_STATUS_CODES


def _is_retryable_code(response_code: int) -> bool:
    """
    Determine if response is retryable
    """
    return response_code in _RETRYABLE_STATUS_CODES


def _is_throttle_code(response_code: int) -> bool:
    """
    Determine if response is throttle response
    """
    return response_code in _THROTTLE_STATUS_CODES


def _reached_ingestion_code(response_code: int) -> bool:
    """
    Determine if response indicates ingestion service has been reached
    """
    return response_code in _REACHED_INGESTION_STATUS_CODES


def _update_requests_map(type_name, value=None):
    # value is either None, duration, status_code or exc_name
    with _REQUESTS_MAP_LOCK:
        if type_name in (_REQ_SUCCESS_NAME[1], "count"):  # success, count
            _REQUESTS_MAP[type_name] = _REQUESTS_MAP.get(type_name, 0) + 1
        elif type_name == _REQ_DURATION_NAME[1]:  # duration
            _REQUESTS_MAP[type_name] = _REQUESTS_MAP.get(type_name, 0) + value
        else:  # exception, failure, retry, throttle
            prev = 0
            if _REQUESTS_MAP.get(type_name):
                prev = _REQUESTS_MAP.get(type_name).get(value, 0)
            else:
                _REQUESTS_MAP[type_name] = {}
            _REQUESTS_MAP[type_name][value] = prev + 1
