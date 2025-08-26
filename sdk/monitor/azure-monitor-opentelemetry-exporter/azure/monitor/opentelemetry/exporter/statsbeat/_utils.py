# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import os
from typing import Optional, List, Tuple

from requests import ReadTimeout, Timeout
from azure.core.exceptions import ServiceRequestTimeoutError
from azure.monitor.opentelemetry.exporter._constants import (
    RetryCode,
    RetryCodeType,
    DropCodeType,
    DropCode,
    _UNKNOWN,
)
from azure.monitor.opentelemetry.exporter._utils import _get_telemetry_type
from azure.monitor.opentelemetry.exporter._generated.models import TelemetryItem
from azure.monitor.opentelemetry.exporter._storage import StorageExportResult
from azure.monitor.opentelemetry.exporter.statsbeat._state import get_local_storage_setup_state_exception


from azure.monitor.opentelemetry.exporter._constants import (
    _APPLICATIONINSIGHTS_STATS_CONNECTION_STRING_ENV_NAME,
    _APPLICATIONINSIGHTS_STATS_LONG_EXPORT_INTERVAL_ENV_NAME,
    _APPLICATIONINSIGHTS_STATS_SHORT_EXPORT_INTERVAL_ENV_NAME,
    _DEFAULT_NON_EU_STATS_CONNECTION_STRING,
    _DEFAULT_EU_STATS_CONNECTION_STRING,
    _DEFAULT_STATS_SHORT_EXPORT_INTERVAL,
    _DEFAULT_STATS_LONG_EXPORT_INTERVAL,
    _EU_ENDPOINTS,
    _REQ_DURATION_NAME,
    _REQ_SUCCESS_NAME,
    _APPLICATIONINSIGHTS_SDKSTATS_EXPORT_INTERVAL,
    _CLIENT_EXCEPTION,
    _NETWORK_EXCEPTION,
    _STORAGE_EXCEPTION,
    _TIMEOUT_EXCEPTION,
)
from azure.monitor.opentelemetry.exporter.statsbeat._state import (
    _REQUESTS_MAP_LOCK,
    _REQUESTS_MAP,
)

def _get_stats_connection_string(endpoint: str) -> str:
    cs_env = os.environ.get(_APPLICATIONINSIGHTS_STATS_CONNECTION_STRING_ENV_NAME)
    if cs_env:
        return cs_env
    for endpoint_location in _EU_ENDPOINTS:
        if endpoint_location in endpoint:
            # Use statsbeat EU endpoint if user is in EU region
            return _DEFAULT_EU_STATS_CONNECTION_STRING
    return _DEFAULT_NON_EU_STATS_CONNECTION_STRING


# seconds
def _get_stats_short_export_interval() -> int:
    ei_env = os.environ.get(_APPLICATIONINSIGHTS_STATS_SHORT_EXPORT_INTERVAL_ENV_NAME)
    if ei_env:
        try:
            return int(ei_env)
        except ValueError:
            return _DEFAULT_STATS_SHORT_EXPORT_INTERVAL
    return _DEFAULT_STATS_SHORT_EXPORT_INTERVAL


# seconds
def _get_stats_long_export_interval() -> int:
    ei_env = os.environ.get(_APPLICATIONINSIGHTS_STATS_LONG_EXPORT_INTERVAL_ENV_NAME)
    if ei_env:
        try:
            return int(ei_env)
        except ValueError:
            return _DEFAULT_STATS_LONG_EXPORT_INTERVAL
    return _DEFAULT_STATS_LONG_EXPORT_INTERVAL


def _update_requests_map(type_name, value):
    # value can be either a count, duration, status_code or exc_name
    with _REQUESTS_MAP_LOCK:
        # Mapping is {type_name: count/duration}
        if type_name in (_REQ_SUCCESS_NAME[1], "count", _REQ_DURATION_NAME[1]):  # success, count, duration
            _REQUESTS_MAP[type_name] = _REQUESTS_MAP.get(type_name, 0) + value
        else:  # exception, failure, retry, throttle
            prev = 0
            # Mapping is {type_name: {value: count}
            if _REQUESTS_MAP.get(type_name):
                prev = _REQUESTS_MAP.get(type_name).get(value, 0)
            else:
                _REQUESTS_MAP[type_name] = {}
            _REQUESTS_MAP[type_name][value] = prev + 1

def categorize_status_code(status_code: int) -> str:
    status_map = {
        400: "Bad request",
        401: "Unauthorized",
        402: "Daily quota exceeded",
        403: "Forbidden",
        404: "Not found",
        408: "Request timeout",
        413: "Payload too large",
        429: "Too many requests",
        500: "Internal server error",
        502: "Bad gateway",
        503: "Service unavailable",
        504: "Gateway timeout",
    }
    if status_code in status_map:
        return status_map[status_code]
    if 400 <= status_code < 500:
        return "Client error 4xx"
    if 500 <= status_code < 600:
        return "Server error 5xx"
    return f"status_{status_code}"

