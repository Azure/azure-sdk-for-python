# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import os

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
        400: "bad_request",
        401: "unauthorized",
        402: "daily quota exceeded",
        403: "forbidden",
        404: "not_found",
        408: "request_timeout",
        413: "payload_too_large",
        429: "too_many_requests",
        500: "internal_server_error",
        502: "bad_gateway",
        503: "service_unavailable",
        504: "gateway_timeout",
    }
    if status_code in status_map:
        return status_map[status_code]
    if 400 <= status_code < 500:
        return "client_error_4xx"
    if 500 <= status_code < 600:
        return "server_error_5xx"
    return f"status_{status_code}"
