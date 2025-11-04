# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import os
import threading
from typing import TYPE_CHECKING, Dict, Union

from azure.monitor.opentelemetry.exporter._constants import (
    _APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL
)

if TYPE_CHECKING:
    from azure.monitor.opentelemetry.exporter.statsbeat._manager import StatsbeatManager

_REQUESTS_MAP: Dict[str, Union[int, Dict[int, int]]] = {}
_REQUESTS_MAP_LOCK = threading.Lock()

_STATSBEAT_STATE = {
    "INITIAL_FAILURE_COUNT": 0,
    "INITIAL_SUCCESS": False,
    "SHUTDOWN": False,
    "CUSTOM_EVENTS_FEATURE_SET": False,
    "LIVE_METRICS_FEATURE_SET": False,
    "CUSTOMER_SDKSTATS_FEATURE_SET": False,
}
_STATSBEAT_STATE_LOCK = threading.Lock()
_STATSBEAT_FAILURE_COUNT_THRESHOLD = 3

# Global singleton instance for easy access throughout the codebase
_statsbeat_manager = None

def get_statsbeat_manager() -> "StatsbeatManager":
    """Get the global Statsbeat Manager singleton instance.

    This provides a single access point to the manager and handles lazy initialization.

    :return: The singleton Statsbeat Manager instance
    :rtype: StatsbeatManager
    """
    global _statsbeat_manager  # pylint: disable=global-statement
    if _statsbeat_manager is None:
        from azure.monitor.opentelemetry.exporter.statsbeat._manager import StatsbeatManager
        _statsbeat_manager = StatsbeatManager()
    return _statsbeat_manager

def is_statsbeat_enabled():
    disabled = os.environ.get(_APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL)
    return disabled is None or disabled.lower() != "true"


def increment_statsbeat_initial_failure_count():  # pylint: disable=name-too-long
    with _STATSBEAT_STATE_LOCK:
        _STATSBEAT_STATE["INITIAL_FAILURE_COUNT"] += 1


def increment_and_check_statsbeat_failure_count():  # pylint: disable=name-too-long
    increment_statsbeat_initial_failure_count()
    return get_statsbeat_initial_failure_count() >= _STATSBEAT_FAILURE_COUNT_THRESHOLD


def get_statsbeat_initial_failure_count():
    return _STATSBEAT_STATE["INITIAL_FAILURE_COUNT"]


def set_statsbeat_initial_success(success):
    with _STATSBEAT_STATE_LOCK:
        _STATSBEAT_STATE["INITIAL_SUCCESS"] = success


def get_statsbeat_initial_success():
    return _STATSBEAT_STATE["INITIAL_SUCCESS"]


def get_statsbeat_shutdown():
    return _STATSBEAT_STATE["SHUTDOWN"]


def get_statsbeat_custom_events_feature_set():
    return _STATSBEAT_STATE["CUSTOM_EVENTS_FEATURE_SET"]


def set_statsbeat_custom_events_feature_set():
    with _STATSBEAT_STATE_LOCK:
        _STATSBEAT_STATE["CUSTOM_EVENTS_FEATURE_SET"] = True


def get_statsbeat_live_metrics_feature_set():
    return _STATSBEAT_STATE["LIVE_METRICS_FEATURE_SET"]


def set_statsbeat_live_metrics_feature_set():
    with _STATSBEAT_STATE_LOCK:
        _STATSBEAT_STATE["LIVE_METRICS_FEATURE_SET"] = True


def set_statsbeat_shutdown(shutdown: bool):
    with _STATSBEAT_STATE_LOCK:
        _STATSBEAT_STATE["SHUTDOWN"] = shutdown

def get_statsbeat_customer_sdkstats_feature_set(): # pylint: disable=name-too-long
    return _STATSBEAT_STATE["CUSTOMER_SDKSTATS_FEATURE_SET"]

def set_statsbeat_customer_sdkstats_feature_set(): # pylint: disable=name-too-long
    with _STATSBEAT_STATE_LOCK:
        _STATSBEAT_STATE["CUSTOMER_SDKSTATS_FEATURE_SET"] = True