def _determine_client_retry_code(error) -> Tuple[RetryCodeType, Optional[str]]:
    timeout_exception_types = (
        ServiceRequestTimeoutError,
        ReadTimeout,
        TimeoutError,
        Timeout,
    )
    network_exception_types = (
        ConnectionError,
        OSError,
    )
    if hasattr(error, 'status_code') and error.status_code in [401, 403, 408, 429, 500, 502, 503, 504]:
        # For specific status codes, preserve the custom message if available
        error_message = getattr(error, 'message', None) if hasattr(error, 'message') else None
        return (error.status_code, error_message or _UNKNOWN)

    if isinstance(error, timeout_exception_types):
        return (RetryCode.CLIENT_TIMEOUT, _TIMEOUT_EXCEPTION)

    if hasattr(error, 'message'):
        error_message = getattr(error, 'message', None) if hasattr(error, 'message') else None
        if error_message is not None and ('timeout' in error_message.lower() or 'timed out' in error_message.lower()):
            return (RetryCode.CLIENT_TIMEOUT, _TIMEOUT_EXCEPTION)

    if isinstance(error, network_exception_types):
        return (RetryCode.CLIENT_EXCEPTION, _NETWORK_EXCEPTION)

    return (RetryCode.CLIENT_EXCEPTION, _CLIENT_EXCEPTION)

def _track_successful_items(customer_sdkstats_metrics, envelopes: List[TelemetryItem]):
    if customer_sdkstats_metrics:
        for envelope in envelopes:
            telemetry_type = _get_telemetry_type(envelope)
            customer_sdkstats_metrics.count_successful_items(
                1,
                telemetry_type
            )

def _track_dropped_items(
        customer_sdkstats_metrics,
        envelopes: List[TelemetryItem],
        drop_code: DropCodeType,
        error_message: Optional[str] = None
    ):
    if customer_sdkstats_metrics:
        if error_message is None:
            for envelope in envelopes:
                telemetry_type = _get_telemetry_type(envelope)
                customer_sdkstats_metrics.count_dropped_items(
                    1,
                    telemetry_type,
                    drop_code
                )
        else:
            for envelope in envelopes:
                telemetry_type = _get_telemetry_type(envelope)
                customer_sdkstats_metrics.count_dropped_items(
                    1,
                    telemetry_type,
                    drop_code,
                    error_message
                )

def _track_retry_items(customer_sdkstats_metrics, envelopes: List[TelemetryItem], error) -> None:
    if customer_sdkstats_metrics:
        retry_code, message = _determine_client_retry_code(error)
        for envelope in envelopes:
            telemetry_type = _get_telemetry_type(envelope)
            if isinstance(retry_code, int):
                # For status codes, include the message if available
                if message:
                    customer_sdkstats_metrics.count_retry_items(
                        1,
                        telemetry_type,
                        retry_code,
                        str(message)
                    )
                else:
                    customer_sdkstats_metrics.count_retry_items(
                        1,
                        telemetry_type,
                        retry_code
                    )
            else:
                customer_sdkstats_metrics.count_retry_items(
                    1,
                    telemetry_type,
                    retry_code,
                    str(message)
                )

def _track_dropped_items_from_storage(customer_sdkstats_metrics, result_from_storage_put, envelopes):
    if customer_sdkstats_metrics:
        if result_from_storage_put == StorageExportResult.CLIENT_STORAGE_DISABLED:
            # Track items that would have been retried but are dropped since client has local storage disabled
            _track_dropped_items(customer_sdkstats_metrics, envelopes, DropCode.CLIENT_STORAGE_DISABLED)
        elif result_from_storage_put == StorageExportResult.CLIENT_READONLY:
            # If filesystem is readonly, track dropped items in customer sdkstats
            _track_dropped_items(customer_sdkstats_metrics, envelopes, DropCode.CLIENT_READONLY)
        elif result_from_storage_put == StorageExportResult.CLIENT_PERSISTENCE_CAPACITY_REACHED:
            # If data has to be dropped due to persistent storage being full, track dropped items
            _track_dropped_items(customer_sdkstats_metrics, envelopes, DropCode.CLIENT_PERSISTENCE_CAPACITY)
        elif get_local_storage_setup_state_exception() != "":
            # For exceptions caught in _check_and_set_folder_permissions during storage setup
            _track_dropped_items(customer_sdkstats_metrics, envelopes, DropCode.CLIENT_EXCEPTION, _STORAGE_EXCEPTION)
        elif isinstance(result_from_storage_put, str):
            # For any exceptions occurred in put method of either LocalFileStorage or LocalFileBlob, track dropped item with reason # pylint: disable=line-too-long
            _track_dropped_items(customer_sdkstats_metrics, envelopes, DropCode.CLIENT_EXCEPTION, _STORAGE_EXCEPTION) # pylint: disable=line-too-long
        else:
            # LocalFileBlob.put returns StorageExportResult.LOCAL_FILE_BLOB_SUCCESS here. Don't need to track anything in this case. # pylint: disable=line-too-long
            pass

def _get_customer_sdkstats_export_interval() -> int:
    customer_sdkstats_ei_env = os.environ.get(_APPLICATIONINSIGHTS_SDKSTATS_EXPORT_INTERVAL)
    if customer_sdkstats_ei_env:
        try:
            return int(customer_sdkstats_ei_env)
        except ValueError:
            return _DEFAULT_STATS_SHORT_EXPORT_INTERVAL
    return _DEFAULT_STATS_SHORT_EXPORT_INTERVAL
