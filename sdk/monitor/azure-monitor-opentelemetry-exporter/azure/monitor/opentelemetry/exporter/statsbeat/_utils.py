# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import os
import logging
import json
from collections.abc import Iterable
from typing import Optional, Dict

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
    _ONE_SETTINGS_DEFAULT_STATS_CONNECTION_STRING_KEY,
    _ONE_SETTINGS_SUPPORTED_DATA_BOUNDARIES_KEY,
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
