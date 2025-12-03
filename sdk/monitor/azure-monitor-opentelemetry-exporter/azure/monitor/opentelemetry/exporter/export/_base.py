# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import getpass
import logging
import os
import tempfile
import time
import sys
from pathlib import Path
from enum import Enum
from typing import List, Optional, Any
from urllib.parse import urlparse
import psutil

from azure.core.exceptions import HttpResponseError, ServiceRequestError
from azure.core.pipeline.policies import (
    ContentDecodePolicy,
    HttpLoggingPolicy,
    RedirectPolicy,
    RequestIdPolicy,
)
from azure.identity import ManagedIdentityCredential
from azure.monitor.opentelemetry.exporter._generated import AzureMonitorClient
from azure.monitor.opentelemetry.exporter._generated._configuration import AzureMonitorClientConfiguration
from azure.monitor.opentelemetry.exporter._generated.models import (
    MessageData,
    MetricsData,
    MonitorDomain,
    RemoteDependencyData,
    RequestData,
    TelemetryEventData,
    TelemetryExceptionData,
    TelemetryItem,
)
from azure.monitor.opentelemetry.exporter._constants import (
    _AZURE_MONITOR_DISTRO_VERSION_ARG,
    _APPLICATIONINSIGHTS_AUTHENTICATION_STRING,
    _INVALID_STATUS_CODES,
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
    DropCode,
    _exception_categories,
)
from azure.monitor.opentelemetry.exporter._connection_string_parser import ConnectionStringParser
from azure.monitor.opentelemetry.exporter._storage import LocalFileStorage
from azure.monitor.opentelemetry.exporter._utils import (
    _get_auth_policy,
    _get_sha256_hash,
)
from azure.monitor.opentelemetry.exporter.statsbeat._state import (
    get_statsbeat_initial_success,
    get_statsbeat_shutdown,
    increment_and_check_statsbeat_failure_count,
    is_statsbeat_enabled,
    set_statsbeat_initial_success,
)
from azure.monitor.opentelemetry.exporter.statsbeat._utils import (
    _update_requests_map,
)
from azure.monitor.opentelemetry.exporter.statsbeat.customer._utils import (
    track_dropped_items_from_storage,
    track_dropped_items,
    track_retry_items,
    track_successful_items,
)
from azure.monitor.opentelemetry.exporter.statsbeat.customer._state import (
    get_customer_stats_manager,
)


logger = logging.getLogger(__name__)

