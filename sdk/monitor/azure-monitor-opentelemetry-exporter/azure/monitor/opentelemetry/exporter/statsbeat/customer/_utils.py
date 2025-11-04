# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import os
from typing import Optional, List, Tuple, Union
# mypy: disable-error-code="import-untyped"
from requests import ReadTimeout, Timeout
from azure.core.exceptions import ServiceRequestTimeoutError
from azure.monitor.opentelemetry.exporter._constants import (
    _REQUEST,
    RetryCode,
    RetryCodeType,
    DropCodeType,
    DropCode,
    _UNKNOWN,
    _DEPENDENCY,
    _APPLICATIONINSIGHTS_SDKSTATS_EXPORT_INTERVAL,
    _DEFAULT_STATS_SHORT_EXPORT_INTERVAL,
    _APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW,
    _exception_categories,
)
from azure.monitor.opentelemetry.exporter._utils import _get_telemetry_type
from azure.monitor.opentelemetry.exporter._generated.models import TelemetryItem
from ._state import (
    get_local_storage_setup_state_exception,
    get_customer_stats_manager,
)


def get_customer_sdkstats_export_interval() -> int:
    """Get the export interval for customer SDK stats from environment or default.
    
    :return: Export interval in seconds
    :rtype: int
    """
    customer_sdkstats_ei_env = os.environ.get(_APPLICATIONINSIGHTS_SDKSTATS_EXPORT_INTERVAL)
    if customer_sdkstats_ei_env:
        try:
            return int(customer_sdkstats_ei_env)
        except ValueError:
            return _DEFAULT_STATS_SHORT_EXPORT_INTERVAL
    return _DEFAULT_STATS_SHORT_EXPORT_INTERVAL


def is_customer_sdkstats_enabled() -> bool:
    """Check if customer SDK stats collection is enabled via environment variable.
    
    :return: True if enabled, False otherwise
    :rtype: bool
    """
    return os.environ.get(_APPLICATIONINSIGHTS_SDKSTATS_ENABLED_PREVIEW, "").lower() == "true"


def categorize_status_code(status_code: int) -> str:
    """Categorize HTTP status codes into human-readable messages.
    
    :param status_code: HTTP status code
    :type status_code: int
    :return: Human-readable status message
    :rtype: str
    """
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


def _determine_client_retry_code(error) -> Tuple[RetryCodeType, Optional[str]]:  # pylint: disable=docstring-missing-type
    """Determine the retry code and message for a given error.
    
    :param error: The error that occurred
    :return: Tuple of retry code and optional message
    :rtype: Tuple[RetryCodeType, Optional[str]]
    """
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


def _get_telemetry_success_flag(envelope: TelemetryItem) -> Union[bool, None]:
    """Extract the success flag from a telemetry envelope.
    
    :param envelope: The telemetry envelope
    :type envelope: TelemetryItem
    :return: Success flag if available, None otherwise
    :rtype: Union[bool, None]
    """
    if not hasattr(envelope, "data") or envelope.data is None:
        return None

    if not hasattr(envelope.data, "base_type") or envelope.data.base_type is None:
        return None

    if not hasattr(envelope.data, "base_data") or envelope.data.base_data is None:
        return None

    base_type = envelope.data.base_type

    if base_type in ("RequestData", "RemoteDependencyData") and hasattr(envelope.data.base_data, "success"):
        success_value = getattr(envelope.data.base_data, "success", None)
        if isinstance(success_value, bool):
            return success_value
    return None


def track_successful_items(envelopes: List[TelemetryItem]):
    """Track successful telemetry items in customer SDK stats.
    
    :param envelopes: List of telemetry envelopes that were successfully sent
    :type envelopes: List[TelemetryItem]
    """
    customer_stats = get_customer_stats_manager()

    for envelope in envelopes:
        telemetry_type = _get_telemetry_type(envelope)
        customer_stats.count_successful_items(
            1,
            telemetry_type
        )


def track_dropped_items(
        envelopes: List[TelemetryItem],
        drop_code: DropCodeType,
        error_message: Optional[str] = None
    ):
    customer_stats = get_customer_stats_manager()

    if error_message is None:
        for envelope in envelopes:
            telemetry_type = _get_telemetry_type(envelope)
            customer_stats.count_dropped_items(
                1,
                telemetry_type,
                drop_code,
                _get_telemetry_success_flag(envelope) if telemetry_type in (_REQUEST, _DEPENDENCY) else True
            )
    else:
        for envelope in envelopes:
            telemetry_type = _get_telemetry_type(envelope)
            customer_stats.count_dropped_items(
                1,
                telemetry_type,
                drop_code,
                _get_telemetry_success_flag(envelope) if telemetry_type in (_REQUEST, _DEPENDENCY) else True,
                exception_message=error_message
            )


def track_retry_items(envelopes: List[TelemetryItem], error) -> None:
    customer_stats = get_customer_stats_manager()

    retry_code, message = _determine_client_retry_code(error)
    for envelope in envelopes:
        telemetry_type = _get_telemetry_type(envelope)
        if isinstance(retry_code, int):
            # For status codes, include the message if available
            if message:
                customer_stats.count_retry_items(
                    1,
                    telemetry_type,
                    retry_code,
                    str(message)
                )
            else:
                customer_stats.count_retry_items(
                    1,
                    telemetry_type,
                    retry_code
                )
        else:
            customer_stats.count_retry_items(
                1,
                telemetry_type,
                retry_code,
                str(message)
            )


def track_dropped_items_from_storage(result_from_storage_put, envelopes):
    # Use delayed import to avoid circular import
    from azure.monitor.opentelemetry.exporter._storage import StorageExportResult

    if result_from_storage_put == StorageExportResult.CLIENT_STORAGE_DISABLED:
        # Track items that would have been retried but are dropped since client has local storage disabled
        track_dropped_items(envelopes, DropCode.CLIENT_STORAGE_DISABLED)
    elif result_from_storage_put == StorageExportResult.CLIENT_READONLY:
        # If filesystem is readonly, track dropped items in customer sdkstats
        track_dropped_items(envelopes, DropCode.CLIENT_READONLY)
    elif result_from_storage_put == StorageExportResult.CLIENT_PERSISTENCE_CAPACITY_REACHED:
        # If data has to be dropped due to persistent storage being full, track dropped items
        track_dropped_items(envelopes, DropCode.CLIENT_PERSISTENCE_CAPACITY)
    elif get_local_storage_setup_state_exception() != "":
        # For exceptions caught in _check_and_set_folder_permissions during storage setup
        track_dropped_items(envelopes, DropCode.CLIENT_EXCEPTION, _exception_categories.STORAGE_EXCEPTION.value) # pylint: disable=line-too-long
    elif isinstance(result_from_storage_put, str):
        # For any exceptions occurred in put method of either LocalFileStorage or LocalFileBlob, track dropped item with reason # pylint: disable=line-too-long
        track_dropped_items(envelopes, DropCode.CLIENT_EXCEPTION, _exception_categories.STORAGE_EXCEPTION.value) # pylint: disable=line-too-long
    else:
        # LocalFileBlob.put returns StorageExportResult.LOCAL_FILE_BLOB_SUCCESS here. Don't need to track anything in this case. # pylint: disable=line-too-long
        pass
