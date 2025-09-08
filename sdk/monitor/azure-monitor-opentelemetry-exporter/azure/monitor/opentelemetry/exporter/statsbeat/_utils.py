# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import os
import logging
import json
from collections.abc import Iterable
from typing import Optional, List, Tuple, Dict
from requests import ReadTimeout, Timeout  # mypy: disable-error-code="import-untyped"
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
from azure.monitor.opentelemetry.exporter.statsbeat._state import (
    get_local_storage_setup_state_exception,
    get_customer_sdkstats_metrics,
)

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
    _ONE_SETTINGS_DEFAULT_STATS_CONNECTION_STRING_KEY,
    _ONE_SETTINGS_SUPPORTED_DATA_BOUNDARIES_KEY,
    _exception_categories,
)

from azure.monitor.opentelemetry.exporter.statsbeat._state import (
    _REQUESTS_MAP,
    _REQUESTS_MAP_LOCK,
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
            value = int(ei_env)
            if value < 1:
                return _DEFAULT_STATS_SHORT_EXPORT_INTERVAL
            return value
        except ValueError:
            return _DEFAULT_STATS_SHORT_EXPORT_INTERVAL
    return _DEFAULT_STATS_SHORT_EXPORT_INTERVAL


# seconds
def _get_stats_long_export_interval() -> int:
    ei_env = os.environ.get(_APPLICATIONINSIGHTS_STATS_LONG_EXPORT_INTERVAL_ENV_NAME)
    if ei_env:
        try:
            value = int(ei_env)
            if value < 1:
                return _DEFAULT_STATS_LONG_EXPORT_INTERVAL
            return value
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


## Customer SDK stats

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
        return (RetryCode.CLIENT_TIMEOUT, _exception_categories.TIMEOUT_EXCEPTION.value)

    if hasattr(error, 'message'):
        error_message = getattr(error, 'message', None) if hasattr(error, 'message') else None
        if error_message is not None and ('timeout' in error_message.lower() or 'timed out' in error_message.lower()):
            return (RetryCode.CLIENT_TIMEOUT, _exception_categories.TIMEOUT_EXCEPTION.value)

    if isinstance(error, network_exception_types):
        return (RetryCode.CLIENT_EXCEPTION, _exception_categories.NETWORK_EXCEPTION.value)

    return (RetryCode.CLIENT_EXCEPTION, _exception_categories.CLIENT_EXCEPTION.value)

def _track_successful_items(envelopes: List[TelemetryItem]):
    customer_sdkstats_metrics = get_customer_sdkstats_metrics()
    if not customer_sdkstats_metrics:
        return

    for envelope in envelopes:
        telemetry_type = _get_telemetry_type(envelope)
        customer_sdkstats_metrics.count_successful_items(
            1,
            telemetry_type
        )

def _track_dropped_items(
        envelopes: List[TelemetryItem],
        drop_code: DropCodeType,
        error_message: Optional[str] = None
    ):
    customer_sdkstats_metrics = get_customer_sdkstats_metrics()
    if not customer_sdkstats_metrics:
        return

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

def _track_retry_items(envelopes: List[TelemetryItem], error) -> None:
    customer_sdkstats_metrics = get_customer_sdkstats_metrics()
    if not customer_sdkstats_metrics:
        return
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

def _track_dropped_items_from_storage(result_from_storage_put, envelopes):
    customer_sdkstats_metrics = get_customer_sdkstats_metrics()
    if not customer_sdkstats_metrics:
        return
    # Use delayed import to avoid circular import
    from azure.monitor.opentelemetry.exporter._storage import StorageExportResult

    if result_from_storage_put == StorageExportResult.CLIENT_STORAGE_DISABLED:
        # Track items that would have been retried but are dropped since client has local storage disabled
        _track_dropped_items(envelopes, DropCode.CLIENT_STORAGE_DISABLED)
    elif result_from_storage_put == StorageExportResult.CLIENT_READONLY:
        # If filesystem is readonly, track dropped items in customer sdkstats
        _track_dropped_items(envelopes, DropCode.CLIENT_READONLY)
    elif result_from_storage_put == StorageExportResult.CLIENT_PERSISTENCE_CAPACITY_REACHED:
        # If data has to be dropped due to persistent storage being full, track dropped items
        _track_dropped_items(envelopes, DropCode.CLIENT_PERSISTENCE_CAPACITY)
    elif get_local_storage_setup_state_exception() != "":
        # For exceptions caught in _check_and_set_folder_permissions during storage setup
        _track_dropped_items(envelopes, DropCode.CLIENT_EXCEPTION, _exception_categories.STORAGE_EXCEPTION.value) # pylint: disable=line-too-long
    elif isinstance(result_from_storage_put, str):
        # For any exceptions occurred in put method of either LocalFileStorage or LocalFileBlob, track dropped item with reason # pylint: disable=line-too-long
        _track_dropped_items(envelopes, DropCode.CLIENT_EXCEPTION, _exception_categories.STORAGE_EXCEPTION.value) # pylint: disable=line-too-long
    else:
        # LocalFileBlob.put returns StorageExportResult.LOCAL_FILE_BLOB_SUCCESS here. Don't need to track anything in this case. # pylint: disable=line-too-long
        pass

# seconds
def _get_customer_sdkstats_export_interval() -> int:
    customer_sdkstats_ei_env = os.environ.get(_APPLICATIONINSIGHTS_SDKSTATS_EXPORT_INTERVAL)
    if customer_sdkstats_ei_env:
        try:
            return int(customer_sdkstats_ei_env)
        except ValueError:
            return _DEFAULT_STATS_SHORT_EXPORT_INTERVAL
    return _DEFAULT_STATS_SHORT_EXPORT_INTERVAL


## OneSettings Config

# pylint: disable=too-many-return-statements
def _get_connection_string_for_region_from_config(target_region: str, settings: Dict[str, str]) -> Optional[str]:
    """Get the appropriate stats connection string for the given region.

    This function determines which data boundary the given region
    belongs to and returns the corresponding stats connection string. The logic:

    1. Checks if the given region is in any of the supported data boundary regions
    2. Returns the matching stats connection string for that boundary
    3. Falls back to DEFAULT if region is not found in any boundary

    :param target_region: The Azure region name (e.g., "westeurope", "eastus")
    :type target_region: str
    :param settings: Dictionary containing OneSettings configuration values
    :type settings: Dict[str, str]
    :return: The stats connection string for the region's data boundary,
            or None if no configuration is available
    :rtype: Optional[str]
    """
    logger = logging.getLogger(__name__)

    default_connection_string = settings.get(_ONE_SETTINGS_DEFAULT_STATS_CONNECTION_STRING_KEY)

    try:
        # Get supported data boundaries
        supported_boundaries = settings.get(_ONE_SETTINGS_SUPPORTED_DATA_BOUNDARIES_KEY)
        if not supported_boundaries:
            logger.warning("Supported data boundaries key not found in configuration")
            return default_connection_string

        # Parse if it's a JSON string
        if isinstance(supported_boundaries, str):
            supported_boundaries = json.loads(supported_boundaries)

        # supported_boundaries should be a list
        if not isinstance(supported_boundaries, Iterable):
            logger.warning("Supported data boundaries is not iterable")
            return default_connection_string

        # Check each supported boundary to find the region
        for boundary in supported_boundaries:
            # Skip DEFAULT
            if boundary.upper() == "DEFAULT":
                continue
            boundary_regions_key = f"{boundary}_REGIONS"
            boundary_regions = settings.get(boundary_regions_key)

            if boundary_regions:
                # Parse if it's a JSON string
                if isinstance(boundary_regions, str):
                    boundary_regions = json.loads(boundary_regions)

                # Check if the region is in this boundary's regions
                if isinstance(boundary_regions, list) and \
                    any(target_region.lower() == r.lower() for r in boundary_regions):
                    # Found the boundary, get the corresponding connection string
                    connection_string_key = f"{boundary}_STATS_CONNECTION_STRING"
                    connection_string = settings.get(connection_string_key)

                    if connection_string:
                        return connection_string

                    logger.warning("Connection string key '%s' not found in configuration",
                                    connection_string_key)

        # Region not found in any specific boundary, try DEFAULT
        if not default_connection_string:
            logger.warning("Default stats connection string not found in configuration")
            return None
        return default_connection_string
    except (ValueError, TypeError, KeyError) as ex:
        logger.warning("Error parsing configuration for region '%s': %s", target_region, str(ex))
        return None
    except Exception as ex:  # pylint: disable=broad-exception-caught
        logger.warning("Unexpected error getting stats connection string for region '%s': %s",
                     target_region, str(ex))
        return None