_AZURE_TEMPDIR_PREFIX = "Microsoft-AzureMonitor-"
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
        :keyword ManagedIdentityCredential/ClientSecretCredential credential: Token credential, such as ManagedIdentityCredential or ClientSecretCredential, used for Azure Active Directory (AAD) authentication. Defaults to None.
        :keyword bool disable_offline_storage: Determines whether to disable storing failed telemetry records for retry. Defaults to `False`.
        :keyword str storage_directory: Storage path in which to store retry files. Defaults to `<tempfile.gettempdir()>/opentelemetry-python-<your-instrumentation-key>`.
        :rtype: None
        """
        parsed_connection_string = ConnectionStringParser(kwargs.get("connection_string"))

        # TODO: Uncomment configuration changes once testing is completed
        # Get the configuration manager
        # self._configuration_manager = get_configuration_manager()

        self._api_version = kwargs.get("api_version") or _SERVICE_API_LATEST
        # We do not need to use entra Id if this is a sdkStats exporter
        if self._is_stats_exporter():
            self._credential = None
        else:
            # We use the credential on a regular exporter or customer sdkStats exporter
            self._credential = _get_authentication_credential(**kwargs)
        self._consecutive_redirects = 0  # To prevent circular redirects
        self._disable_offline_storage = kwargs.get("disable_offline_storage", False)
        self._connection_string = parsed_connection_string._connection_string
        self._endpoint = parsed_connection_string.endpoint
        self._region = parsed_connection_string.region
        self._instrumentation_key = parsed_connection_string.instrumentation_key
        self._aad_audience = parsed_connection_string.aad_audience
        self._storage_maintenance_period = kwargs.get(
            "storage_maintenance_period", 60
        )  # Maintenance interval in seconds.
        self._storage_max_size = kwargs.get(
            "storage_max_size", 50 * 1024 * 1024
        )  # Maximum size in bytes (default 50MiB)
        self._storage_min_retry_interval = kwargs.get(
            "storage_min_retry_interval", 60
        )  # minimum retry interval in seconds
        if "storage_directory" in kwargs:
            self._storage_directory = kwargs.get("storage_directory")
        elif not self._disable_offline_storage:
            self._storage_directory = _get_storage_directory(self._instrumentation_key or "")
        else:
            self._storage_directory = None
        self._storage_retention_period = kwargs.get(
            "storage_retention_period", 48 * 60 * 60
        )  # Retention period in seconds (default 48 hrs)
        self._timeout = kwargs.get("timeout", 10.0)  # networking timeout in seconds
        self._distro_version = kwargs.get(
            _AZURE_MONITOR_DISTRO_VERSION_ARG, ""
        )  # If set, indicates the exporter is instantiated via Azure monitor OpenTelemetry distro. Versions corresponds to distro version.
        # specifies whether current exporter is used for collection of instrumentation metrics
        self._instrumentation_collection = kwargs.get("instrumentation_collection", False)

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
            _get_auth_policy(self._credential, config.authentication_policy, self._aad_audience),
            config.custom_hook_policy,
            config.logging_policy,
            # Explicitly disabling to avoid infinite loop of Span creation when data is exported
            # DistributedTracingPolicy(**kwargs),
            config.http_logging_policy or HttpLoggingPolicy(**kwargs),
        ]

        self.client: AzureMonitorClient = AzureMonitorClient(
            host=self._endpoint, connection_timeout=self._timeout, policies=policies, **kwargs
        )
        # TODO: Uncomment configuration changes once testing is completed
        # if self._configuration_manager:
        #    self._configuration_manager.initialize(
        #        os=_get_os(),
        #        rp=_get_rp(),
        #        attach=_get_attach_type(),
        #        component="ext",
        #        version=ext_version,
        #        region=self._region,
        #    )
        self.storage: Optional[LocalFileStorage] = None
        if not self._disable_offline_storage:
            self.storage = LocalFileStorage(  # pyright: ignore
                path=self._storage_directory,  # type: ignore
                max_size=self._storage_max_size,
                maintenance_period=self._storage_maintenance_period,
                retention_period=self._storage_retention_period,
                name="{} Storage".format(self.__class__.__name__),
                lease_period=self._storage_min_retry_interval,
            )

        # statsbeat initialization
        if self._should_collect_stats():
            try:
                # Import here to avoid circular dependencies
                from azure.monitor.opentelemetry.exporter.statsbeat._statsbeat import collect_statsbeat_metrics
                collect_statsbeat_metrics(self)
            except Exception as e:  # pylint: disable=broad-except
                logger.warning("Failed to initialize statsbeat metrics: %s", e)

        # customer sdkstats initialization
        if self._should_collect_customer_sdkstats():

            from azure.monitor.opentelemetry.exporter.statsbeat.customer import collect_customer_sdkstats
            # Collect customer sdkstats metrics
            collect_customer_sdkstats(self)

    def _transmit_from_storage(self) -> None:
        if not self.storage:
            return
        for blob in self.storage.gets():
            # give a few more seconds for blob lease operation
            # to reduce the chance of race (for perf consideration)
            if blob.lease(self._timeout + 5):
                blob_data = blob.get()
                if blob_data is not None:
                    envelopes = [_format_storage_telemetry_item(TelemetryItem.from_dict(x)) for x in blob_data]
                    result = self._transmit(envelopes)
                    if result == ExportResult.FAILED_RETRYABLE:
                        blob.lease(1)
                    else:
                        blob.delete()
                else:
                    # If blob.get() returns None, delete the corrupted blob
                    blob.delete()


    def _handle_transmit_from_storage(self, envelopes: List[TelemetryItem], result: ExportResult) -> None:
        if self.storage:
            if result == ExportResult.FAILED_RETRYABLE:
                envelopes_to_store = [x.as_dict() for x in envelopes]
                result_from_storage_put = self.storage.put(envelopes_to_store)
                if self._should_collect_customer_sdkstats():
                    track_dropped_items_from_storage(result_from_storage_put, envelopes)
            elif result == ExportResult.SUCCESS:
                # Try to send any cached events
                self._transmit_from_storage()

        else:
            # Track items that would have been retried but are dropped since client has local storage disabled
            if self._should_collect_customer_sdkstats():
                track_dropped_items(envelopes, DropCode.CLIENT_STORAGE_DISABLED)

    # pylint: disable=too-many-branches
    # pylint: disable=too-many-nested-blocks
    # pylint: disable=too-many-statements
    def _transmit(self, envelopes: List[TelemetryItem]) -> ExportResult:
        """
        Transmit the data envelopes to the ingestion service.

        Returns an ExportResult, this function should never
        throw an exception.
        :param envelopes: The list of telemetry items to transmit.
        :type envelopes: list of ~azure.monitor.opentelemetry.exporter._generated.models.TelemetryItem
        :return: The result of the export.
        :rtype: ~azure.monitor.opentelemetry.exporter.export._base._ExportResult
        """
        if len(envelopes) > 0:
            result = ExportResult.SUCCESS
            # Track whether or not exporter has successfully reached ingestion
            # Currently only used for statsbeat exporter to detect shutdown cases
            reach_ingestion = False
            start_time = time.time()
            final_result = None
            try:
                track_response = self.client.track(envelopes)
                if not track_response.errors:  # 200
                    self._consecutive_redirects = 0
                    if not self._is_stats_exporter():
                        logger.info(
                            "Transmission succeeded: Item received: %s. Items accepted: %s",
                            track_response.items_received,
                            track_response.items_accepted,
                        )
                    if self._should_collect_stats():
                        _update_requests_map(_REQ_SUCCESS_NAME[1], 1)
                    reach_ingestion = True
                    result = ExportResult.SUCCESS

                    # Track successful items in customer sdkstats
                    if self._should_collect_customer_sdkstats():
                        track_successful_items(envelopes)
                else:  # 206
                    reach_ingestion = True
                    resend_envelopes = []
                    for error in track_response.errors:
                        if _is_retryable_code(error.status_code):
                            resend_envelopes.append(envelopes[error.index])  # type: ignore
                            # Track retried items in customer sdkstats
                            if self._should_collect_customer_sdkstats():
                                track_retry_items(resend_envelopes, error)
                        else:
                            if not self._is_stats_exporter():
                                # Track dropped items in customer sdkstats, non-retryable scenario
                                if self._should_collect_customer_sdkstats():
                                    if error is not None and hasattr(error, "index") and error.index is not None and isinstance(error.status_code, int):
                                        track_dropped_items([envelopes[error.index]], error.status_code)
                                logger.error(
                                    "Data drop %s: %s %s.",
                                    error.status_code,
                                    error.message,
                                    envelopes[error.index] if error.index is not None else "",
                                )
                    if self.storage and resend_envelopes:
                        envelopes_to_store = [x.as_dict() for x in resend_envelopes]
                        result_from_storage = self.storage.put(envelopes_to_store, 0)
                        if self._should_collect_customer_sdkstats():
                            track_dropped_items_from_storage(result_from_storage, resend_envelopes)
                        self._consecutive_redirects = 0
                    elif resend_envelopes:
                        # Track items that would have been retried but are dropped since client has local storage disabled
                        if self._should_collect_customer_sdkstats():
                            track_dropped_items(resend_envelopes, DropCode.CLIENT_STORAGE_DISABLED)
                    # Mark as not retryable because we already write to storage here
                    result = ExportResult.FAILED_NOT_RETRYABLE
            except HttpResponseError as response_error:
                # HttpResponseError is raised when a response is received
                if _reached_ingestion_code(response_error.status_code):
                    reach_ingestion = True
                if _is_retryable_code(response_error.status_code):
                    if self._should_collect_stats():
                        _update_requests_map(_REQ_RETRY_NAME[1], value=response_error.status_code)
                    result = ExportResult.FAILED_RETRYABLE
                    # Log error for 401: Unauthorized, 403: Forbidden to assist with customer troubleshooting
                    if not self._is_stats_exporter():
                        if self._should_collect_customer_sdkstats():
                            track_retry_items(envelopes, response_error)
                        if response_error.status_code == 401:
                            logger.error(
                                "Retryable server side error: %s. " \
                                "Your Application Insights resource may be configured to use entra ID authentication. " \
                                "Please make sure your application is configured to use the correct token credential.",
                                response_error.message,
                            )
                        elif response_error.status_code == 403:
                            logger.error(
                                "Retryable server side error: %s. " \
                                "Your application may be configured with a token credential " \
                                "but your Application Insights resource may be configured incorrectly. Please make sure " \
                                "your Application Insights resource has enabled entra Id authentication and " \
                                "has the correct `Monitoring Metrics Publisher` role assigned.",
                                response_error.message,
                            )
                elif _is_throttle_code(response_error.status_code):
                    if self._should_collect_stats():
                        _update_requests_map(_REQ_THROTTLE_NAME[1], value=response_error.status_code)
                    result = ExportResult.FAILED_NOT_RETRYABLE

                    if not self._is_stats_exporter():
                        if self._should_collect_customer_sdkstats() and isinstance(response_error.status_code, int):
                            track_dropped_items(envelopes, response_error.status_code)
                elif _is_redirect_code(response_error.status_code):
                    self._consecutive_redirects = self._consecutive_redirects + 1
                    # pylint: disable=W0212
                    if self._consecutive_redirects < self.client._config.redirect_policy.max_redirects:  # type: ignore
                        if response_error.response and response_error.response.headers:  # type: ignore
                            redirect_has_headers = True
                            location = response_error.response.headers.get("location")  # type: ignore
                            url = urlparse(location)
                        else:
                            redirect_has_headers = False
                        if redirect_has_headers and url.scheme and url.netloc:  # pylint: disable=E0606
                            # Change the host to the new redirected host
                            self.client._config.host = "{}://{}".format(url.scheme, url.netloc)  # pylint: disable=W0212
                            # Attempt to export again
                            result = self._transmit(envelopes)
                        else:
                            if not self._is_stats_exporter():
                                if self._should_collect_customer_sdkstats():
                                    track_dropped_items(envelopes, DropCode.CLIENT_EXCEPTION, _exception_categories.CLIENT_EXCEPTION.value)
                                logger.error(
                                    "Error parsing redirect information.",
                                )
                            result = ExportResult.FAILED_NOT_RETRYABLE
                    else:
                        if not self._is_stats_exporter():
                            # Track dropped items in customer sdkstats, non-retryable scenario
                            if self._should_collect_customer_sdkstats():
                                track_dropped_items(
                                    envelopes,
                                    DropCode.CLIENT_EXCEPTION,
                                    _exception_categories.CLIENT_EXCEPTION.value
                                )
                            logger.error(
                                "Error sending telemetry because of circular redirects. "
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
                            "Non-retryable server side error: %s.",
                            response_error.message,
                        )
                        # Track dropped items in customer sdkstats, non-retryable scenario
                        if self._should_collect_customer_sdkstats() and isinstance(response_error.status_code, int):
                            track_dropped_items(envelopes, response_error.status_code)
                        if _is_invalid_code(response_error.status_code):
                            # Shutdown statsbeat on invalid code from customer endpoint
                            # Import here to avoid circular dependencies
                            from azure.monitor.opentelemetry.exporter.statsbeat._statsbeat import (
                                shutdown_statsbeat_metrics,
                            )
                            from azure.monitor.opentelemetry.exporter.statsbeat.customer import (
                                shutdown_customer_sdkstats_metrics,
                            )

                            shutdown_statsbeat_metrics()
                            # Also shutdown customer sdkstats on invalid code
                            shutdown_customer_sdkstats_metrics()
                    result = ExportResult.FAILED_NOT_RETRYABLE
            except ServiceRequestError as request_error:
                # Errors when we're fairly sure that the server did not receive the
                # request, so it should be safe to retry.
                # ServiceRequestError is raised by azure.core for these cases
                logger.warning("Retrying due to server request error: %s.", request_error.message)

                # Track retry items in customer sdkstats for client-side exceptions
                if self._should_collect_customer_sdkstats():
                    track_retry_items(envelopes, request_error)

                if self._should_collect_stats():
                    exc_type = request_error.exc_type
                    if exc_type is None or exc_type is type(None):
                        exc_type = request_error.__class__.__name__  # type: ignore
                    _update_requests_map(_REQ_EXCEPTION_NAME[1], value=exc_type)
                result = ExportResult.FAILED_RETRYABLE
            except Exception as ex:
                logger.exception("Envelopes could not be exported and are not retryable: %s.", ex)  # pylint: disable=C4769

                # Track dropped items in customer sdkstats for general exceptions
                if self._should_collect_customer_sdkstats():
                    track_dropped_items(envelopes, DropCode.CLIENT_EXCEPTION, _exception_categories.CLIENT_EXCEPTION.value)

                if self._should_collect_stats():
                    _update_requests_map(_REQ_EXCEPTION_NAME[1], value=ex.__class__.__name__)
                result = ExportResult.FAILED_NOT_RETRYABLE
            finally:
                if self._should_collect_stats():
                    end_time = time.time()
                    _update_requests_map("count", 1)
                    _update_requests_map(_REQ_DURATION_NAME[1], value=end_time - start_time)
                if self._is_statsbeat_initializing_state():
                    # Update statsbeat initial success state if reached ingestion
                    if reach_ingestion:
                        set_statsbeat_initial_success(True)
                    else:
                        # if didn't reach ingestion, increment and check if failure threshold
                        # has been reached during attempting statsbeat initialization
                        if increment_and_check_statsbeat_failure_count():
                            # Import here to avoid circular dependencies
                            from azure.monitor.opentelemetry.exporter.statsbeat._statsbeat import (
                                shutdown_statsbeat_metrics,
                            )

                            shutdown_statsbeat_metrics()
                            final_result = ExportResult.FAILED_NOT_RETRYABLE

                if final_result is None:
                    final_result = result
            return final_result

        # No spans to export
        self._consecutive_redirects = 0
        return ExportResult.SUCCESS

    # check to see whether its the case of stats collection
    def _should_collect_stats(self):
        return (
            is_statsbeat_enabled()
            and not get_statsbeat_shutdown()
            and not self._is_stats_exporter()
            and not self._is_customer_sdkstats_exporter()
            and not self._instrumentation_collection
        )


    # check to see whether its the case of customer sdkstats collection
    def _should_collect_customer_sdkstats(self):
        manager = get_customer_stats_manager()
        return (
            manager.is_enabled
            and not manager.is_shutdown
            and not self._is_stats_exporter()
            and not self._is_customer_sdkstats_exporter()
            and not self._instrumentation_collection
        )

    # check to see if statsbeat is in "attempting to be initialized" state
    def _is_statsbeat_initializing_state(self):
        return self._is_stats_exporter() and not get_statsbeat_shutdown() and not get_statsbeat_initial_success()

    def _is_stats_exporter(self):
        return getattr(self, "_is_sdkstats", False)

    def _is_customer_sdkstats_exporter(self):
        return getattr(self, '_is_customer_sdkstats', False)

def _is_invalid_code(response_code: Optional[int]) -> bool:
    """Determine if response is a invalid response.

    :param int response_code: HTTP response code
    :return: True if response is a invalid response
    :rtype: bool
    """
    return response_code in _INVALID_STATUS_CODES


def _is_redirect_code(response_code: Optional[int]) -> bool:
    """Determine if response is a redirect response.

    :param int response_code: HTTP response code
    :return: True if response is a redirect response
    :rtype: bool
    """
    return response_code in _REDIRECT_STATUS_CODES


def _is_retryable_code(response_code: Optional[int]) -> bool:
    """Determine if response is retryable.

    :param int response_code: HTTP response code
    :return: True if response is retryable
    :rtype: bool
    """
    return response_code in _RETRYABLE_STATUS_CODES


def _is_throttle_code(response_code: Optional[int]) -> bool:
    """Determine if response is throttle response.

    :param int response_code: HTTP response code
    :return: True if response is throttle response
    :rtype: bool
    """
    return response_code in _THROTTLE_STATUS_CODES


def _reached_ingestion_code(response_code: Optional[int]) -> bool:
    """Determine if response indicates ingestion service has been reached.

    :param int response_code: HTTP response code
    :return: True if response indicates ingestion service has been reached
    :rtype: bool
    """
    return response_code in _REACHED_INGESTION_STATUS_CODES


_MONITOR_DOMAIN_MAPPING = {
    "EventData": TelemetryEventData,
    "ExceptionData": TelemetryExceptionData,
    "MessageData": MessageData,
    "MetricData": MetricsData,
    "RemoteDependencyData": RemoteDependencyData,
    "RequestData": RequestData,
}


# from_dict() deserializes incorrectly, format TelemetryItem correctly after it
# is called
def _format_storage_telemetry_item(item: TelemetryItem) -> TelemetryItem:
    # After TelemetryItem.from_dict, all base_data fields are stored in
    # additional_properties as a dict instead of in item.data.base_data itself
    # item.data.base_data is also of type MonitorDomain instead of a child class
    if hasattr(item, "data") and item.data is not None:
        if hasattr(item.data, "base_data") and isinstance(item.data.base_data, MonitorDomain):
            if hasattr(item.data, "base_type") and isinstance(item.data.base_type, str):
                base_type = _MONITOR_DOMAIN_MAPPING.get(item.data.base_type)
                # Apply deserialization of additional_properties and store that as base_data
                if base_type:
                    item.data.base_data = base_type.from_dict(item.data.base_data.additional_properties)  # type: ignore
                    item.data.base_data.additional_properties = None  # type: ignore
    return item

# mypy: disable-error-code="union-attr"
def _get_authentication_credential(**kwargs: Any) -> Optional[ManagedIdentityCredential]:
    if "credential" in kwargs:
        return kwargs.get("credential")
    auth_string = os.getenv(_APPLICATIONINSIGHTS_AUTHENTICATION_STRING, "")
    try:
        if _APPLICATIONINSIGHTS_AUTHENTICATION_STRING in os.environ:
            kv_pairs = auth_string.split(";")
            auth_string_d = dict(s.split("=") for s in kv_pairs)
            auth_string_d = {key.lower(): value for key, value in auth_string_d.items()}
            if "authorization" in auth_string_d and auth_string_d["authorization"] == "AAD":
                if "clientid" in auth_string_d:
                    credential = ManagedIdentityCredential(client_id=auth_string_d["clientid"])
                    return credential
                credential = ManagedIdentityCredential()
                return credential
    except ValueError as exc:
        logger.error("APPLICATIONINSIGHTS_AUTHENTICATION_STRING, %s, has invalid format: %s", auth_string, exc)  # pylint: disable=do-not-log-exceptions-if-not-debug
    except Exception as e:
        logger.error("Failed to get authentication credential and enable AAD: %s", e)  # pylint: disable=do-not-log-exceptions-if-not-debug
    return None

def _get_storage_directory(instrumentation_key: str) -> str:
    """Return the deterministic local storage path for a given instrumentation key.

    On shared Linux hosts the first user to create ``/tmp/Microsoft/AzureMonitor`` can
    block others because the directory inherits that user's ``umask``. This is avoided by
    inserting a hash of the instrumentation key, user name, process name, and
    application directory, giving each user their own subdirectory, e.g.
    ``/tmp/Microsoft-AzureMonitor-1234...../opentelemetry-python-<ikey>``.

    :param str instrumentation_key: Application Insights instrumentation key.
    :return: Absolute path to the storage directory.
    :rtype: str
    """

    def _safe_psutil_call(func, default=""):
        try:
            return func() or default
        except psutil.Error:
            return default

    shared_root = tempfile.gettempdir()

    process = None
    try:
        process = psutil.Process()
    except psutil.Error:
        pass

    process_name = _safe_psutil_call(process.name) if process else ""
    candidate_path = _safe_psutil_call(process.cwd) if process else ""

    if not candidate_path:
        candidate_path = sys.argv[0] if sys.argv else ""

    try:
        application_directory = Path(candidate_path or ".").resolve()
    except Exception:
        application_directory = Path(shared_root)

    try:
        user_segment = getpass.getuser()
    except Exception:
        user_segment = ""

    hash_input = ";".join(
        [
            instrumentation_key,
            user_segment,
            process_name,
            os.fspath(application_directory), # cspell:disable-line
        ]
    )
    subdirectory = _get_sha256_hash(hash_input)
    storage_directory = os.path.join(
        shared_root, _AZURE_TEMPDIR_PREFIX + subdirectory, _TEMPDIR_PREFIX + instrumentation_key
    )
    return storage_directory
