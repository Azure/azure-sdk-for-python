# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import os
import threading
from typing import Dict, Union

from azure.monitor.opentelemetry.exporter._constants import _APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL

_REQUESTS_MAP: Dict[str, Union[int, Dict[int, int]]] = {}
_REQUESTS_MAP_LOCK = threading.Lock()

_STATSBEAT_STATE = {
    "INITIAL_FAILURE_COUNT": 0,
    "INITIAL_SUCCESS": False,
    "SHUTDOWN": False,
    "CUSTOM_EVENTS_FEATURE_SET": False,
    "LIVE_METRICS_FEATURE_SET": False,
}
_STATSBEAT_STATE_LOCK = threading.Lock()
_STATSBEAT_FAILURE_COUNT_THRESHOLD = 3


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
